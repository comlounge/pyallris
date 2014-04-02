
# Makefile zur automatischen Erzeugung der OSM-Daten-Derivate
# this is copied from offeneskoeln but will not really work anymore and is kept just
# for reference. Please use prepare.sh, do_city.sh or all.sh to do all of it

# Benötigt python-osm!
# pip install git+git://github.com/werner2101/python-osm.git
# das wiederum benötigt NumPy und Matplotlib.nxutils
# pip install numpy
# pip install matplotlib

import: aachen-streets.osm
	python osm-import.py aachen-streets.osm

aachen-streets.osm: osmfilter aachen.osm
	./osmfilter aachen.osm \
	--keep="highway=primary =secondary =tertiary =residential =unclassified =road =living-street =pedestrian" \
	--drop-author --drop-version > aachen-streets.osm

aachen.osm: aachen.poly koeln-regbez-latest.osm osmosis
	bin/osmosis --read-xml file="koeln-regbez-latest.osm" --bounding-polygon file="aachen.poly" --write-xml file="aachen.osm"

koeln-regbez-latest.osm:
	wget -N http://download.geofabrik.de/europe/germany/nordrhein-westfalen/koeln-regbez-latest.osm.bz2
	bunzip2 koeln-regbez-latest.osm.bz2

osmfilter:
	wget -O - http://m.m.i24.cc/osmfilter.c |cc -x c - -O3 -o osmfilter

osmosis:
	wget -N http://bretth.dev.openstreetmap.org/osmosis-build/osmosis-latest.tgz
	tar xzf osmosis-latest.tgz
	chmod u+x bin/osmosis
	cp bin/osmosis .
	rm osmosis-latest.tgz
	rm -r script
	rm readme.txt
	rm copying.txt
	rm changes.txt

aachen.poly:
	python -m osm.multipolygon -r 62564 -m aachen.poly

clean:
	rm aachen.poly
	rm koeln-regbez-latest.osm
	rm aachen.osm
	rm osmfilter
	rm *-streets.osm
	rm *.poly
	rm osmosis
	rm -r bin
	rm -r lib
	rm -r config
