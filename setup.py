# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in custom_payroll/__init__.py
from custom_payroll import __version__ as version

setup(
	name='custom_payroll',
	version=version,
	description='Custom Payroll',
	author='Fayez Qandeel',
	author_email='customvivvo@gmail.com',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
