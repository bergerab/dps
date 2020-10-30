from setuptools import setup, find_packages

setup(
    name='dps_test',
    version='0.1',
    packages=find_packages(exclude=['tests*']),
    license='MIT',
    description='Integration tests for DPS',
    long_description=open('README.org').read(),
    url='https://github.com/bergerab/dps',
    author='Adam Berger',
    author_email='bergerab@icloud.com',
    entry_points = {
        'console_scripts': ['dps_test=dps_test:cli'],
    },
    install_requires=['click', 'requests'],    
)
