import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import lab3_processing as lp
import json, os

# Data filename, time points column name, input wave column name
OSC_DATA = os.path.join('data', 'oscillator-3.csv')
TIME_COL = 'time (s)'
INPUT_COL = 'net1 (V)'
TOP_TRIGGER = 0.8 # Calculate rise/fall times 20%-80%
BOT_TRIGGER = 0.2
HALF_TRIGGER = 0.5 # 50%

def allPlots(df):
    """
        Function for plotting all output traces
    """
    
    # Create xrange for plots
    x = range(df.shape[0])
    
    # Scale through output trace columns and plot each one
    for i, net in enumerate(list(df)):
        if net == TIME_COL:
            continue
        # Get output trace series, convert to list
        points = df[net].tolist()
        
        trace = '--'
        if i%2==0:
            trace='-'
        # Put on plot  
        plt.plot(x, points, trace, label=net)

    plt.title('Oscillator Simulated Results')
    plt.xlabel('Time (S x 10e-9)')
    plt.ylabel('Voltage (V)')
    plt.legend()
    
    # Show plot
    plt.show()
    
def riseFall_times(df, showPlot=1, saveJson=False, skipPlots=True, inv_eval=0):
    """
        Function to find rise and fall indicies of x-axis for output traces
        
        INPUTS
        :df: - dataframe of points for inverter net traces
        :showPlot: - bool for whether plots should be shown of traces
        :saveJson: - string of filename to save records dict to or False to not save
        :skipPlots: - bool of whether to skip some plot outputs
        
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
        
        t_ind, b_ind, h_ind = lp.clear_range(t_ind, b_ind, h_ind)
        
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
            #print(records[INPUT_COL]['rise_half'], records[INPUT_COL]['fall_half'])
            rise_prop_ts, fall_prop_ts, prop_ts = lp.calc_prop_times(records[net], 
                                                            records[INPUT_COL], 
                                                            time)
                                                            
            records[net]['rise_prop_ts'] = rise_prop_ts
            records[net]['fall_prop_ts'] = fall_prop_ts
            records[net]['prop_ts'] = prop_ts
            
        elif net == INPUT_COL:
            records[net]['initial_input'] = 'True'
            
            try:
                if not inv_eval:
                    rise_prop_ts, fall_prop_ts, prop_ts = lp.osc_prop_time(records[net],
                                                                            time)
                    records[net]['osc_rise_prop_ts'] = rise_prop_ts
                    records[net]['osc_fall_prop_ts'] = fall_prop_ts
                    records[net]['prop_ts'] = prop_ts
            except Exception as e:
                print('Error hit... If evaluating for single inverter this is fine.')
                inv_eval = 1
                del records[net]['osc_rise_prop_ts']
                del records[net]['osc_fall_prop_ts']
                del records[net]['prop_ts']
                
        else:
            raise Exception('No input recorded to reference, INPUT_COL ' + 
                            'must be same as first for loop iteration net')

        # Skip any iterations where i%3!=0
        if not i % 4 == 0 and skipPlots:
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
            plt.plot(time[list(rise[:, 0])], points[list(rise[:, 0])], 'k*', markersize=13.0)
            plt.plot(time[list(rise[:, 1])], points[list(rise[:, 1])], 'k*', markersize=13.0)
            plt.plot(time[list(rise_half)], points[list(rise_half)], 'k*', markersize=13.0)
            # 80% - 20% falling edges (blue dots)
            plt.plot(time[list(fall[:, 0])], points[list(fall[:, 0])], 'bo', markersize=9.5)
            plt.plot(time[list(fall[:, 1])], points[list(fall[:, 1])], 'bo', markersize=9.5)
            plt.plot(time[list(fall_half)], points[list(fall_half)], 'bo', markersize=9.5)
            # Actual inverter curve
            plt.plot(time, points, label='Inv %s' % i)
        
    if len(records) > 4:
        mean_rise = []
        mean_fall = []
        for net in list(records):
            rise_prop_ts = records[net].get('rise_prop_ts', 'cannot compute')
            fall_prop_ts = records[net].get('fall_prop_ts', 'cannot compute')
            
            if not 'cannot compute' in str(rise_prop_ts).lower():
                mean_rise.extend(list(rise_prop_ts))
                mean_fall.extend(list(fall_prop_ts))
                
        records['all_invs'] = {}
        records['all_invs']['mean_rise_prop_ts'] = np.mean(mean_rise)
        records['all_invs']['mean_fall_prop_ts'] = np.mean(mean_fall)
                
    plt.xlabel('Time (s x 10^-9)')
    plt.ylabel('Voltage (V)')
    plt.title('Oscillator trace outputs')
    
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
        print('\nNet:', net)
        print('Rise times:', records[net]['rise_ts'])
        print('Fall times:', records[net]['fall_ts'])
        if not net == INPUT_COL:
            print('Rise propagation times:', records[net]['rise_prop_ts'])
            print('Fall propagation times:', records[net]['fall_prop_ts'])
    
if __name__ == '__main__':
    osc_data = pd.read_csv(OSC_DATA)
    print('Data shape:', osc_data.shape)
    print('Columns:', list(osc_data))
    
    # For outputting plots, True or 1 to turn on and False or 0 to turn off
    PLOTS_ON = 1
    JSON_OUTPUT = os.path.join('data', 'lab3_osc_records.json')
    
    if PLOTS_ON:
        allPlots(osc_data)
        
    records = riseFall_times(osc_data, showPlot=PLOTS_ON, 
                            saveJson=JSON_OUTPUT, skipPlots=not PLOTS_ON,
                            inv_eval=0)
    
    #print_times(records)