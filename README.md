Installation

First and foremost you need to have a CKAN instance setup by following the [CKAN Install Guide](http://docs.ckan.org/en/latest/maintaining/installing/index.html).

Then follow these instructions to download, install and serve the TeSS CKAN extension in development mode:

    cd /usr/lib/ckan/default

    sudo pip install -e git+https://github.com/ElixirUK/ckanext-tess#egg=ckanext-tess

    cd ckanext-tess

    python setup.py develop

Open  /etc/ckan/default/development.ini in your text editor

     $ cd ../

     $ sudo paster serve /etc/ckan/default/development.ini
