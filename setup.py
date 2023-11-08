
from setuptools import setup, find_packages

setup(
    name='alpha',
    version='0.0.1',
    description='[SURI] Alpha-study library',
    author='uihyunglee,surfhawk',
    author_email='uihyunglee.tech@gmail.com',
    url='https://gitlab.vsq.kr:5443/hh/hawkivelib_push',
    python_requires='>=3.7',
    include_package_data=True,
    package_data={
        'alpha': ['*', ]
    },
    install_requires=[
        "numpy",
        "pandas",
        "psycopg2",
    ],
)
