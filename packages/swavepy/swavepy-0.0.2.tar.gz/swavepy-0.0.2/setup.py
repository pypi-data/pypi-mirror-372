from setuptools import setup, find_packages

setup(
	name='swavepy',
	version='0.0.2',
	description="Modular version of WavePy",
	author="Nienke Blom, Will Pizii",
	packages=find_packages(),
	install_requires=[
		'numpy',
		'matplotlib',
		'numba',
		'ipympl'
	],
	project_urls={
		'Source': 'https://github.com/willpizii/Cam_WavePy/module'
	},
)
