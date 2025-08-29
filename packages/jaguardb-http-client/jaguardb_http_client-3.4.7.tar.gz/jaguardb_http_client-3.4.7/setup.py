from setuptools import setup, find_packages
setup(
    name='jaguardb_http_client',
    version='3.4.7',
    author = 'JaguarDB',
    description = 'Http client for Jaguar vector database',
    url = 'http://www.jaguardb.com',
    license = 'Apache 2.0',
    python_requires = '>=3.0',
    packages=find_packages(),
    include_package_data=True,
    data_files=[
        ('jaguardb', ['jaguardb_http_client/LICENSE', 'jaguardb_http_client/README-http.md', 'jaguardb_http_client/JaguarHttpClient.py'])
    ],
)
