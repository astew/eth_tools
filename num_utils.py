
import numpy as np



def floor_size(a, ):
    return np.floor(a*1e6) / float(1e6)
    
def floor_funds(a, ):
    return np.floor(a*1e2) / float(1e2)

def interp_float_str(fs, available):
    if(fs == 'all'):
        return available
    elif(fs.endswith('%')):
        return available * float(fs[:-1])/100.0
    else:
        return float(fs)
