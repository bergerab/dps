from setuptools import setup, find_packages

setup(
    name='dps_services',
    version='0.1',
    packages=find_packages(exclude=['tests*']),
    license='MIT',
    description='Micro-services for DPS',
    long_description=open('README.org').read(),
    url='https://github.com/bergerab/dps',
    author='Adam Berger',
    author_email='bergerab@icloud.com',
    test_suite='nose.collector',
    tests_require=['nose', 'requests'],
    install_requires=['numpy', 'flask', 'pandas'],
)
