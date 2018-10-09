# Tutorial 3 - Symbol Editing and Transient Simulations
- Repo Author: R.J. Weld
- Institution: Rowan University
- Course: VLSI
- Professor: Dr. Shin
- Lab Instructor: Adam Fifth

Setup
-----
1. Have Python 3.5.x installed
    - Probably works with other 3.x versions but not tested
2. Within lab 3 folder in terminal run...
```bash
pip3 install -r requirements.txt
```

Scope
-----
Oscillator simulation output points, in CSV file, are input to *lab3_analysis.py* to
calculate the rise time, fall time and propogation delays of the oscillator. Plots are then
output for some of the traces and all data is saved in JSON format. 

Editing Script Parameteres
--------------------------
1. Top of script after imports
    - Input CSV filename can be changed
        1. Time and input column names should then be changed to correlate with input CSV
    - Top trigger for rise/fall calculations (Default 80%)
    - Bottom trigger for rise/fall calculations (Default 20%)
    
2. Bottom of script within _if \_\_name\_\_ == '\_\_main\_\_'_ statement
    - Plot outputs can be toggled on/off
    - JSON output filename can be changed or turned off