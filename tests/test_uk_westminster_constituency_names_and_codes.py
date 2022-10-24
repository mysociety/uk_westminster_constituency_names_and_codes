import uk_westminster_constituency_names_and_codes

import pytest
import pandas as pd
from pathlib import Path


top_level = Path(__file__).parent.parent
package_dir = Path(
    top_level, "data", "packages", "uk_westminster_constituency_names_and_codes"
)


def test_all_constituencies():
    df = pd.read_csv(Path(package_dir, "constituencies_and_codes.csv"))
    assert len(df) == 650, "Does not contain correct number of constituencies"

    for col in df.columns:
        # have to this weird thing as assert does not like False is False
        assert not df[col].isna().any() is True, f"Column {col} contains empty NA"
