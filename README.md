# dragonboard_testbench
[![Build Status](https://travis-ci.org/cta-observatory/dragonboard_testbench.svg?branch=master)](https://travis-ci.org/cta-observatory/dragonboard_testbench)

A collection of programs to help with DRS4 calibration of the LST test data of the dragon_cam.


## Installation

The easiest way to install this is to use the (Python Conda Distribution)[https://www.continuum.io/downloads].
Once installed you can install some dependencies using

```
conda install numpy scipy pandas matplotlib pytables pyqt=5
```

Now you can install the `dragonboard_testbench` by using *pip*

```
pip install git+https://github.com/cta-observatory/dragonboard_testbench
```

or, if you are developing

```
git clone http://github.com/cta-observatory/dragonboard_testbench
pip install -e dragonboard_testbench
```

## Usage


### DragonViewer

Use the `dragonviewer` executable to view some data, it is in your `$PATH` after
you installed this module.

`dragoviewer [<inputfile>]`

If you do not provide `<inputfile>`, a file dialog will open

![Alt text](/dragonviewer.png?raw=true "Optional Title")

### Scripts

Use `python offset_calculation.py <inputfiles> ... [options]` to convert raw data.dat files to .hdf5 files that can be used by further scripts.

Use `python fit_delta_t.py <inputfile> <outputfile> [options]` to calculate a powerlaw fit a*x^b+c for every cell.

Use `python calibration_performance.py <inputfile> <fit_constants> <offsets> <outputfile> [options]` to plot an overview of the performance of all calibration techniques

## Running the tests

We are using `pytest`, install with

```
$ conda install pytest
```
or, if you are not using anaconda,
```
pip install pytest
```

You can then run the tests using:

```
py.test
```

in the base directory, the output could look like this if everything goes well:

```
$ py.test
===================== test session starts ============================
platform linux -- Python 3.5.1, pytest-2.8.5, py-1.4.31, pluggy-0.3.1
rootdir: /home/maxnoe/Uni/CTA/dragonboard_testbench, inifile: 
collected 2 items 

dragonboard/tests/test_runningstats.py ..

================== 2 passed in 0.28 seconds ==========================
```



