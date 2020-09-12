from setuptools import setup

setup(
    name='UWM Database Manager',
    version='1.0',
    long_description=__doc__,
    packages=['database_manager'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Flask',
        'SQLAlchemy',
        'psycopg2-binary'
    ]
)
