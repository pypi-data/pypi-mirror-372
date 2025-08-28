from setuptools import setup


setup(
    name='SensorMiddleware',
    version='1.3.1',
    author_name='Pablo Skubert',
    author_email='pablo1920@protonmail.com',

    packages=['ecotrust_smiddleware'],
    install_requires=[
        "boto3==1.24.57",
        "botocore==1.27.96",
        "psutil==5.9.8",
        "typer==0.12.1",
        "requests-toolbelt==1.0.0",
        "gevent==22.10.2",
    ],
    description='Middleware para os Sensores EcoTrust',
    long_description=open('README.md', 'r').read(),
    entry_points={
        'console_scripts': [
            'scontroler = ecotrust_smiddleware.main:scontroler_main'
        ]
    },
    python_requires='>=3.7',
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
    ],
)
