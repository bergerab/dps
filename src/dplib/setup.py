from setuptools import setup, find_packages

setup(
    name='dplib',
    version='0.1',
    packages=find_packages(exclude=['tests*']),
    license='MIT',
    description='A data processing library for pointwise and windowed computations',
    long_description=open('README.org').read(),
    url='https://github.com/bergerab/dps',
    author='Adam Berger',
    author_email='bergerab@icloud.com',
    test_suite='nose.collector',
    tests_require=['nose', 'numpy'],
    install_requires=['numpy'],
)
