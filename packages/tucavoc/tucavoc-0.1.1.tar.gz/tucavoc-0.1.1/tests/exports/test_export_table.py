from pathlib import Path

import pandas as pd

import tucavoc
from tucavoc.exports.excel import TableType, export_to_table

tucavoc_test_outputs = Path(*tucavoc.__path__).parent / "tests" / "exports" / "outputs"
tucavoc_test_outputs.mkdir(exist_ok=True, parents=True)


def test_can_run():
    export_to_table(
        pd.DataFrame(
            {
                ("-", "datetime"): pd.date_range("2020-01-01", periods=3, freq="D"),
                ("-", "type"): ["std", "blank", "air"],
                ("sub_A", "conc"): [1.0, 0.0, 2.0],
                ("sub_B", "conc"): [2.0, 0.0, 1.0],
                ("sub_A", "u_rel_expanded"): [0.1, 0.0, 0.2],
                ("sub_B", "u_rel_expanded"): [0.2, 0.0, 0.1],
            }
        ),
        pd.DataFrame(
            {
                "export_name": ["Substance A", "Substance B"],
            },
            index=["sub_A", "sub_B"],
        ),
        export_path=tucavoc_test_outputs,
        table_type=TableType.CSV,
    )
