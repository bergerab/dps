from setuptools import setup

setup(
    name='DPS Relay',
    version='1.0',
    long_description=__doc__,
    packages=['dps_relay'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Flask',
    ],
)
