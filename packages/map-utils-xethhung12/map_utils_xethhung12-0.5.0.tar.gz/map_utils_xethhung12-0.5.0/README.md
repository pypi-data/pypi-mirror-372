# map-utils-xethhung12

A simple library for google map or map related operation.
* Find denso map code from google map link (make use exists [website](https://saibara.sakura.ne.jp/map/convgeo.cgi)
* Get real path from google map from `url shortening`

# build
ensure `python` command works well.
If the command not work, try use `alias python="python3"` or install `python3-is-python` package.

run build script:
```shell
./py-build.sh
```

# upload 
Write token to file `token.txt`
Set `token` variable with command `token=$(cat token.txt)`
```shell
twine upload dist/* -u __token__ -p $token
```

# update package version
```shell
./patch.sh
```