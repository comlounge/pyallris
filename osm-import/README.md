Introduction
============

This package will retrieve a list of cities from OSM and store them inside a mongodb collection called "streets".
It will also reference the location objects per street which are stored in the locations collection.

For each import we need the following data:

- the city name under which we store the streets
- the OSM relation under which to find the city borders. You can find those at http://www.openstreetmap.org/. Just search for a city and it should show the relation id
- the regionalschlüssel. You can simply search for that via google e.g. "aachen regionalschlüssel". 

Preparing the package
=====================

call ./prepare.sh to download all date and compile tools

You also need to have postgresql installed but I forgot the details. One tool uses it though for storing the data
and tokyo-cabinet and protobuf

in config.py you can define the mongodb host etc.
(copy if from config.py.in)

Python installs:

pip install numpy==1.7.1
pip install matplotlib==1.1.0
pip install git+git://github.com/werner2101/python-osm.git
pip install imposm


Importing city data
===================

./do_city.sh city relation regionalschlüssel

Data as above.

After that run python the script in scripts/ to merge locations and streets.
