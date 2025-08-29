import hashlib
import json
import re
import zoneinfo
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

import requests
import yaml
from bs4 import BeautifulSoup
from pyjsparser import PyJsParser

from map_utils_xethhung12.GridSystem import LatLon

hktz = zoneinfo.ZoneInfo("Asia/Hong_Kong")
time_format = '%Y-%m-%dT%H:%M:%S%z'
def to_time_str(d):
    return d.astimezone(hktz).strftime(time_format)

def from_str_to_time(date_str):
    return datetime.strptime(date_str.replace(" +", "+"), time_format).astimezone(hktz)

class SimpleDataClass:
    def dict(self) -> dict:
        return asdict(self, dict_factory=custom_asdict_factory)

def custom_asdict_factory(data):
    def convert_value(obj):
        if isinstance(obj, datetime):
            # return obj.astimezone(hktz).strftime(time_format)
            return to_time_str(obj)
        elif isinstance(obj, Enum):
            return obj.name
        return obj

    return dict((k, convert_value(v)) for k, v in data)

@dataclass
class GLocation(SimpleDataClass):
    id: str
    latlon: LatLon
    name: str
    description: str

@dataclass
class SavedPlaces(SimpleDataClass):
    url: str
    name: str
    description: str
    locations: [GLocation]

@dataclass
class KV(SimpleDataClass):
    key: str
    value: str

class Trip:
    def __init__(self, saved_places: SavedPlaces):
        self.saved_places = saved_places
        self.kvs=self._extract_meta()

    def _extract_meta(self)->[KV]:
        kvs: [KV] = []
        pattern_of_meta = re.compile("^# ([\w\d-]+)=(.*)$")
        for meta_str in [para.strip() for para in self.saved_places.description.split("------") if para.strip().startswith("##meta")]:
            for meta_line in  meta_str.split("\n")[1:]:
                matcher = pattern_of_meta.match(meta_line)
                key=matcher[1]
                value=matcher[2]
                kvs.append(KV(key, value))
        return kvs

    def start_day(self)->None|datetime:
        start_day_found = list(filter(lambda x: x.key=="start_day",self.kvs))
        return None if len(start_day_found)==0 else datetime.strptime(start_day_found[0].value, "%Y-%m-%d")

    def end_day(self)->None|datetime:
        end_day_found = list(filter(lambda x: x.key=="end_day",self.kvs))
        return None if len(end_day_found)==0 else datetime.strptime(end_day_found[0].value, "%Y-%m-%d")

    def flights(self)->[str]:
        return [f.value for f in list(filter(lambda x: x.key=="flight",self.kvs))]


    def output_yaml(self)->str:
        d={
            "start_day": self.start_day(),
            "end_day": self.end_day(),
            "trip_name": self.saved_places.name,
            "locations": [ f"{location.name} [{str(location.latlon.lat)},{str(location.latlon.lon)}] - {get_url_from_latlon_2(location.latlon.lat, location.latlon.lon)}" for location in self.saved_places.locations],
            "flights": self.flights()
        }
        return yaml.dump(d, allow_unicode=True)



class Geocode:
    def __init__(self, key):
        self.key = key

    def geocode_api_by_address(self, address: str, key: str)->dict:
        LocationParams = {'address': address, key: key}
        LocationURL = 'http://maps.googleapis.com/maps/api/geocode/json'
        r = requests.get(LocationURL, params=LocationParams)
        responseJson = json.loads(r.text)
        self.res = responseJson
        return self.res

    def get_size_of_result(self):
        return len(self.res)

    def get_lat_lon_obj(self, i=0)->LatLon:
        lat = float(self.res.get('results')[i]['geometry']['location']['lat'])
        lng = float(self.res.get('results')[i]['geometry']['location']['lng'])
        return LatLon(lat, lng)

    def get_address(self, i=0) -> str:
        return self.res.get('results')[i]['formatted_address']


def get_url_from_latlon_object(latlon: LatLon) -> str:
    return get_url_from_latlon(latlon.lat, latlon.lon)

def get_url_from_latlon(lat: float, lon: float) -> str:
    return f"https://www.google.com/maps/@{lat},{lon}"

def get_url_from_latlon_2(lat: float, lon: float) -> str:
    return f"https://www.google.com/maps?z=12&t=m&q=loc:{lat}+{lon}"


def get_lat_lon(url: str) -> LatLon | None:
    ps = [
        "^https://.*google.*/maps/place/[^/]+/@([\d.]+),([\d.]+),\d+z/.*$",
        "^https://.*google.*/maps/@([\d.]+),([\d.]+).*$"
    ]

    for s in ps:
        rs = re.compile(s).match(url)
        if rs is not None:
            return LatLon(float(rs[1]), float(rs[2]))
    return None


def get_real_url_of_google_map(url: str):
    response = requests.get(url, allow_redirects=False)
    if response.status_code in [301, 302, 307, 308]:
        return response.headers['Location']
    else:
        return url


def extrac_saved_places(url: str)->SavedPlaces:
    import requests
    x: requests.Response = requests.get(url)
    b64 = BeautifulSoup(x.text, "html.parser")
    rs = b64.select("script")
    text = [r.text for r in rs if "window.APP_OPTIONS=" in r.text][0]
    # text = text[1:][:-4]

    # JSParser(text)
    glocations: [GLocation] = []
    parsed=PyJsParser().parse(text)
    parsed_data=PyJsParser().parse(parsed["body"][0]["expression"]["callee"]["body"]["body"][2]["expression"]["right"]["elements"][3]["elements"][16]["value"][5:])["body"][0]["expression"]["elements"][0]["elements"]

    locations =parsed_data[8]["elements"]
    for location in locations:
        location = location["elements"]
        name = location[2]["value"]
        description = location[3]["value"]
        lat = float(location[1]["elements"][5]["elements"][2]["value"])
        lon = float(location[1]["elements"][5]["elements"][3]["value"])
        id = hashlib.sha256(f"{lat:.5f} {lon:.5f}".encode("utf-8")).hexdigest()
        glocations.append(GLocation(id, latlon=LatLon(lat, lon), name=name, description=description))

    map_name=parsed_data[4]["value"]
    map_description=parsed_data[5]["value"]
    return SavedPlaces(url, map_name, map_description, glocations)

