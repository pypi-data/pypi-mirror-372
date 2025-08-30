"""conftest.py
Custom PyTest configuration.
"""
import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption("--buffer", action="store_true", help="test all possible buffer settings")
    parser.addoption("--calmode", action="store_true", help="test all possible calibration modes")


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    # test both in_buffer settings (where possible)
    if "in_buffer" in metafunc.fixturenames:
        if metafunc.config.getoption("buffer"):
            in_buffer = [True, False]
        else:
            in_buffer = [True]
        metafunc.parametrize("in_buffer", in_buffer)
    # test both out_buffer settings (where possible)
    if "out_buffer" in metafunc.fixturenames:
        if metafunc.config.getoption("buffer"):
            out_buffer = [False, True]
        else:
            out_buffer = [False]
        metafunc.parametrize("out_buffer", out_buffer)
    # test both modes for calibration
    if "cal_mode" in metafunc.fixturenames:
        if metafunc.config.getoption("calmode"):
            cal_mode = ["peak", "rms"]
        else:
            cal_mode = ["peak"]
        metafunc.parametrize("cal_mode", cal_mode)
