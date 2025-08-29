from setuptools import setup, find_packages
setup(
    name='jaguardb_socket_client',
    version='3.4.7',
    author = 'JaguarDB',
    description = 'Socket client for Jaguar vector database',
    url = 'http://www.jaguardb.com',
    license = 'Apache 2.0',
    python_requires = '>=3.0',
    packages=find_packages(),
    include_package_data=True,
    data_files=[
        ('jaguardb', ['jaguardb_socket_client/LICENSE', 'jaguardb_socket_client/README.md', 'jaguardb_socket_client/libJaguarClient.so', 'jaguardb_socket_client/jaguarpy.so', 'jaguardb_socket_client/JaguarSocketClient.py'])
    ],
)
