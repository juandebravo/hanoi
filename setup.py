from setuptools import setup, find_packages

setup(
    name='hanoy',
    description='Toggle on/off features. Rollout python port',
    version='0.0.1',
    url='https://github.com/juandebravo/hanoi',
    author='Juan de Bravo',
    author_email='juandebravo@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],
    tests_require=['nose', 'pyshould'],
    test_suite="nose.collector",
    zip_safe=False,
)
