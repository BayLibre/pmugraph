# pmugraph
A tools to display charts computed from SoC PMUs

## Requirements
The application leverage LibRegice to perform access to target using JTAG.
This uses and only have been tested on python3.6.
The device must be supported by LibRegice (a least, must have a PMU driver).

## Installation
pmugraph uses pyqt5 for UI. Although this could be installed using pip,
this have not given good results, so it is recommended to install it
using the package manager of the distribution.
```
sudo apt-get install python3-pyqt5
```

The rest of the installation use setuptools.This could installed using:
```
apt-get install python3-setuptools
```

Then, you can install pmugraph by runnig:
```
python3 setup.py install --user
```

You may have to install architecture files to support a specific target.
Refer to [libregice wiki](https://github.com/BayLibre/libregice/wiki)
for more details

## Usage
### Options
```
usage: pmugraph.py [-h] [--svd SVD] [--openocd] [--jlink]
                   [--jlink-script JLINK_SCRIPT] [--jlink-device JLINK_DEVICE]
                   [--test] [--cpu-load] [--memory-load]

optional arguments:
  -h, --help            show this help message and exit
  --svd SVD             SVD file that contains registers definition
  --openocd             Use openocd to connect to target
  --test                Use a mock as target
  --cpu-load            Display the cpu load
  --memory-load         Display the memory load

jlink:
  --jlink               Use JLink to connect to target
  --jlink-script JLINK_SCRIPT
                        Load and run a JLink script before to connect to
                        target
  --jlink-device JLINK_DEVICE
                        Name of device to connect to
```

### Examples
```
# Run the demo, with cpu and memory load graphics
# This assumes that RegiceTest has been installed
python3 -m pmugraph --test --svd BL123.svd --cpu-load --memory-load

# Show cpu load of S905X
# This assumes that RegiceMeson has been installed, and openocd is connected to target
python3 -m pmugraph --openocd --svd S905X.svd --cpu-load
```
