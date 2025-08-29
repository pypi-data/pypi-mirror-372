import pytest
import pint
from datetime import datetime
from libra_toolbox.tritium.lsc_measurements import GasStream, LIBRASample, LSCSample
from libra_toolbox.tritium.model import ureg


def test_get_cumulative_activity():
    # Create sample activities
    activity1 = 10 * ureg.Bq
    activity2 = 20 * ureg.Bq
    activity3 = 30 * ureg.Bq
    activity4 = 40 * ureg.Bq

    # Create LSCSample instances
    sample1 = LSCSample(activity1, "Sample1")
    sample2 = LSCSample(activity2, "Sample2")
    sample3 = LSCSample(activity3, "Sample3")
    sample4 = LSCSample(activity4, "Sample4")

    # Mark background as subtracted
    sample1.background_substracted = True
    sample2.background_substracted = True
    sample3.background_substracted = True
    sample4.background_substracted = True

    # Create LIBRASample instances
    libra_sample1 = LIBRASample([sample1, sample2], "01/01/2023 12:00 PM")
    libra_sample2 = LIBRASample([sample3, sample4], "01/02/2023 12:00 PM")

    # Create GasStream instance
    libra_run = GasStream([libra_sample1, libra_sample2], "01/01/2023 12:00 PM")

    # Test cumulative activity
    cumulative_activity = libra_run.get_cumulative_activity()
    assert cumulative_activity.magnitude.tolist() == [30, 100]
    assert cumulative_activity.units == ureg.Bq


def test_get_cumulative_activity_without_background_subtracted():
    # Create sample activities
    activity1 = 10 * ureg.Bq
    activity2 = 20 * ureg.Bq

    # Create LSCSample instances
    sample1 = LSCSample(activity1, "Sample1")
    sample2 = LSCSample(activity2, "Sample2")

    # Create LIBRASample instance
    libra_sample = LIBRASample([sample1, sample2], "01/01/2023 12:00 PM")

    # Create GasStream instance
    libra_run = GasStream([libra_sample], "01/01/2023 12:00 PM")

    # Test cumulative activity without background subtracted
    with pytest.raises(
        ValueError,
        match="Background must be substracted before calculating cumulative activity",
    ):
        libra_run.get_cumulative_activity()


def test_relative_times():
    # Create LSCSample instances
    sample1 = LSCSample(10 * ureg.Bq, "Sample1")
    sample2 = LSCSample(20 * ureg.Bq, "Sample2")

    # Create LIBRASample instances
    libra_sample1 = LIBRASample([sample1], "01/02/2023 12:00 PM")
    libra_sample2 = LIBRASample([sample2], "01/03/2023 12:00 PM")

    # Create GasStream instance
    start_time = "01/01/2023 12:00 PM"
    libra_run = GasStream([libra_sample1, libra_sample2], start_time)

    # Test relative times
    relative_times = libra_run.relative_times
    assert relative_times == [
        datetime.strptime("01/02/2023 12:00 PM", "%m/%d/%Y %I:%M %p")
        - datetime.strptime(start_time, "%m/%d/%Y %I:%M %p"),
        datetime.strptime("01/03/2023 12:00 PM", "%m/%d/%Y %I:%M %p")
        - datetime.strptime(start_time, "%m/%d/%Y %I:%M %p"),
    ]
