from pathlib import Path

import pandas as pd

import tucavoc
from tucavoc.exports.empa_qa_tools import export_EmpaQATool

tucavoc_test_outputs = Path(*tucavoc.__path__).parent / "tests" / "exports" / "outputs" / "qa_tool"
tucavoc_test_outputs.mkdir(exist_ok=True, parents=True)


def test_export_qa_tool():

    dt =  pd.date_range("2020-01-01", periods=3, freq="D")
    export_EmpaQATool(
        pd.DataFrame(
            {
                ("-", "datetime"): dt,
                ("StartEndOffsets", "datetime_start"): dt - pd.Timedelta("1h"),
                ("StartEndOffsets", "datetime_end"): dt + pd.Timedelta("2h"),
                ("-", "type"): ["std", "blank", "air"],
                ("sub_A", "conc"): [1.0, 0.0, 2.0],
                ("sub_A", "flag"): [0] * 3,
                ("sub_B", "conc"): [2.0, 0.0, 1.0],
                ("sub_B", "flag"): [0] * 3,
                ("sub_A", "u_expanded"): [0.1, 0.0, 0.2],
                ("sub_B", "u_expanded"): [0.2, 0.0, 0.1],
                ("sub_A", "u_precision"): [0.1, 0.0, 0.2],
                ("sub_B", "u_precision"): [0.2, 0.0, 0.1],
            }
        ),
        pd.DataFrame(
            {
                "export_name": ["Substance A", "Substance B"],
            },
            index=["sub_A", "sub_B"],
        ),
        export_path=tucavoc_test_outputs,
    )
