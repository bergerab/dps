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
    tests_require=['nose'],    
)
