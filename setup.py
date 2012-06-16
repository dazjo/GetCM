from setuptools import setup, find_packages

version = "2.4.7"

setup(
    name="GetCM",
    version=version,
    packages=find_packages(),
    install_requires=['tornado==2.2', 'sqlalchemy', 'mako', 'python-android'],
    entry_points={
        'console_scripts': [
            'getcm.server=getcm.app:run_server',
            'getcm.addfile=getcm.utils.addfile:main',
            'getcm.fetchbuilds=getcm.utils.fetchbuilds:main',
        ],
    },
    include_package_data=True,
)
