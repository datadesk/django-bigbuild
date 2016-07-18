from setuptools import setup


setup(
    name='django-bigbuild',
    version='0.0.1',
    description='A simple system for creating complex pages',
    author='The Los Angeles Times Data Desk',
    author_email='datadesk@latimes.com',
    url='http://www.github.com/datadesk/bigbuilder/',
    packages=(
        'bigbuild',
        'bigbuild.management',
        'bigbuild.management.commands',
        'bigbuild.models',
        'bigbuild.templatetags',
    ),
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Framework :: Django',
        'Framework :: Django :: 1.9',
        'License :: OSI Approved :: MIT License',
    ],
    install_requires=[
        'python-frontmatter>=0.2.1',
        'django-bakery>=0.8.3',
        'validictory>=1.0.1',
        'django-compressor>=2.0',
        'greeking>=2.1.0',
        'pytz',
    ],
)
