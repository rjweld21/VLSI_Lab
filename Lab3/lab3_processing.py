import json, os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

TIME_COL = 'time (s)'
TOP_TRIGGER = 0.8 # Calculate rise/fall times 20%-80%
BOT_TRIGGER = 0.2
HALF_TRIGGER = 0.5 # 50%

def remove_unpaired(data):
    """
        Function to remove unpaied rising or falling points.
            For instance, if rising points are to be found and a top
            intersection does not have a bottom intersection before it,
            the top is filtered out to create a top and bot pair of 
            same length
            
        INPUT
        :data: - dictionary of lists where keys are 'top' and 'bot' for top
            and bottom indicies
            
        OUTPUT
        :data: - :data: input with filtered out unpaired indicies
    """
    # If top and bot points are of equal amount it is known that if
        # a point must be filtered out from one aspect, a point must
        # be filtered out from the other end of the other aspect
    if len(data['top']) == len(data['bot']):
        if data['top'][1] < data['bot'][0]:
            data['top'] = data['top'][1:]
            data['bot'] = data['bot'][:-1]
            
        elif data['top'][0] > data['bot'][1]:
            data['bot'] = data['bot'][1:]
            data['top'] = data['top'][:-1]
    # If not equal in length, must do processing differently
    else:
        # Checks if one bound has 2 extra points than the other
            # If this is true, first and last point will be filtered
            # out of mismatched bound
        bothSides = False
        if abs(len(data['top'])-len(data['bot']))==2:
            bothSides=True
            
        # Checks if there is an extra top point in beginning
        if data['top'][1] < data['bot'][0]:
            data['top'] = data['top'][1:]
            if bothSides:
                data['top'] = data['top'][:-1]
            
        # Checks if there is an extra bot point in beginning
        elif data['top'][0] > data['bot'][1]:
            data['bot'] = data['bot'][1:]
            if bothSides:
                data['bot'] = data['bot'][:-1]

    return data
    
def get_risefall_inds(data):
    """
        Function to get rise and fall point indicies from input data
        
        INPUT
        :data: - dictionary of lists where keys are 'top' and 'bot' for top
            and bottom indicies that has been processed by removed_unpaired
            
        OUTPUTS
        :rise: - np.array of index points associated with rise in waveform
        :fall: - np.array of index points associated with fall in waveform
        
        NOTE: Rise and fall outputs are with orientation of...
            [top x-index, bot x-index]
    """
    try:
        # Zips top and bot lists so top, bot indicies are paired into Nx2 array
        temp = zip(data['top'], data['bot'])
    except KeyError as e: # Raises error if data is not formatted correctly
        raise KeyError('\'top\' and \'bot\' keys required in data input')
    
    # Init lists for rise and fall coords
    rise = []
    fall = []
    rise_half = []
    fall_half = []
    
    # Iterate through top, bot pairs
    for i, t in enumerate(temp):
        # If top index is before bottom, it is a rise event
        if t[0] > t[1]:
            rise.append(t)
            rise_half.append(data['half'][i])
        else: # Otherwise it is a fall event
            fall.append(t)
            fall_half.append(data['half'][i])
            
    # Return as numpy arrays
    return np.array(rise), np.array(fall), np.array(rise_half), np.array(fall_half)
    
def calc_riseFall_times(index_dict, time):
    """
        Function to get rise and fall times for input indicies
        
        INPUT
        :index_dict: - dictionary of lists where keys are 'rise' and 'fall' for top
            and bottom indicies that has been processed by get_risefall_inds
        :time: - timescale for times to be calculated from based off index_dict
            indicies
            
        OUTPUTS
        :rise_ts: - list of rise times
        :fall_ts: - list of fall times
    """
    rise = index_dict['rise']
    fall = index_dict['fall']

    # Get timesets then subtract...
        # top-bot for rise
        # bot-top for fall
    rise_ts = np.array([np.sum(time[r]*[1, -1]) for r in rise])
    fall_ts = np.array([np.sum(time[f]*[-1, 1]) for f in fall])

    return rise_ts, fall_ts
    
