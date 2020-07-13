
# This is just a quick visualizer I wrote because for this
# demo - I don't need the entire custom visualization framework
# that ships with MABE, and would like to alter the output
# a bit more anyway.

import pandas as pd
import matplotlib.pyplot as plt
import glob
import os
import numpy as np
import statsmodels.stats.api as sms

from typing import Tuple,List

def get_reps(condition_path:str) -> List[str]:
    return [str(inum) for inum in sorted([int(snum) for snum in os.listdir(condition_path)])]

def get_num_reps(condition_path:str) -> int:
    return len(get_reps(condition_path))

def get_rep_bounds(condition_path:str) -> Tuple[int,int]:
    reps = get_reps(condition_path)
    return (reps[0],reps[-1])

def get_lod_data(condition_path:str) -> List[pd.DataFrame]:
    #num_reps = get_num_reps(condition_path)
    reps = get_reps(condition_path)
    dataframes = [None]*len(reps)
    for i,rep in enumerate(reps):
        file_path = os.path.join(condition_path,rep,'LOD_data.csv')
        dataframes[i] = pd.read_csv(file_path)
        dataframes[i]['rep'] = i
    return dataframes

def conf_int(data:List[float]) -> Tuple[float,float]:
    return sms.DescrStatsW(data).tconfint_mean()

def add_condition_to_plot(condition:str,label:str) -> None: 
    # collect data
    dataframes = get_lod_data(condition)
    dataframe = pd.concat(dataframes)
    # process to get confidence 95% intervals
    processed = pd.pivot_table(dataframe, values='eaten', index=['update'], aggfunc=[np.mean,conf_int])
    processed['conf_int.low'], processed['conf_int.high'] = zip(*processed['conf_int'].eaten)
    # add plot data to canvas
    plt.fill_between(range(len(processed['mean'].eaten)), processed['conf_int.low'], processed['conf_int.high'], alpha=0.3,edgeColor=None)
    plt.plot(processed['mean'].eaten,label=label)

plt.figure(figsize=(4,3),dpi=200)
add_condition_to_plot('predictable',label='Predictable Environment')
add_condition_to_plot('unpredictable',label='Unpredictable Environment')
plt.legend()
plt.title('Evolution of Puzzle-Solving')
plt.xlabel('Generations')
plt.ylabel('Avg Puzzles Solved')
plt.tight_layout()
plt.savefig('figure.png')
