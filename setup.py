from setuptools import setup, find_packages

version = "2.4.5"

setup(
    name="GetCM",
    version=version,
    packages=find_packages(),
    install_requires=['tornado', 'sqlalchemy', 'mako', 'python-android'],
    entry_points={
        'console_scripts': [
            'getcm.server=getcm.app:run_server',
            'getcm.addfile=getcm.utils.addfile:main',
            'getcm.fetchbuilds=getcm.utils.fetchbuilds:main',
        ],
    },
    include_package_data=True,
)
