# PMDSA
Photometric Method for Double Star Analysis

## BACKGROUND
This code is used to analyze basic information of binary star systems. Please note that there are some bugs in this code, that can make some values be very far off, but the median and mean values are generally within ()% of the accepted values. The code as is, provides the system's Seperation (Arcseconds), Position Angle (degrees), and Difference in Magnitude (Delta Mag)

## USE
The code was built for performance on Python3.13, though some backwards compatability likely exists up to a certain point.
### Requirements
```bash
pip install numpy
```
OR
```bash
pip install -r requirements.txt
```
### Bash/cmd
```bash
python3 PMDSA.py /path/to/file.fits
```
or gui with
```bash
python3 gui.py
```
If you don't have your target centered in your images, I suggest adding the RA and DEC (in degrees) in the gui or to the python command like
```bash
python3 PMDSA.py /path/to/file.fits deg_RA deg_DEC
```
To batch run this program use `run.sh` in bash
```bash
./run.sh /path/to/fits/directory [deg_RA] [deg_DEC]
```
or `run.bat` for cmd
```cmd
./run.bat /path/to/fits/directory [deg_RA] [deg_DEC]
```
These shell scripts write the outputs to CSV and can handle multiple targets in different subdirectories if needed.

## NOTES
Images must be plate-solved with WCS values available in the FITS header. My recommendation is to use [astrometry.net](https://nova.astrometry.net)

The output of the function is in a CSV format in the order Seperation,PositionAngle, Delta Magnitude

### Acknowledgments:
Special Thanks to [Numpy](https://github.com/numpy/numpy) and [Matplotlib](https://github.com/matplotlib/matplotlib)

The writing of this code was tested using data provided in the NSF's Four Corners Student Research Consortium funded by NSF grant NSF#2428684 and data from Dimension Point observatory.

### Citations:
If you use this code for the analysis of your code, please include the following insert as an acknowledgment and please reach out to me so we can show your published work here. 
>>Analysis used in this publication was assissted in whole or part by PMDSA  provided by HarbingerOfFire on github (https://github.com/harbingeroffire/PMDSA)

Past works include:

Syfrett et. Al.  "Comparative Analysis of Two Astrometric Measuring Methods on Five Known Binaries"  *Journal of Double Star Observations* Pending Publishing, April 30th. 2025.