#!/bin/bash

python_packge_name="osm2gmns"

if [ -d "$python_packge_name" ]; then
    rm -rf "$python_packge_name"
fi

mkdir "$python_packge_name"
cp -R python/* "$python_packge_name"/
cp -R build/install/* "$python_packge_name"/

echo "$python_packge_name python package created."