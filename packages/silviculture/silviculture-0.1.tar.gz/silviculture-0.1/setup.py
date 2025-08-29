from setuptools import setup

installation_requirements = [

]

setup(
    version="0.1",
    name="silviculture",
    description="graph care",
    author="(~)",
    url="https://github.com/freeflock/silviculture",
    package_dir={"": "packages"},
    packages=["silviculture"],
    install_requires=installation_requirements,
)
