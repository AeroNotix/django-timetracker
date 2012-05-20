Dependencies
============

Python specific
---------------
* Python v2.7

* Django v1.4

* simplejson (included with Django)

* MySQLdb Python MySQL bindings

Misc
----
* Apache+mod_wsgi

* Any SMTP Server

* MySQL Server

Detailed Instructions
---------------------

Below will outline all the required steps to prepare your system.

Install Python
--------------

If you're using Windows, this will simply be a case of heading to the main 
Python website and downloading the Python 2.7 binary and installing. It is
extremely vital that this particular version of Python is used otherwise,
the later (and some earlier) versions are code-incompatible. Either through
syntax differences or some modules are not available.

If you're on Linux, any debian-based system will have the python2 package in
it's repos. Most distros will have the package required.

Install Django
--------------

If you're using Windows, head to the Django website and download and unzip
the 1.4 source then follow the below::

    cd django1.4
    python setup.py install

Other than taking an inordinate amount of time. This will then install Django
1.4 onto your system.

If you're on Linux, please refer to the available packages in your repos to
find the exact name of the package. However, the steps will include::

    for Arch:
    sudo pacman -S python-django
    Debian-based:
    sudo apt-get install python-django

simplejson
----------

This should come with django, but, for whatever reason you wish to use an
externally sourced version, please go to Google and download the latest
via any links found on there.

MySQLdb Python bindings
-----------------------

This part is actually a little tricky for Windows. Therefore we have decided
to link to a pre-compiled binary for the MySQLdb Python bindings. It can be
found `here. <http://www.lfd.uci.edu/~gohlke/pythonlibs/>`_

If you're on Linux, please refer to your distro's repos for what the package
name is, however, some hints are below::

    on Arch:
    sudo pacman -S mysql-python
    Debian-based:
    sudo apt-get install mysql-python

This covers the installation portion of the code-dependencies.

Next is preparing your system for the software which needs to be installed.

Apache
------

Windows:

Head to the Apache website and download the Apache 2.2 binary and install.

Linux::

    On Arch:
    sudo pacman -S apache
    Debian based:
    sudo apt-get install apache

mod_wsgi
--------

Download the latest mod_wsgi.so file from the mod_wsgi downloads page found,
`on here. <http://code.google.com/p/modwsgi/wiki/DownloadTheSoftware>`_

Then, depending on the system you are using, put it into your Apache modules
directory.

Windows::

    C:\Program Files\Apache Software Foundation\Apache2.2\bin\

Linux::

    /etc/httpd/modules

Then for both, modify your httpd.conf file so that it enabled the mod_wsgi.so
module::

    LoadModule wsgi_module <path_to_modules_dir>/mod_wsgi.so
