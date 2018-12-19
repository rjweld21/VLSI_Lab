import pandas as pd, numpy as np
import matplotlib.pyplot as plt
import os

HALF_TRIGGER = 0.5
DATA_DIR = 'data'
PLOT_DIR = 'plots'
if not os.path.exists(PLOT_DIR):
    os.mkdir(PLOT_DIR)

def load_data(filename, exclude=[], print_cols=False):
    # Function to read CSV data into pandas dataframe and drop any specified
        #columns
        
    df = pd.read_csv(filename)
    print('\nFile found!')
    if print_cols:
        print('Columns:', list(df))
    
    ex_count = 0
    if exclude:
        for ex in exclude:
            try:
                df = df.drop(labels=ex, axis=1)
                ex_count += 1
            except Exception as e:
                print('%s not found in CSV columns' % ex)
        
    print('\nLoaded %s and excluded %s columns\n' % (filename, ex_count))
    
    return df
    
def get_files(f_dir, print_nums=True):
    """
        Function to get user input of CSV to plot based on CSV
            index in file directory. If incorrect index is input,
            function acts recursively to ask for new correct input
    """
    # If data directory files are to be output, output them with 
        # associated index numbers
    if len(os.listdir(f_dir)) == 1:
        print('Loading only file found in directory...')
        return os.path.join(f_dir, os.listdir(f_dir)[0])
    if print_nums:
        for i, f in enumerate(os.listdir(f_dir)):
            print('%s: %s' % (i, f))
        
    # Get user input for index
    num = input('Enter number of file to select: ')
    try:
        # If index is valid, return joined path of data directory and filename
        f = os.listdir(f_dir)[int(num)]
        return os.path.join(f_dir, f)
    except:
        # If index is not valid, notify user and re-run function. No join
            # occurs on this output because it will occur once a correct
            # file is found.
        print('\nFile at index %s not found! '
                'Re-enter selection from list above!\n' % num)
        f = get_files(f_dir, print_nums=False)
        return f
    
def plot_data(data, separate=False, savename=False, clockOverlayCol=False,
                replace_on_ylabel=[]):
    if clockOverlayCol:
        clk = data[clockOverlayCol]
        del data[clockOverlayCol]
        
    if separate:
        global fig, halfs_data, halfs_clock, TOP_TRIGGER
        halfs_data = {}
        halfs_clock = {}
        
        fig, axes = plt.subplots(nrows=data.shape[1], sharex=True)
        
        for i, col in enumerate(sorted(set(list(data)))):
            TOP_TRIGGER = max(data[col])
            ylabel_text = str(col)
            for r in replace_on_ylabel:
                ylabel_text = ylabel_text.replace(str(r), '')
                
            if i == 0:
                axes[i].set_title('Simulation Waveforms')
            axes[i].set_ylabel(ylabel_text)
            axes[i].plot(data[col])
            axes[i].spines['top'].set_visible(False)
            axes[i].spines['right'].set_visible(False)
            
            if clockOverlayCol:
                axes[i].plot(clk, linestyle='--') # marker='.')
            if i == len(list(data))-1:
                axes[i].set_xlabel('Samples (1 Sample = 1 ps)')
            
            half = np.array([TOP_TRIGGER * HALF_TRIGGER]*len(data[col]))
            h_ind = np.argwhere(np.diff(np.sign(data[col] - half))).flatten()
            h_clk = np.argwhere(np.diff(np.sign(clk - half))).flatten()
            halfs_data[axes[i]] = []
            halfs_clock[axes[i]] = []
            for j, val in enumerate(h_ind):
                if not j == len(h_ind)-1:
                    if abs(val - h_ind[j+1]) > 10:
                        halfs_data[axes[i]].append(val)
                        halfs_clock[axes[i]].append(h_clk[j])
                else:
                    halfs_data[axes[i]].append(val)
                    halfs_clock[axes[i]].append(h_clk[j])
            
        
        plt.subplots_adjust(hspace=0.2)
    else:
        plt.plot(data.T)
        
        if clockOverlayCol:
                plt.plot(clk, linestyle='--')
                
        
        
    if savename:
        outfile = os.path.join(PLOT_DIR, savename + '.png')
        plt.savefig(outfile)
        
    cid = fig.canvas.mpl_connect('button_press_event', onclick)
    plt.xlim([0, 50000])
    plt.show()
    
def onclick(event):
    """
    print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f, axes=%s' %
          ('double' if event.dblclick else 'single', event.button,
           event.x, event.y, event.xdata, event.ydata, event.inaxes))
    """
    # Gets closest 50% point
    xdata = getClosest(event.xdata, halfs_data[event.inaxes], halfs_clock[event.inaxes])
    xdata = event.xdata
    delayPoints['x'].append(xdata)
    
    # If 2 plots have already been plotted and new click comes in, delete previous point
    if len(delayPoints['x'])< 2 and len(delayPoints['p']) > 1:
        for p in delayPoints['p']:
            p.remove()
        delayPoints['p'] = []
    elif len(delayPoints['x']) > 1: # If 2 x points, output difference
        print(abs(xdata - delayPoints['x'][0]), 'samples of delay')
        delayPoints['x'] = []
        
    # Plots chosen point
    delayPoints['p'].append(event.inaxes.plot(xdata, TOP_TRIGGER*HALF_TRIGGER, 'o', c='r')[0])
    fig.canvas.draw()
    fig.canvas.flush_events() #Put on all points
    
def getClosest(xpoint, data_halfs, clk_halfs):
    # Gets abs of difference, smallest value is closest to chosen point
    data = [abs(xpoint - val) for val in data_halfs]
    clk = [abs(xpoint - val) for val in clk_halfs]
    
    if min(data) > min(clk):
        data = clk_halfs[clk.index(min(clk))]
    else:
        data = data_halfs[data.index(min(data))]
    
    return data
    
if __name__ == '__main__':
    delayPoints = {'p': [], 'x': []}
    
    f = get_files(DATA_DIR)
    df = load_data(f, exclude=['time (s)'], print_cols=True)
    f = f.split('\\')[-1]
    plot_data(df, separate=True, savename='.'.join(f.split('.')[:-1]),
                clockOverlayCol='CLK (V)', replace_on_ylabel=[' (V)'])