from setuptools import setup, find_packages

setup(
    author='Juan de Bravo',
    author_email='juandebravo@gmail.com',
    description='Toggle on/off features. Rollout python port',
    include_package_data=True,
    install_requires=['redis'],
    name='hanoi',
    packages=find_packages(),
    tests_require=['nose', 'pyshould', 'redis'],
    test_suite='nose.collector',
    url='https://github.com/juandebravo/hanoi',
    version='0.0.4',
    zip_safe=False,
)
