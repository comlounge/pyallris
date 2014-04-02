#!/bin/sh

echo
echo "retrieving and compiling osmfilter"
wget -O - http://m.m.i24.cc/osmfilter.c |cc -x c - -O3 -o osmfilter

echo
echo "retrieving and compiling osmfilter"
wget -O - http://m.m.i24.cc/osmfilter.c |cc -x c - -O3 -o osmfilter

echo
echo "compiling osmosis"
wget -N http://bretth.dev.openstreetmap.org/osmosis-build/osmosis-latest.tgz
tar xzf osmosis-latest.tgz
chmod u+x bin/osmosis
cp bin/osmosis .
rm osmosis-latest.tgz
rm -r script
rm readme.txt
rm copying.txt
rm changes.txt

echo
echo "retrieving osm for koeln regbz"
wget -N http://download.geofabrik.de/europe/germany/nordrhein-westfalen/koeln-regbez-latest.osm.bz2
bunzip2 koeln-regbez-latest.osm.bz2

