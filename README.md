# Intellectual_filtration

## About
The program implements intelligent filteration for primary data or signals obtained on the Kvant atomic absorption spectrometer.

## Technologies used and application features
The following technologies were used in the development of this application:
- Python
- Pandas
- PyPlot
- PyQT6

The application is implemented in one function for error-free assembly in an exe-file using Pyinstaller.
The result is displayed on the screen in the form of a filtered spectrum and is saved either in the directory with the executable file, or in a directory created by the user if a batch of data is immediately filtered. Saving occurs as an xls-file.

## Implemented functions
The program implements the following functions:
### 1 Data download methods

    1.1 Loading data from the clipboard
 
    1.2 Loading data using xls-file
 
    1.3 Loading data in batches or one measurement result at a time

### 2 Data processing methods

      2.1 Calculation of the analytical absorption signal from an array of primary data obtained in the format of the Kvant spectrometer
  
      2.2 Further data processing using implemented functions
  
      2.3 Filtering data using an additional filter

      2.4 Averaging data when working with a stack of spectra, calculating the average filtered and unfiltered signals


### 3. Displaying and saving results

      3.1 Saving single filtered spectra and primary data used for calculations
  
      3.2 Saving a file with a set of spectra if the data is loaded in batches

      3.3 Display the filtered and primary signal or display a group of them
  
      3.4 Saving data with intermediate calculations to check the functionality of the algorithm
  

## Installation and launch on another device

Clone repository:
```[
https://github.com/Samiel19/Intellectual_filtration.git
```
Go to application directory:
```
cd intellectual_filtration
```
Create a virtual environment:
```
python3 -m venv env
```
Activate virtual environment:

```
source env/script/activate
```
Install dependencies from the requirements.txt file:
```
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```
Run project:
```
python filter_2.3.py
```
Alternative run (as exe-file):
```
pyi-makespec --onefile filter_2.3.py

add 'sys', 'os', 'fnmatch', 'pandas', 'matplotlib', 'math', 'copy', 'shutil' in hiddenimports list of .spec file

pyinstaller --onefile filter_v2.3.py
```
