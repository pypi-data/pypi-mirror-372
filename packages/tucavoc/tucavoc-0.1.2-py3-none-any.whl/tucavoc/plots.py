from __future__ import annotations
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

from tucavoc import parameters

from .abstract_uncertainty import Uncertainty

if TYPE_CHECKING:
    from matplotlib.axes import Axes

class Colors:
    CALIBRATION = "firebrick"
    SAMPLE = "mediumblue"
    TANK = "orange"
    BLANK = "darkviolet"
    COMBINED_U = "pink"
    COMBINED_REL_U = "lightgrey"
    EXPANDED_REL_U = "darkgrey"
    EXPANDED_U = "red"


def plot_calibration_areas(
    ax: Axes,
    sub: str,
    df_calc: pd.DataFrame,
    df_subs: pd.DataFrame,
    plot_calibration_factor: bool = True,
):
    """Plot the calibration."""
    # Plot tanks in a different color
    if ("-", "type") in df_calc:
        mask_tank = df_calc[("-", "type")] == "tank"
        if any(mask_tank):
            ax.scatter(
                df_calc.loc[mask_tank, ("-", "datetime")],
                df_calc.loc[mask_tank, (sub, "area")],
                label="tank_area",
                color=Colors.TANK,
            )
        # Simply plot the area of everything
        ax.plot(
            df_calc.loc[~mask_tank, ("-", "datetime")],
            df_calc.loc[~mask_tank, (sub, "area")],
            label="measured_area",
            color=Colors.SAMPLE,
        )
    else:
        # Simply plot the area of everything
        ax.plot(
            df_calc[("-", "datetime")],
            df_calc[(sub, "area")],
            label="measured_area",
            color=Colors.SAMPLE,
        )
    if (sub, "area_calib") in df_calc:
        ax.plot(
            df_calc[("-", "datetime")],
            df_calc[(sub, "area_calib")],
            label="area_calib",
            color=Colors.CALIBRATION,
        )
    if (sub, "area_blank") in df_calc:
        # Check has blank
        ax.plot(
            df_calc[("-", "datetime")],
            df_calc[(sub, "area_blank")],
            label="area_blank",
            color=Colors.BLANK,
        )
        mask_blank = df_calc["is_blank"]
        ax.scatter(
            df_calc.loc[mask_blank, ("-", "datetime")],
            df_calc.loc[mask_blank, (sub, "area")],
            color=Colors.BLANK,
        )
    if (sub, "area_calib") in df_calc:
        ax.fill_between(
            df_calc[("-", "datetime")],
            df_calc[(sub, "area_calib")] - df_calc[(sub, "area_std_calib")],
            df_calc[(sub, "area_calib")] + df_calc[(sub, "area_std_calib")],
            color=Colors.CALIBRATION,
            alpha=0.6,
        )
    mask_calib = df_calc["is_calib"]
    ax.scatter(
        df_calc.loc[mask_calib, ("-", "datetime")],
        df_calc.loc[mask_calib, (sub, "area")],
        color=Colors.CALIBRATION,
    )
    if plot_calibration_factor:
        ax2 = ax.twinx()
        if (sub, "calib_factor") in df_calc:
            if not df_calc[(sub, "calib_factor")].isna().all():
                ax2.plot(
                    df_calc[("-", "datetime")],
                    df_calc[(sub, "calib_factor")],
                    color="grey",
                    label="calibration factor",
                )
            ax2.set_ylabel(parameters.CALIB_FACTOR.unit)
            # Just to show the legend with the others
            ax.plot(
                [],
                color="grey",
                label=f"{parameters.CALIB_FACTOR.name} (scale right)",
            )
        else:
            group = df_subs.loc[sub, "group"]

            mean_crf = (
                df_calc[(group, "mean_carbon_response_factor")]
                if group
                else df_calc[("-", "general_mean_carbon_response_factor")]
            )
            ax2.plot(
                df_calc[("-", "datetime")],
                mean_crf,
                color="grey",
                label=parameters.MEAN_CRF.full_name,
            )
            ax2.set_ylabel(parameters.MEAN_CRF.unit)
            # Just to show the legend with the others
            ax.plot(
                [],
                color="grey",
                label=parameters.MEAN_CRF.full_name + " (scale right)",
            )
    ax.legend()
    ax.set_ylabel("Area [area unit]")

    ax.set_title(f"Areas for {sub}")


