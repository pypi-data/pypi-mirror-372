import pandas as pd
from avoca.utils import compounds_from_df

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


def test_calcuation_simple_with_uncertainties():

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

    main(
        df_calc,
        df_subs,
        uncertainties=uncs,
        debug=True,
        blanks_in_df_subs=True,
        interpolate=False,
    )


def test_on_minimal_dataset():

    df_calc_test = pd.DataFrame(
        {
            ("-", "datetime"): pd.date_range("2020-01-01", periods=3, freq="D"),
            ("-", "type"): ["std", "blank", "air"],
            ("sub_A", "area"): [1.0, 0.0, 2.0],
            ("sub_B", "area"): [2.0, 0.0, 1.0],
        }
    )

    df_subs = pd.DataFrame(
        {
            "in_calib": True,
            "conc_calib": 1.0,
        },
        index=["sub_A", "sub_B"],
    )

    df_result, df_calibs = main(
        df_calc_test,
        df_subs,
    )

    # Check the result
    assert df_result.loc[2, ("sub_A", "conc")] == 2.0
    assert df_result.loc[2, ("sub_B", "conc")] == 0.5


def test_on_minimal_blank_not_in_df():

    df_calc_test = pd.DataFrame(
        {
            ("-", "datetime"): pd.date_range("2020-01-01", periods=3, freq="D"),
            ("-", "type"): ["std", "air", "air"],
            ("sub_A", "area"): [1.0, 0.0, 2.0],
            ("sub_B", "area"): [2.0, 2.0, 1.0],
        }
    )

    df_subs = pd.DataFrame(
        {
            "in_calib": True,
            "conc_calib": 1.0,
            "blank_conc_preset": [0.0, 1.0],
        },
        index=["sub_A", "sub_B"],
    )

    df_result, df_calibs = main(
        df_calc_test,
        df_subs,
        blanks_in_df_subs=True,
    )

    # Check the result
    assert df_result.loc[1, ("sub_A", "conc")] == 0.0
    assert df_result.loc[2, ("sub_A", "conc")] == 2.0
    # Same as standard
    assert df_result.loc[1, ("sub_B", "conc")] == 1.0
    # Measured only the blank (1.0)
    assert df_result.loc[2, ("sub_B", "conc")] == 0.0



def test_on_minimal_group():

    df_calc_test = pd.DataFrame(
        {
            ("-", "datetime"): pd.date_range("2020-01-01", periods=3, freq="D"),
            ("-", "type"): ["std", "blank", "air"],
            ("sub_A", "area"): [1.0, 0.0, 2.0],
            ("sub_B", "area"): [2.0, 0.0, 1.0],
            ("sub_C", "area"): [2.0, 1.0, 2.0],
        }
    )

    df_subs = pd.DataFrame(
        {
            "in_calib": True,
            "conc_calib": 1.0,
            "group": ["", "groupped", "groupped"]
        },
        index=["sub_A", "sub_B", "sub_C"],
    )

    df_result, df_calibs = main(
        df_calc_test,
        df_subs,
    )

    # Check the result
    # 1 from c and 0.5 from b
    assert df_result.loc[2, ("groupped", "conc")] == 1.5
