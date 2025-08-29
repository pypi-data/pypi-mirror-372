from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
	long_description = fh.read() 

' read version '
version = None
with open("version.txt", "r", encoding="utf-8") as fh:
    version = fh.read()

setup(
	name='openadbapi',
	version=version,
	author='Christian Schwatke',
	author_email='christian.schwatke@tum.de', 
	license="MIT",
	license_files=[], 
	packages=find_packages(where="src"),
	package_dir={"": "src"},
	url='https://gitlab.lrz.de/openadb/python3-openadbapi',
	description='OpenADB-API',
	long_description=long_description,
	long_description_content_type="text/markdown", 
	include_package_data=True,
	package_data={},
	install_requires=[],
	scripts=[]
)

