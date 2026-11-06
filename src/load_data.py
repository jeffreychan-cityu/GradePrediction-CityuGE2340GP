"""Jeffrey's shared interface. Does not fit models or read test unless requested."""
from pathlib import Path
import pandas as pd
from run_pipeline import FEATURES, TARGET, ROOT

def load_split(name, scaled=True, output_dir=None):
    if name not in {'train','validation','test'}:raise ValueError('Invalid split')
    folder=Path(output_dir) if output_dir else ROOT/'outputs'
    d=pd.read_csv(folder/'processed'/f'{name}_{"scaled" if scaled else "raw"}.csv')
    return d['row_id'].copy(),d[FEATURES].copy(),d[TARGET].copy()
