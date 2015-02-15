from setuptools import setup, find_packages

setup(
    name='hanoi',
    description='Toggle on/off features. Rollout python port',
    version='0.0.2',
    url='https://github.com/juandebravo/hanoi',
    author='Juan de Bravo',
    author_email='juandebravo@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    install_requires=['redis'],
    tests_require=['nose', 'pyshould', 'redis-py'],
    test_suite='nose.collector',
    zip_safe=False,
)
