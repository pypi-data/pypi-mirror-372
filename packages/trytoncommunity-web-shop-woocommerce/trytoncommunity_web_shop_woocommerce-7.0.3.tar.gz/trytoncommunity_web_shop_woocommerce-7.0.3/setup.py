#!/usr/bin/env python3
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.

import io
import os
import re
from configparser import ConfigParser

from setuptools import find_packages, setup


def read(fname):
    content = io.open(
        os.path.join(os.path.dirname(__file__), fname),
        'r', encoding='utf-8').read()
    content = re.sub(
        r'(?m)^\.\. toctree::\r?\n((^$|^\s.*$)\r?\n)*', '', content)
    return content


def get_require_version(name):
    require = '%s >= %s.%s, < %s.%s'
    require %= (name, major_version, minor_version,
        major_version, minor_version + 1)
    return require


config = ConfigParser()
config.read_file(open(os.path.join(os.path.dirname(__file__), 'tryton.cfg')))
info = dict(config.items('tryton'))
for key in ('depends', 'extras_depend', 'xml'):
    if key in info:
        info[key] = info[key].strip().splitlines()
version = info.get('version', '0.0.1')
major_version, minor_version, _ = version.split('.', 2)
major_version = int(major_version)
minor_version = int(minor_version)
name = 'trytoncommunity_web_shop_woocommerce'

download_url = 'https://foss.heptapod.net/tryton-community/modules/web_shop_woocommerce/-/releases'  # noqa: E501

requires = ['WooCommerce']
for dep in info.get('depends', []):
    if not re.match(r'(ir|res)(\W|$)', dep):
        requires.append(get_require_version('trytond_%s' % dep))
requires.append(get_require_version('trytond'))

tests_require = [
    get_require_version('trytond_product_image'),
    ]

setup(name=name,
    version=version,
    description='Woocommerce connector for the Tryton platform',
    long_description=read('README.rst'),
    long_description_content_type='text/x-rst',
    author='Kopen Software',
    author_email='info@kopen.es',
    url='https://www.kopen.es',
    download_url=download_url,
    project_urls={
        "Bug Tracker": 'https://foss.heptapod.net/tryton-community/modules/web_shop_woocommerce/-/issues',  # noqa: E501
        "Forum": 'https://www.tryton.org/forum',
        "Source Code": 'https://foss.heptapod.net/tryton-community/modules/web_shop_woocommerce',  # noqa: E501
        },
    keywords='tryton webshop woocommerce',
    package_dir={'trytond.modules.web_shop_woocommerce': '.'},
    packages=(
        ['trytond.modules.web_shop_woocommerce']
        + ['trytond.modules.web_shop_woocommerce.%s' % p
            for p in find_packages()]
        ),
    package_data={
        'trytond.modules.web_shop_woocommerce': (info.get('xml', [])
            + ['tryton.cfg', 'view/*.xml', 'locale/*.po', '*.fodt',
                'icons/*.svg', 'tests/*.rst']),
        },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Plugins',
        'Framework :: Tryton',
        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry',
        'Intended Audience :: Legal Industry',
        'License :: OSI Approved :: '
        'GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: Catalan',
        'Natural Language :: English',
        'Natural Language :: Spanish',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Office/Business',
        ],
    license='GPL-3',
    python_requires='>=3.8',
    install_requires=requires,
    extras_require={
        'test': tests_require,
        },
    zip_safe=False,
    entry_points="""
    [trytond.modules]
    web_shop_woocommerce = trytond.modules.web_shop_woocommerce
    """,  # noqa: E501
    )
