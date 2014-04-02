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

in config.py you can define the mongodb host etc.

Importing city data
===================

./do_city.sh city relation regionalschlüssel

Data as above.
