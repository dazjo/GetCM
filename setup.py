from setuptools import setup, find_packages

version = "2.4.9"

setup(
    name="GetCM",
    version=version,
    packages=find_packages(),
    install_requires=['tornado==2.4', 'sqlalchemy', 'mako', 'python-android'],
    tests_require=['nose'],
    entry_points={
        'console_scripts': [
            'getcm.server=getcm.app:run_server',
            'getcm.addfile=getcm.utils.addfile:main',
            'getcm.fetchbuilds=getcm.utils.fetchbuilds:main',
        ],
    },
    include_package_data=True,
)
