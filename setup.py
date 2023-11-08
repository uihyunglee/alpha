
from setuptools import setup, find_packages

setup(
    name='alpha',
    version='0.0.2',
    description='[SURI] Alpha-study library',
    author='uihyunglee,surfhawk',
    author_email='uihyunglee.tech@gmail.com',
    url='https://github.com/uihyunglee/alpha',
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

# HOW TO INSTALL WITH PIP
# pip install git+https://{YOUR_REMOTE_GIT_URL}
