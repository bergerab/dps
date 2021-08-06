from setuptools import setup, find_packages

setup(
    name='dps_batch_processor',
    version='0.1',
    packages=find_packages(exclude=['tests*']),
    license='MIT',
    description='DPS Batch Processor',
    long_description=open('README.org').read(),
    url='https://github.com/bergerab/dps',
    author='Adam Berger',
    author_email='bergerab@icloud.com',
    entry_points = {
        'console_scripts': ['dps_batch_processor=dps_batch_processor:cli'],
    },
    test_suite='nose.collector',
    tests_require=['nose', 'requests'],
    install_requires=['click', 'numpy', 'pandas', 'asyncio', 'aiohttp', 'simplejson'],
)