def plot_calibration_concs(
    ax: Axes, sub: str, df_calc: pd.DataFrame, df_subs: pd.DataFrame
):
    """Plot the concentration of the calibration."""
    if not df_calc[(sub, "conc")].isna().all():
        ax.plot(
            df_calc[("-", "datetime")],
            df_calc[(sub, "conc")],
            label="Calculated Concentration",
            color=Colors.SAMPLE,
        )
    mask_calibration = df_calc[("-", "type")] == "std"

    conc_calib = (
        df_calc[(sub, "conc_calib")]
        if (sub, "conc_calib") in df_calc
        else df_calc[(sub, "conc")]
    )
    mask_not_nan = ~conc_calib.isna()
    mask = mask_calibration & mask_not_nan

    ax.scatter(
        df_calc.loc[mask, ("-", "datetime")],
        conc_calib.loc[mask],
        label="Calibration Concentration",
        color=Colors.CALIBRATION,
    )
    ax.set_ylabel("[pmol/mol]")
    ax.legend()


def plot_uncertainties(
    ax: Axes,
    sub: str,
    uncertainties: list[Uncertainty],
    df_calc: pd.DataFrame,
    df_subs: pd.DataFrame,
):
    """Plot the uncertainties."""
    ax.plot(
        df_calc[("-", "datetime")],
        df_calc[(sub, "conc")],
        label="Calculated Concentration",
        color=Colors.SAMPLE,
    )
    top_line = df_calc[(sub, "conc")].to_numpy()
    bot_line = df_calc[(sub, "conc")].to_numpy()
    for u in uncertainties:
        std = df_calc[(sub, f"u_{u.name}")]
        new_top_line = top_line + std
        new_bot_line = bot_line - std
        ax.fill_between(
            df_calc[("-", "datetime")],
            top_line,
            new_top_line,
            label=f"Uncertainty {u.name}",
            color=u.color,
        )
        ax.fill_between(
            df_calc[("-", "datetime")],
            bot_line,
            new_bot_line,
            color=u.color,
        )
        # Update where the lines are
        top_line = new_top_line
        bot_line = new_bot_line

    ax.plot(
        df_calc[("-", "datetime")],
        df_calc[(sub, "conc")] + df_calc[(sub, "u_combined")],
        label="Combined Uncertainty",
        color=Colors.COMBINED_U,
        linestyle="--",
    )
    ax.plot(
        df_calc[("-", "datetime")],
        df_calc[(sub, "conc")] - df_calc[(sub, "u_combined")],
        color=Colors.COMBINED_U,
        linestyle="--",
    )
    ax.plot(
        df_calc[("-", "datetime")],
        df_calc[(sub, "conc")] + df_calc[(sub, "u_expanded")],
        label="Expanded Uncertainty",
        color=Colors.EXPANDED_U,
        linestyle="--",
    )
    ax.plot(
        df_calc[("-", "datetime")],
        df_calc[(sub, "conc")] - df_calc[(sub, "u_expanded")],
        color=Colors.EXPANDED_U,
        linestyle="--",
    )

    ax.set_ylabel("[pmol/mol]")

    ax2 = ax.twinx()
    ax2.plot(
        df_calc[("-", "datetime")],
        df_calc[(sub, "u_rel_combined")] * 100,
        label="Relative Combined Uncertainty",
        color=Colors.COMBINED_REL_U,
        linestyle="--",
    )
    # Just to show the legend with the others
    ax.plot(
        [],
        label="Relative Combined Uncertainty  (scale right)",
        color=Colors.COMBINED_REL_U,
        linestyle="--",
    )
    ax2.plot(
        df_calc[("-", "datetime")],
        df_calc[(sub, "u_rel_expanded")] * 100,
        label="Relative Expanded Uncertainty",
        color=Colors.EXPANDED_REL_U,
        linestyle="--",
    )
    # Just to show the legend with the others
    ax.plot(
        [],
        label="Relative Expanded Uncertainty  (scale right)",
        color=Colors.EXPANDED_REL_U,
        linestyle="--",
    )
    ax2.set_ylim(0, None)
    ax2.set_ylabel("Rel. Error [%]")
    ax.legend()


