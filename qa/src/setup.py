

from setuptools import find_namespace_packages
from setuptools import setup

__version__ = '1.1.0'

setup(
    name='np-cats-qa',
    version=__version__,
    packages=find_namespace_packages(include=['np_cats_qa', 'np_cats_qa.*'],
                                     exclude=['np_cats_qa.steps.db', 'np_cats_qa.steps.mock']),
    include_package_data=True,
    author='',
    author_email='a_agafonov@test.com',
    url='[url]',
    install_requires=[
        'ulid2>=0.2.0',
        'npqa-http>=2.0.0',
        'npqa-report>=2.0.0',
        'capi-lib-python>=2.4.2',
    ]

)
