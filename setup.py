from setuptools import setup, find_packages

version = '0.1'

setup(name='pyallris',
      version=version,
      description="a ALLRIS importer written in python",
      long_description="""
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='COM.lounge',
      author_email='info@comlounge.net',
      url='',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        "pytz",
        "lxml",
        "requests",
        "pymongo",
        "cssselect",
        "mongogogo",
        "starflyer",
      ],
      entry_points="""
      [paste.app_factory]
      main = pyallris.web.app:app
      """,
      )
