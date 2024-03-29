import pytest
from utilities import handle_error
from io import StringIO
import sys


def test_handle_error(capfd):
    try:
        raise ValueError("Test error")
    except Exception as e:
        handle_error(e)
    out, err = capfd.readouterr()
    assert "Test error" in err