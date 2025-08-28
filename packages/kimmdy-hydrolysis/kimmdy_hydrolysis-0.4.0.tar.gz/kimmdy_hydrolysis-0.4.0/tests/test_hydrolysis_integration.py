import os
from pathlib import Path

import pytest

from kimmdy.cmd import kimmdy_run


def read_last_line(file):
    with open(file, "rb") as f:
        try:  # catch OSError in case of one line file
            f.seek(-2, os.SEEK_END)
            while f.read(1) != b"\n":
                f.seek(-2, os.SEEK_CUR)
        except OSError:
            f.seek(0)
        return f.readline().decode()


@pytest.mark.parametrize(
    "arranged_tmp_path", (["test_hydrolysis_integration"]), indirect=True
)
@pytest.mark.slow
def test_integration_hydrolysis_reaction(arranged_tmp_path):
    print(arranged_tmp_path)
    kimmdy_run()

    assert "Finished running last task" in read_last_line(Path("run_prod.kimmdy.log"))
    assert len(list(Path.cwd().glob("run_prod/*"))) == 11