def plot_uncertainties_err_bars(
    ax: Axes,
    sub: str,
    uncertainties: list[Uncertainty],
    df_calc: pd.DataFrame,
    df_subs: pd.DataFrame,
):
    """Plot the uncertainties using error bars instead of surface errors."""
    ax.scatter(
        df_calc[("-", "datetime")],
        df_calc[(sub, "conc")],
        label="Calculated Concentration",
        color=Colors.SAMPLE,
    )
    top_line = df_calc[(sub, "conc")].to_numpy()
    bot_line = df_calc[(sub, "conc")].to_numpy()

    cap_size = 5
    for u in uncertainties:
        std = df_calc[(sub, f"u_{u.name}")]
        new_top_line = top_line + std
        new_bot_line = bot_line - std
        ax.errorbar(
            df_calc[("-", "datetime")],
            top_line,
            std,
            lolims=True,
            label=f"Uncertainty {u.name}",
            linestyle="None",
            color=u.color,
            capsize=cap_size,
        )
        ax.errorbar(
            df_calc[("-", "datetime")],
            bot_line,
            std,
            uplims=True,
            linestyle="None",
            color=u.color,
            capsize=cap_size,
        )
        # Update where the lines are
        top_line = new_top_line
        bot_line = new_bot_line

    ax.errorbar(
        df_calc[("-", "datetime")],
        df_calc[(sub, "conc")],
        df_calc[(sub, "u_combined")],
        label="Combined Uncertainty",
        color=Colors.COMBINED_U,
        linestyle="None",
        capsize=3 * cap_size,
    )
    ax.errorbar(
        df_calc[("-", "datetime")],
        df_calc[(sub, "conc")],
        df_calc[(sub, "u_expanded")],
        label="Expanded Uncertainty",
        color=Colors.EXPANDED_U,
        linestyle="None",
        capsize=3 * cap_size,
    )

    ax.set_ylabel("[pmol/mol]")
    ax.legend()


def plot_uncertainties_parts(
    ax: Axes,
    sub: str,
    uncertainties: list[Uncertainty],
    df_calc: pd.DataFrame,
    df_subs: pd.DataFrame,
):
    """Plot the part of uncertainties in the total uncertainties."""
    for u in uncertainties:
        part_of_u = df_calc[(sub, f"ratio_u_{u.name}_in_u_combined")]

        ax.plot(
            df_calc[("-", "datetime")],
            part_of_u,
            label=f"Uncertainty {u.name}",
            color=u.color,
        )

    ax.set_ylabel("[%]")
    ax.legend()


def plot_group_conc(
    ax: Axes,
    group: str,
    df_calc: pd.DataFrame,
    df_subs: pd.DataFrame,
):
    """Plot the uncertainties."""
    ax.plot(
        df_calc[("-", "datetime")],
        df_calc[(group, "conc")],
        label="Calculated Concentration",
        color=Colors.SAMPLE,
    )
    top_line = np.zeros(len(df_calc))
    for member in df_subs["group"].loc[df_subs["group"] == group].index:
        conc = df_calc[(member, "conc")]
        new_top_line = top_line + conc
        ax.fill_between(
            df_calc[("-", "datetime")],
            top_line,
            new_top_line,
            label=member,
        )

        # Update where the line is
        top_line = new_top_line

    ax.set_ylabel("[pmol/mol]")
    ax.legend()
