try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup
	
config = {
	'description': 'My Project',
	'author': 'Antoine Orozco',
	'url': 'URL to get it at.',
	'download_url': 'Where to download it.',
	'author_email': 'orozco_antoine@yahoo.fr'
	'version': '0.1',
	'install_requires': ['nose'],
	'packages': ['MusicShare','templates'],
	'scripts': [],
	'name': 'MusicShare'
}

setup(**config)