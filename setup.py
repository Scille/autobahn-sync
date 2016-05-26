# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


with open('README.rst', 'rb') as readme_file:
    readme = readme_file.read().decode('utf8')


REQUIRES = (
    'crochet>=1.4.0',
    'autobahn>=0.12.0'
)


setup(
    name='autobahn-sync',
    version='0.3.2',
    description='Bring autobahn to your synchronous apps !',
    long_description=readme,
    author='Emmanuel Leblond',
    author_email='emmanuel.leblond@gmail.com',
    url='https://github.com/Scille/autobahn_sync',
    packages=find_packages(exclude=("test*", )),
    package_dir={'autobahn_sync': 'autobahn_sync'},
    include_package_data=True,
    install_requires=REQUIRES,
    license='MIT',
    zip_safe=False,
    keywords='autobahn autobahn.ws wamp twisted crochet flask',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='tests',
)
