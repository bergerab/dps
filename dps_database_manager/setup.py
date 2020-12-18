from setuptools import setup

setup(
    name='DPS Database Manager',
    version='1.0',
    long_description=__doc__,
    packages=['dps_database_manager'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Flask',
        'SQLAlchemy',
        'psycopg2-binary',
        'expiringdict',
    ],
    test_suite='nose.collector',
    tests_require=['nose'],    
)
