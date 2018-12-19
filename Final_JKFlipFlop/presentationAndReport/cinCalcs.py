import matplotlib.pyplot as plt, numpy as np

def find_b(C_vals):
    b = [1, 0, 1, 0]
    
    b[1] = (C_vals[2]+C_vals[1])/C_vals[2]
    b[3] = (C_vals[0]+C_vals[3]+90)/90
    
    return b, np.prod(b)
    
def get_params(C_vals, NUM_STAGES, g_vals):
    G = np.prod(g_vals)
    H = 90/3
    b, B = find_b(C_vals)
    F = G*B*H
    f = F**(1/NUM_STAGES)
    
    return G, H, B, F, b, f
    
def round_list(l):
    for i in range(len(l)):
        adder = 1 if (l[i]-int(l[i]))>=0.5 else 0
        l[i] = int(l[i]) + adder
        
    return l
    
if __name__ == '__main__':
    NUM_ITER = 10
    NUM_STAGES = 4
    ALL_CIN = np.zeros((NUM_ITER, NUM_STAGES))
    CIN = [8, 5, 4, 5]
    g_vals = [5/3, 1.4367, 4/3, 1.4367]
    
    G, H, B, F, b, f = get_params(CIN, NUM_STAGES, g_vals)
    
    for i in range(NUM_ITER):
        for j in range(NUM_STAGES):
            if j == 0:
                cin = 90+CIN[-(j+1)]+CIN[j]
            elif j == 2:
                cin = CIN[-j] + CIN[-(j+1)]
            else:
                cin = CIN[-j]
                
            g = g_vals[-(j+1)]
                
            CIN[-(j+1)] = g*(cin/f)
            
        print('ITERATION %s: ' % (i+1), 
                'G=',G, 
                'H=',H, 
                'B=',B, 
                'F=',F, 
                'b=',b, 
                'f=',f)
        G, H, B, F, b, f = get_params(CIN, NUM_STAGES, g_vals)
        ALL_CIN[i] = np.array(CIN)
        
    print('C_in VALUES BY ITERATION:\n', ALL_CIN)
    l = ['STAGE %s' % (i+1) for i in range(NUM_STAGES)]
    CIN = np.array(round_list(CIN))
    PMOS = [CIN[0]*(2/5), CIN[1]*(2/5),
            CIN[2]*(2/4), CIN[3]*(2/5)]
    print('\nPMOS K RATIO: \n', PMOS)
    NMOS = [CIN[0]*(3/5), CIN[1]*(3/5),
            CIN[2]*(2/4), CIN[3]*(3/5)]
    print('\nNMOS K RATIOS: \n', NMOS)
    print('\nFINAL b VALUES BY STAGE: \n', b)
    plt.plot(ALL_CIN)
    plt.legend(l)
    plt.xlabel('Iteration')
    plt.ylabel('C_in Value')
    plt.title('C_in Value Stabilization')
    plt.show()