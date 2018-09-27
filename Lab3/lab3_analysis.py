import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import lab3_processing as lp
import json

from scipy import signal

# Data filename, time points column name, input wave column name
OSC_DATA = 'oscillator-3.csv'
TIME_COL = 'time (s)'
INPUT_COL = 'net1 (V)'
TOP_TRIGGER = 0.8 # Calculate rise/fall times 20%-80%
BOT_TRIGGER = 0.2
HALF_TRIGGER = 0.5 # 50%

def allPlots(df):
    """
        Function for plotting all output traces
    """
    # Delete time column, custom scale to be created
    del df[TIME_COL]
    
    # Create xrange for plots
    x = range(df.shape[0])
    
    # Scale through output trace columns and plot each one
    for net in list(df):
        # Get output trace series, convert to list
        points = df[net].tolist()
        # Put on plot
        plt.plot(x, points)

    # Show plot
    plt.show()
    
def riseFall_times(df, showPlot=1, saveJson=False):
    """
        Function to find rise and fall indicies of x-axis for output traces
        
        INPUTS
        :df: - dataframe of points for inverter net traces
        :showPlot: - bool for whether plots should be shown of traces
        :saveJson: - string of filename to save records dict to or False to not save
        
        OUTPUT
        :records: - dict of processed data
    """
    # Get time in np.array then remove from dataframe so only y-points are iterated
    time = df[TIME_COL].values
    del df[TIME_COL]
    
    # Create records variable
    records = {}
    
    for i, net in enumerate(list(df)):
        # Create records entry for net
        records[net] = {'top': [], 'bot': [], 'half': []}
        
        # Get points in np.arrays then determine top and bottom values
            # to calculate rise time between
        points = df[net].values
        raw_max = max(points)
        
        # Create arrays of 80% value, 50% value and 20% value
        top = np.array([raw_max * TOP_TRIGGER]*len(points))
        bot = np.array([raw_max * BOT_TRIGGER]*len(points))
        half = np.array([raw_max * HALF_TRIGGER]*len(points))
        
        # Find points of intersections between points and top/bot thresholds
        t_ind = np.argwhere(np.diff(np.sign(points - top))).flatten()
        b_ind = np.argwhere(np.diff(np.sign(points - bot))).flatten()
        h_ind = np.argwhere(np.diff(np.sign(points - half))).flatten()
        
        # Record intersections indicies
        records[net]['top'] = t_ind
        records[net]['bot'] = b_ind
        records[net]['half'] = h_ind
        records[net]['half_ts'] = time[h_ind]

        # Filter out unpaired top or bottom intercepts
        records[net] = lp.remove_unpaired(records[net])
        
        # Get pairs indicies for rising and falling edges
        # NOTE: Rise and fall pairs are with orientation of...
            #       [top x-index, bot x-index]
        rise, fall, rise_half, fall_half = lp.get_risefall_inds(records[net])
        records[net]['rise'] = rise
        records[net]['fall'] = fall
        records[net]['rise_half'] = rise_half
        records[net]['fall_half'] = fall_half
        
        # Calculate rise and fall times
        rise_ts, fall_ts = lp.calc_riseFall_times(records[net], time)
        
        # Keep rise and fall calculated times
        records[net]['rise_ts'] = rise_ts
        records[net]['fall_ts'] = fall_ts
        
        if INPUT_COL in records and not net == INPUT_COL:
            records[net]['initial_input'] = 'False, see %s' % INPUT_COL
            rise_prop_ts, fall_prop_ts = lp.calc_prop_times(records[net], 
                                                            records[INPUT_COL], 
                                                            time)
            
        elif net == INPUT_COL:
            records[net]['initial_input'] = 'True'
            
        else:
            raise Exception('No input recorded to reference, INPUT_COL ' + 
                            'must be same as first for loop iteration net')
            
        # Skip any iterations where i%3!=0
        if not i % 3 == 0:
            continue
            
        if showPlot:
            # Only on first iteration, plot 80%, 50% and 20% lines
            if i == 0:
                plt.plot(time, top, '--', label='80%')
                plt.plot(time, bot, '--', label='20%')
                plt.plot(time, half, '--', label='50%')
                
            # Plot traces and intersectins
            #plt.plot(time[t_ind], points[t_ind], 'go') # Top intersections
            #plt.plot(time[b_ind], points[b_ind], 'bo') # Bottom intersections
            #plt.plot(time[h_ind], points[h_ind], 'ro') # Halfway intersetions
            # 20% - 80% rising edges (black dots)
            plt.plot(time[list(rise[:, 0])], points[list(rise[:, 0])], 'ko')
            plt.plot(time[list(rise[:, 1])], points[list(rise[:, 1])], 'ko')
            # 80% - 20% falling edges (blue dots)
            plt.plot(time[list(fall[:, 0])], points[list(fall[:, 0])], 'bo')
            plt.plot(time[list(fall[:, 1])], points[list(fall[:, 1])], 'bo')
            # Actual inverter curve
            plt.plot(time, points, label='Inv %s' % i)
        
    # If filename is input to save to...
    if saveJson:
        # Convert filename to string just incase
        filename = str(saveJson)
        # Check for JSON extension and add to filename if not found
        if not filename.split('.')[-1].lower() == 'json':
            filename += '.json'
            
        # Convert dictionary lists to strings
        out_json = lp.arrays_to_strings(records)
        
        # Output JSON with indents for easy reading
        json.dump(out_json, open(filename, 'w'), indent=4)
        print('Records saved!')
        
    # If chosen, put legend on plot and show plot
    if showPlot:
        print('Plotting...')
        plt.legend()
        plt.show()
        
    return records
    
def print_times(records):
    """
        Function to print rise and fall times calculated
        
        INPUT
        :records: - resulting dictionary from riseFall_times function
    """
    for net in list(records):
        print('Net:', net)
        print('Rise times:', records[net]['rise_ts'])
        print('Fall times:', records[net]['fall_ts'])
        print('Rise propogation times:', records[net]['rise_prop_ts'])
        print('Fall propogation times:', records[net]['fall_prop_ts'])
    
if __name__ == '__main__':
    osc_data = pd.read_csv(OSC_DATA)
    print('Data shape:', osc_data.shape)
    print('Columns:', list(osc_data))
    
    # For outputting plots, True or 1 to turn on and False or 0 to turn off
    PLOTS_ON = 0
    JSON_OUTPUT = 'lab3_records.json'
    JSON_OUTPUT = False
    
    if PLOTS_ON and False:
        allPlots(osc_data)
    
    records = riseFall_times(osc_data, showPlot=PLOTS_ON, saveJson='lab3_records.json')
    
    print_times(records)