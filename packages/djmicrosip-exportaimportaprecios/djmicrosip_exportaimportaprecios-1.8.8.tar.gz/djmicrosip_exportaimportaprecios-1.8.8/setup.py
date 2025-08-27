import os, time, compileall, sys
from setuptools import setup, find_packages

if "sdist" in sys.argv:
    path = os.path.abspath(os.path.dirname(__file__))+"\\djmicrosip_exportaimportaprecios\\"
    compileall.compile_dir(path, force=True)

# README = open(os.path.join(os.path.dirname(__file__), 'README.txt')).read()
with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()
REQUIREMENTS = [i.strip() for i in open("requirements.txt").readlines()]
# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(

    username = '__token__',
    password = 'pypi-AgEIcHlwaS5vcmcCJDMzNzQ3N2Y4LWJjOWYtNDNlOS1hOGM2LWMwODNhNmYxYjc5MgACKlszLCI0YzkyNTJkMC05YWFmLTQ5ZTYtYmU5ZS01YWYxOWZlZGI5ZDUiXQAABiCXuYtQg-eQ-vWH2gycMSobsCgYaxWgr_CUsJBbWdUQtQ',
    name = 'djmicrosip_exportaimportaprecios',
    version = '1.8.8',
    packages = find_packages(),
    include_package_data = True,
    license = 'BSD License', # example license
    description = 'djmicrosip_exportaimportaprecios',
    long_description = 'README',
    url = '',
    author = 'Servicios de Ingenieria Computacional',
    author_email = 'desarrollo@siccomputacion.com',
    classifiers = [
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License', # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=REQUIREMENTS,
)
