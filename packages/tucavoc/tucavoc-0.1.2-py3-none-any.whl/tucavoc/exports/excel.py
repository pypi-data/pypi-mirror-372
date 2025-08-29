import enum
from pathlib import Path
import pandas as pd

from tucavoc.additional_data import AdditionalData


class TableType(enum.Enum):
    """The different table types."""

    # Excel table
    EXCEL = enum.auto()
    # CSV table
    CSV = enum.auto()


def export_to_table(
    df_calc: pd.DataFrame,
    df_substances: pd.DataFrame,
    export_path: Path,
    table_type: TableType = TableType.EXCEL,
    additional_data: dict[type, AdditionalData] = {},
):
    """Export to excel."""
    substances = df_substances.index.to_list()

    # Select columns we want
    base_cols = [
        # ("-", "date"),
        # ("-", "time"),
        ("-", "datetime"),
        ("-", "type"),
    ]
    columns = base_cols + sum(
        [[(sub, "conc"), (sub, "u_rel_expanded")] for sub in substances], []
    )
    sub_to_export_name = {
        sub: df_substances.loc[sub, "export_name"] for sub in substances
    }
    df_output = df_calc[columns].copy()
    # Rename columns to add the units in the header
    df_output.columns = pd.MultiIndex.from_tuples(
        base_cols
        + sum(
            [
                [(sub_to_export_name[sub], "conc [pmol/mol]"), (sub_to_export_name[sub], "u_rel_expanded [%]")]
                for sub in substances
            ],
            [],
        ),
        names=["substance", "property"],
    )
    # Multiply the expanded uncertainty by 100 to get the percentage
    df_output.loc[:, (slice(None), "u_rel_expanded [%]")] *= 100
    # Export
    if table_type == TableType.EXCEL:
        df_output.to_excel(export_path / "concs.xlsx", na_rep="=NA()")
        df_substances.to_excel(export_path / "substances.xlsx", na_rep="=NA()")
    elif table_type == TableType.CSV:
        df_output.to_csv(export_path / "concs.csv")
        df_substances.to_csv(export_path / "substances.csv")
    else:
        raise NotImplementedError(f"Table type {table_type} not implemented.")


if __name__ == "__main__":
    # Simple test
    df_calc = pd.DataFrame(
        {
            ("-", "date"): ["2020-01-01", "2020-01-02"],
            ("-", "time"): ["00:00:00", "00:00:00"],
            ("-", "datetime"): ["2020-01-01 00:00:00", "2020-01-02 00:00:00"],
            ("-", "type"): ["calibration", "calibration"],
            ("sub1", "conc"): [1, 2],
            ("sub1", "u_rel_expanded"): [3, 4],
            ("sub2", "conc"): [5, 6],
            ("sub2", "u_rel_expanded"): [7, 8],
        }
    )
    df_substances = pd.DataFrame(
        {
            "name": ["sub1", "sub2"],
        },
        index=["sub1", "sub2"],
    )
    export_to_table(
        df_calc,
        df_substances,
        Path(r"C:\Users\coli\Documents\ovoc-calculations\data"),
    )
