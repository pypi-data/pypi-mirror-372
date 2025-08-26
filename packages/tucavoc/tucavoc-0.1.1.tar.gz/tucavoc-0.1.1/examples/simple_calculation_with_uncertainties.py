import pandas as pd
from avoca.utils import compounds_from_df

import matplotlib.pyplot as plt

from tucavoc.calculations import main
from tucavoc.testing.datasets import load_simple_dataset
from tucavoc.uncertainties import (
    Calibration,
    FurtherInstrumentalProblems,
    Linearity,
    PeakIntegration,
    Precision,
    Sampling,
    Volume,
)

from tucavoc.plots import (
    plot_calibration_areas,
    plot_calibration_concs,
    plot_uncertainties,
    plot_uncertainties_err_bars,
    plot_uncertainties_parts,
)

df_calc = load_simple_dataset()

substances = compounds_from_df(df_calc)

df_subs = pd.DataFrame(columns=["volume_calib", "conc_calib"], index=substances)

df_subs["volume_calib"] = 600
df_subs["volume_sample"] = 600
df_subs["detection_limit"] = 10
df_subs["volume_uncertainty_sample"] = 20
df_subs["volume_uncertainty_calib"] = 20
df_subs["error_systematic_instrument"] = 1.0
df_subs["uncertainty_due_to_linearity"] = 0.0
df_subs["uncertainty_sampling_volume_accuracy"] = 0.0
df_subs["u_peak_area_integ_sample"] = 2.0
df_subs["u_peak_area_integ_calib"] = 2.0
df_subs["conc_calib"] = 4000
df_subs["abs_u_cal"] = 1.0
df_subs["carbon_number"] = 2.0
df_subs["effective_carbon_number_contribution"] = 1.0
df_subs["use_for_general_crf"] = True
df_subs["blank_conc_preset"] = 0.0
df_subs["in_calib"] = False
df_subs.loc[["ethane", "ethene"], "in_calib"] = True

df_subs["group"] = ""

uncs = [
    Precision(),
    Calibration(),
    PeakIntegration(),
    Volume(),
    FurtherInstrumentalProblems(),
    Linearity(),
    Sampling(),
]

df_calc, df_calibrations = main(
    df_calc,
    df_subs,
    uncertainties=uncs,
    debug=True,
    blanks_in_df_subs=True,
    interpolate=False,
)


fig, axes = plt.subplots(3, 1, sharex=True)

name = "ethane"
# name = "methane"
axes[0].plot(df_calc[("-", "datetime")], df_calc[(name, "area_calib")])
plot_calibration_areas(axes[0], name, df_calc, df_subs)
plot_uncertainties(axes[1], name, uncs, df_calc[~df_calc["is_calib"]], df_subs)
plot_uncertainties_parts(axes[2], name, uncs, df_calc[~df_calc["is_calib"]], df_subs)
# plot_uncertainties_err_bars(axes[1], name, uncs, df_calc, df_subs)

plt.show()
