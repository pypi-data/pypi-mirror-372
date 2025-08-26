import setuptools
import os
from setuptools.command.install import install

if os.environ.get('CI_COMMIT_TAG'):
    version = os.environ['CI_COMMIT_TAG']
else:
    version = os.environ['CI_JOB_ID']

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('requirements.txt') as req:
    requirements = list(filter(None, [x if 'github.com' not in x else None for x in req.read().split('\n')]))
    

EXCLUDE_FROM_PACKAGES = ['docs', 'tests*']

EXTRAS_REQUIREMENTS = {
    'default': [
        'apache-airflow==2.1.4'
    ],
    'composer': [
        'apache-airflow==2.1.4+composer'
    ]
}

setuptools.setup(
    name="awehflow",
    version=version.strip('v'),
    author="Philip Perold",
    author_email="philip@spatialedge.co.za",
    description="Configuration based Apache Airflow",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(exclude=EXCLUDE_FROM_PACKAGES),
    install_requires=requirements,
    setup_requires=['wheel'],
    extras_require=EXTRAS_REQUIREMENTS,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "aweh=awehflow_cli.cli:aweh",
        ]
    }
)