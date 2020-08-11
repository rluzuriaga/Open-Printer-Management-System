from setuptools import setup, find_packages

setup(
    name='Open-Printer-Management-System',
    version='1.1.0',
    description='Django project to easily view and manage printer SNMP data.',
    url='https://github.com/rluzuriaga/Open-Printer-Management-System',
    license='MIT',
    author='Rodrigo Luzuriaga',
    author_email='me@rodrigoluzuriaga.com',
    maintainer='Rodrigo Luzuriaga',
    maintainer_email='me@rodrigoluzuriaga.com',
    zip_safe=False,
    packages=find_packages(),
    install_requires=[
        'django>=3.0,<4.0',
        'easysnmp>=0.2.5,<0.3.0',
        'gunicorn>=20.0,<21'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Server'
    ]
)