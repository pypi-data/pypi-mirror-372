from avoca.bindings.gcwerks import read_gcwerks
import tucavoc
from pathlib import Path
import pandas as pd

data_folder = Path(*tucavoc.__path__).parent / "data"
def load_simple_dataset() -> pd.DataFrame:


    df_calc = read_gcwerks(
        data_folder / "TestData.dat"
    )

    return df_calc
