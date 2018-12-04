# J-K Flip-Flop VLSI Final Project
### Author: R.J. Weld

### This folder is for analysis/plotting/storage of project simulations and work.

## Setup
1. Files used for analysis and plotting are written in Python 3. This programming 
language should be downloaded and installed along with its package manager, 
pip.
2. To install needed modules, run `pip3 install -r requirements.txt` from command prompt. 
3. To use `plotdata.py`, create "data" folder within repo and put simulations 
CSVs within that folder before running.
4. More configuration can be added with some knowledge of Python. Mostly by looking 
at `plot_data` function within `plotdata.py` is where features can be added.

## Usage
1. Run `plotdata.py` script with Python 3
2. Script will ask which CSV to load if any were found.
    - Enter corresponding output number of CSV to load
3. Click on points around plot. After 2 points are selected, amount of samples 
difference will be output
    - *NOTE: Multiply sample difference output by sample timescale (I had scale of 
    1 sample = 100 fs)*
    - Python will automatically find 50% point of closest rising or falling edge
    from where user click was detected. If point other than 50% is to be found, 
    edit `HALF_TRIGGER` variable near top of script accordingly.