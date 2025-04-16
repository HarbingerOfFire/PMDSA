# PMDSA
Photometric Method for Double Star Analysis: an AstroPY Example

## BACKGROUND
This code is used to analyze basic information of binary star systems. Please note that there are some bugs in this code, that can make some values be very far off, but the median and mean values are generally within ()% of the accepted values. The code as is, provides the system's Seperation (Arcseconds), Position Angle (degrees), and Difference in Magnitude (Delta Mag)

## USE
The code was built for performance on Python3.13, though some backwards compatability likely exists up to a certain point.
### Requirements
```bash
pip install astropy numpy matplotlib photutils
```
OR
```bash
pip install -r requirements.txt
```
### Bash/cmd
```bash
python3 PMDSA.py /path/to/file.fits
```
To batch run this program use `run.sh` in bash
```bash
./run.sh /path/to/fits/directory
```
or `run.bat` for cmd
```cmd
./run.bat /path/to/fits/directory
```

## NOTES
Images must be plate-solved with WCS values available in the FITS header. My recommendation is to use [astrometry.net](https://nova.astrometry.net)

The output of the function is in a CSV format in the order Seperation,PositionAngle, Delta Magnitude

### Acknowledgments:
This work made use of [Astropy](https://github.com/astropy/astropy): a community-developed core Python package and an ecosystem of tools and resources for astronomy (Astropy Collaboration, 2013, 2018,  2022).
Special Thanks to [Numpy](https://github.com/numpy/numpy) and [Matplotlib](https://github.com/matplotlib/matplotlib)

The writing of this code was tested using data provided in the NSF's Four Corners Student Research Consortium funded by NSF grant NSF#2428684

### Citations:
If you use this code for the analysis of your code, please include the following insert as an acknowledgment and please reach out to me so we can show your published work here. Please also add acknowledgments to Astropy, Numpy, and Matplotlib
>>Analysis used in this publication was assissted in whole or part by PMDSA  provided by HarbingerOfFire on github (https://github.com/harbingeroffire/PMDSA)

Past works include:
