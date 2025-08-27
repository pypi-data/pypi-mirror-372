from setuptools import setup, find_namespace_packages

setup(
    name='brynq_sdk_profit',
    version='4.1.2',
    description='Profit wrapper from BrynQ',
    long_description='Profit wrapper from BrynQ',
    author='BrynQ',
    author_email='support@brynq.com',
    packages=find_namespace_packages(include=['brynq_sdk*']),
    license='BrynQ License',
    install_requires=[
        'brynq-sdk-brynq>=4,<5',
        'brynq-sdk-functions>=2',
        'aiohttp>=3,<=4',
        'pandas>=1,<3',
        'requests>=2,<=3',
        'tenacity>=8,<9',
    ],
    zip_safe=False,
)
