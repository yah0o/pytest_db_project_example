

from setuptools import find_namespace_packages
from setuptools import setup

__version__ = '1.1.0'

setup(
    name='np-cats-qa',
    version=__version__,
    packages=find_namespace_packages(include=['db_prj_qa', 'db_prj_qa.*'],
                                     exclude=['db_prj_qa.steps.db', 'db_prj_qa.steps.mock']),
    include_package_data=True,
    author='',
    author_email='a_agafonov@test.com',
    url='[url]',
    install_requires=[
        'ulid2>=0.2.0'
    ]

)
