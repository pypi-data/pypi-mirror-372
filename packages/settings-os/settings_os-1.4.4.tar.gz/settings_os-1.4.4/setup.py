from setuptools import setup, find_packages

setup(
    name='settings-os',
    version='1.4.4',
    packages=find_packages(),
    description='Biblioteca de configurações uteis para projetos diversos.',
    author='Miguel Tenório',
    author_email='deepydev42@gmail.com',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.12',
    install_requires=[
        'selenium',
        'webdriver-manager',
        'sqlalchemy',
        'pymysql',
        'psycopg2-binary',
        'pyodbc',
        'psutil',
        'colorama'
    ],
)
