import pytest
from datetime import datetime, timedelta
from pint import UnitRegistry
from libra_toolbox.tritium.lsc_measurements import LIBRASample, LSCSample

ureg = UnitRegistry()


def test_get_relative_time():
    sample_time = "01/01/2023 12:00 PM"
    start_time = "01/01/2023 10:00 AM"
    sample = LIBRASample([], sample_time)
    expected_relative_time = timedelta(hours=2)
    assert sample.get_relative_time(start_time) == expected_relative_time


def test_substract_background():
    activity1 = 10 * ureg.Bq
    activity2 = 5 * ureg.Bq
    sample1 = LSCSample(activity1, "Sample1")
    sample2 = LSCSample(activity2, "Sample2")
    background_sample = LSCSample(2 * ureg.Bq, "Background")
    sample = LIBRASample([sample1, sample2], "01/01/2023 12:00 PM")
    sample.substract_background(background_sample)
    assert sample1.activity == 8 * ureg.Bq
    assert sample2.activity == 3 * ureg.Bq
    assert sample1.background_substracted
    assert sample2.background_substracted


def test_get_soluble_activity():
    activity1 = 10 * ureg.Bq
    activity2 = 5 * ureg.Bq
    sample1 = LSCSample(activity1, "Sample1")
    sample2 = LSCSample(activity2, "Sample2")
    sample = LIBRASample([sample1, sample2], "01/01/2023 12:00 PM")
    assert sample.get_soluble_activity() == 15 * ureg.Bq


def test_get_insoluble_activity():
    activity1 = 10 * ureg.Bq
    activity2 = 5 * ureg.Bq
    activity3 = 3 * ureg.Bq
    sample1 = LSCSample(activity1, "Sample1")
    sample2 = LSCSample(activity2, "Sample2")
    sample3 = LSCSample(activity3, "Sample3")
    sample = LIBRASample([sample1, sample2, sample3], "01/01/2023 12:00 PM")
    assert sample.get_insoluble_activity() == 3 * ureg.Bq


def test_get_total_activity():
    activity1 = 10 * ureg.Bq
    activity2 = 5 * ureg.Bq
    activity3 = 3 * ureg.Bq
    sample1 = LSCSample(activity1, "Sample1")
    sample2 = LSCSample(activity2, "Sample2")
    sample3 = LSCSample(activity3, "Sample3")
    sample = LIBRASample([sample1, sample2, sample3], "01/01/2023 12:00 PM")
    assert sample.get_total_activity() == 18 * ureg.Bq
