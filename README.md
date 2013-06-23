# pyallris - an ALLRIS-Scraper in python

This scraper is work in progress and builds on the information found in this
wiki document: [ScrapingAllrisHowto](https://code.google.com/p/allris-scraper/wiki/ScrapingAllrisHowto)

It's based on the XML output which needs to be enabled for it to work.
Unfortunately not everything is accessible via the XML output.

## Installation / Requirements

The best way to make it work is to install [virtualenv](https://pypi.python.org/pypi/virtualenv) and create a virtual environment for the scraper to run in:

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

### Ubuntu 12.04 installation
 
Install python 2.7:

    sudo apt-get install python2.7-dev

Install the mongo dbms:

    sudo apt-get install mongodb

Install pip for the virtualenv:

    sudo apt-get install python-pip
    sudo pip-2.7 install virtualenv

Use VirtualEnvironment:
Navigate to a folder where the project root folder will be and run:

    virtualenv-2.7 .
    source bin/activate

Clone the git project as a subdirectory of the virtualenv folder:

    git clone https://github.com/mrtopf/pyallris.git

Initialize the bootstrap git submodule:

    git submodule init
    git submodule update

Now you can run the scrapers with:
   
    python sitzungen.py 
    python meetings.py 
    python persons.py 

To start the server run:

    python setup.py develop

## Notice
Please note that the URLs in use are right now hard coded for the ALLRIS in **Aachen**. This might
change soon though.