def osc_prop_time(input_node, time):
    """
        Function to calculate rise and fall propagation times of specified wave
            in oscillator
            
        INPUTS
        :input_node: - current curve to evaluate against itself curve
        :time: - timescale to be referenced for time differences
        
        OUTPUTS
        :rise_prop_ts: - propagation rise time for node
        :fall_prop_ts: - propagation fall time for node
        :prop_ts: - average propagation time
    """
    node = {}; node.update(input_node)
    
    rise_prop_ts = []
    fall_prop_ts = []
    
    for i, fallIndex in enumerate(node['fall_half']):
        fall_prop_ts.append(time[node['rise_half'][i]] - time[fallIndex])
        
        try:
            fall_prop_ts.append(time[node['fall_half'][i+1]] - time[riseIndex])
        except:
            pass
            
    # Get averate propagation delay
    prop_ts = np.mean(list(rise_prop_ts) + list(fall_prop_ts))
    
    return np.array(rise_prop_ts), np.array(fall_prop_ts), prop_ts
    
def calc_prop_times(node, source, time):
    """
        Function to calculate rise and fall propagation times of specified input
            node against all other node waveforms
        
        INPUTS
        :node: - current curve to evaluate against input curve
        :source: - input curve
        :time: - timescale to be referenced for time differences
        
        OUTPUTS
        :rise_prop_ts: - propagation rise time for node
        :fall_prop_ts: - propagation fall time for node
    """
    node1 = {}; node1.update(node)
    source1 = {}; source1.update(source)
    
    # Check that first half point on current node is for rising edge
        # First point for input edge will always be on rise, so
        # these calculations will only work out for current traces
        # where the current node's first half point is on falling edge
    nodePoints = list(node1['rise_half']) + list(node1['fall_half'])
    
    if not min(nodePoints) in node1['fall_half']:
        return "[Cannot compute]", "[Cannot compute]", "[Cannot compute]"
        
    # First rise half of input curve (source) should be
        # before the first fall half of current node
        # If this is found to not be the case, remove first
        # fall half of current node
    if node1['fall_half'][0] < source1['rise_half'][0]:
        node1['fall_half'] = node1['fall_half'][1:]
        
    # Get propagation delay for rising by iterating through current trace
        # 50% points on rising edges. Current trace is used because this
        # trace will always have as many or less points than the input
        # trace so there won't be any index errors when indexing the
        # input trace falling edge points
    rise_prop_ts = []
    for i, riseIndex in enumerate(node1['rise_half']):
        rise_prop_ts.append(time[riseIndex] - time[source1['fall_half'][i]])
        
    # Get propagation delay for falling with same but opposite methodology
        # as used for rise prop.
    fall_prop_ts = []
    for i, fallIndex in enumerate(node1['fall_half']):
        fall_prop_ts.append(time[fallIndex] - time[source1['rise_half'][i]])
        
    # Get averate propagation delay
    prop_ts = np.mean(list(rise_prop_ts) + list(fall_prop_ts))
    
    return np.array(rise_prop_ts), np.array(fall_prop_ts), prop_ts
    
def arrays_to_strings(records):
    """
        Function to convert any arrays to strings for json output
        
        INPUT
        :records: - dictionary with lists within
        
        OUTPUT
        :records: - :records: input with lists converted to strings
    """
    # Iterate through dictionary keys
    for k in list(records):
        # If entry is dictionary, recursively operate on
        if type(records[k]) == dict:
            records[k] = arrays_to_strings(records[k])
        # If entry is a list...
        elif type(records[k]) == list:
            # Iterate through contents
            for r in records[k]:
                # If content is np.array, convert using np function
                if type(r) == np.array:
                    records[k][records[k].index(r)] = np.array2string(r, separator=',')
            records[k] = str(records[k]).replace('\n', ',')
        else: # Just do regular conversion for all other data types
            records[k] = str(records[k]).replace('\n', ',')
                
    return records
    
def load_record(filepath):
    """
        STATUS: NOT FINISHED
        
        Function to load data into original data types from records JSON output
        
        INPUT
        :filepath: - Filepath to record file to load
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError('Input path %s does not exists' % filepath)
        
    data = json.load(open(filepath, 'r'))
    for key1 in list(data):
        for key2 in list(data[key1]):
            try:
                data[key1][key2] = np.fromstring(data[key1][key2], sep='')
            except Exception as e:
                print(type(e), e)
                
    print(data)