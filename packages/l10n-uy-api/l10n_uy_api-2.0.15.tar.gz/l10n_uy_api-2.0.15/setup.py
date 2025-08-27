from setuptools import setup, find_packages


setup(
    name='l10n_uy_api',
    version='2.0.15',
    description='Libreria para localizacion Uruguaya',
    long_description='Libreria para localizacion Uruguaya',
    url='',
    author='BLUEORANGE GROUP',
    author_email='daniel@blueorange.com.ar',
    license='',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='Libreria para localizacion Uruguaya',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=[
        'zeep',
        'python-dateutil',
        'pytz',
        'unidecode==1.2.0',
        'BeautifulSoup4==4.9.3'
    ],
    extras_require={},
    package_data={},
    data_files=[],
    entry_points={},
    include_package_data=True
)
