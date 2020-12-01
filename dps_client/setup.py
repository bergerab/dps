from setuptools import setup, find_packages

setup(
    name='dps_client',
    version='0.1',
    packages=find_packages(exclude=['tests*']),
    license='MIT',
    description='A client for communicating with the DPS Manager and sending signal data',
    long_description=open('README.org').read(),
    url='https://github.com/bergerab/dps',
    author='Adam Berger',
    author_email='bergerab@icloud.com',
    test_suite='nose.collector',
    entry_points = {
        'console_scripts': ['dps_client=dps_client:cli'],
    },    
    tests_require=['nose'],    
    install_requires=['requests', 'pandas', 'protobuf', 'click'],
)
