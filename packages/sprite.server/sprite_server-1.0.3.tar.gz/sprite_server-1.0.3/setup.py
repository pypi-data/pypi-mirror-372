import setuptools
from sprite.lib.util import constants

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name='sprite.server',
    version=constants.PROJECT_VERSION,
    author=constants.PROJECT_AUTHOR,
    author_email=constants.PROJECT_AUTHOR_EMAIL,
    description=constants.PROJECT_DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='',
    include_package_data=True,
    python_requires='>=3.6',
    classifiers=[
        'Programming Language :: Python :: 3',
        "Programming Language :: Python :: 3 :: Only",
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3.14',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Operating System :: OS Independent'
    ],
    install_requires=[
        'Jinja2==3.1.6',
        'MarkupSafe==3.0.2',
        'psutil==7.0.0'
    ]
)
