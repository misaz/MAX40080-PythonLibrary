# MAX40080 Current Sense Amplifier Python Library

This project contains library for controlling MAX40080 Current Sense Amplifier digital sensor from Maxim Integrated (now Analog Devices). Library is written in Python and is designed for use with Single Board Computers (SBC) like Raspberry Pi.

## Features
- Support for reading both current and voltage.
- Buildin conversion of measured values to amps and volts. Reading RAW values of current and voltage from sensor is also supported.
- Support for ADC sample rates ranging from 15 ksps to 1 Msps.
- Support for digital filtering measauring samples ranging from no-everaging to averaging among 128 samples.
- Support for enabling and disabling packet error checking. Library computes and check CRC when this feature is enabled.
- Tested with
	- Raspberry Pi 3B
	- 64-bit Raspberry Pi OS with kernel version 5.15.32
	- (MikroElektronika Pi 3 Click Shield)[https://www.mikroe.com/pi-3-click-shield]
	- (MikroElektronika Current 6 Click Board)[https://www.mikroe.com/current-6-click]

## Getting started

Install library using following command:

```
pip3 install git+https://github.com/misaz/MAX40080-PythonLibrary
```

If you use MikroE Click Shiend and Current 6 Click Board you need to enable power for the MAX40080 chip. YOu can do this from python or from command line:

```
# Use GPIO 8 when Current 6 Click board is inserted in Click 1 Socket
echo 8 > /sys/class/gpio/export 
echo out > /sys/class/gpio/gpio8/direction 
echo 1 > /sys/class/gpio/gpio8/value

# Use GPIO 7 when Current 6 Click board is inserted in Click 1 Socket
echo 7 > /sys/class/gpio/export 
echo out > /sys/class/gpio/gpio7/direction 
echo 1 > /sys/class/gpio/gpio7/value
```

Then you can use library and access sensor features. Simple example:

```
from max40080 import MAX40080

max = MAX40080()
max.configure()
print(max.read_current())
```

## Functions

MAX40080 class provides you following methods:

```
configure(sample_rate_khz=15, digital_filter=1, measure_current=True, measure_voltage=False)
read_current()
read_voltage()
read_current_and_voltage()
read_raw_current()
read_raw_voltage()
read_raw_current_and_voltage()
```
