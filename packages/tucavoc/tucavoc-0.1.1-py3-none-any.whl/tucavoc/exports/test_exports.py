#%%
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta
import tucavoc
from tucavoc.additional_data import StartEndOffsets
from tucavoc.additional_data.empa import BRM_meteo
import tucavoc.exports
from tucavoc.exports import export_EBAS, export_EmpaQATool
import importlib
from tucavoc.flags import QA_Flag, set_flags

#%%
substances = ["A", "B"]
test_dataframe = pd.DataFrame(
    {
        ("A", "conc"): [1, 2],
        ("A", "u_expanded"): [1, 2],
        ("A", "u_precision"): [1, 2],
        ("A", "flag"): [0, QA_Flag.BELOW_DETECTION_LIMIT.value],
        ("B", "conc"): [3, 4],
        ("B", "u_expanded"): [1, 2],
        ("B", "u_precision"): [1, 2],
        ("B", "flag"): [
            QA_Flag.MISSING.value,
            0,
        ],
        ("-", "datetime"): [
            datetime.now() - timedelta(minutes=37),
            datetime.now(),
        ],
    }
)
df_substances = pd.DataFrame({"detection_limit": [1.2, 2.1]}, index=substances)

# %% Adds offsets required for usual exports
t_serie = test_dataframe[("-", "datetime")]
offset = StartEndOffsets()

added_df = offset.add_data(test_dataframe)

brm_meteo = BRM_meteo()
brm_meteo.meteo_dir = Path(
    r"C:\Users\coli\Documents\ovoc-calculations\meteo_files"
)
added_df = brm_meteo.add_data(added_df)

# %% Add the falgs
set_flags(added_df, substances)
added_df
# %%
importlib.reload(tucavoc.exports)
import tucavoc.exports
from tucavoc.exports import export_EBAS

export_EmpaQATool(added_df, df_substances, Path("."))

# %%
