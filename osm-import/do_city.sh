#!/bin/sh

city=$1
relation=$2
rs=$3
# aachen = 62564
# alsdorf = 157993
# wuerselen = 157994
echo "working on $city"

echo
echo "generating polygons for $city"
python -m osm.multipolygon -r $relation -m $city.poly

echo
echo "generating $city.osm"
bin/osmosis --read-xml file="koeln-regbez-latest.osm" --bounding-polygon file="$city.poly" --write-xml file="$city.osm"

echo
echo "generating $city-streets.osm"
./osmfilter $city.osm \
    --keep="highway=primary =secondary =tertiary =residential =unclassified =road =living-street =pedestrian" \
    --drop-author --drop-version > $city-streets.osm

echo
echo "importing streets for $city"
python osm-import.py $city-streets.osm $city $rs


