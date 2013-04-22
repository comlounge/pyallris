# pyallris - an ALLRIS-Scraper in python

This scraper is work in progress and builds on the information found in this
wiki document: https://code.google.com/p/allris-scraper/wiki/ScrapingAllrisHowto

It's based on the XML output which needs to be enabled for it to work.


## Installation / Requirements

The best way to make it work is to install virtualenv (https://pypi.python.org/pypi/virtualenv) and create a virtual environment for the scraper to run in:

    mkdir scraper
    cd scraper
    virtualenv .
    source bin/activate

Then clone the repo:

    git clone https://github.com/mrtopf/pyallris.git

and develop it:

    cd pyallris
    python setup.py develop

This will install all requirements as well.

After that you can look into `sitzungen.py` to check how it's supposed to work. There are also
some experiments in the `experiments/` folder.

Please note that the URLs in use are right now hard coded for the ALLRIS in Aachen. This might
change soon though.






