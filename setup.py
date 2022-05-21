from setuptools import find_packages, setup

setup(
    name = 'max40080',
    packages = find_packages(include=['max40080']),
    version = '0.1.1',
    description ='Library used for controlling MAX40080 Current Sense Amplifier I2C Sensor using Single Board Computers like Raspberry Pi.',
	install_requires = ["smbus", "crc"],
    author = 'misaz',
    license = 'MIT',
)