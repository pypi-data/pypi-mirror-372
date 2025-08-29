import pytest
import numpy as np
from libra_toolbox.tritium.plotting import plot_bars
from libra_toolbox.tritium.lsc_measurements import LIBRASample, GasStream, LSCSample
from libra_toolbox.tritium import ureg

import matplotlib.pyplot as plt


@pytest.fixture
def sample_measurements():
    samples = [
        LIBRASample(
            samples=[
                LSCSample(activity=1 * ureg.Bq, name="Sample 1A"),
                LSCSample(activity=1.1 * ureg.Bq, name="Sample 1B"),
                LSCSample(activity=1.2 * ureg.Bq, name="Sample 1C"),
                LSCSample(activity=1.3 * ureg.Bq, name="Sample 1D"),
            ],
            time="11/8/2024 4:20 PM",
        ),
        LIBRASample(
            samples=[
                LSCSample(activity=2 * ureg.Bq, name="Sample 2A"),
                LSCSample(activity=2.1 * ureg.Bq, name="Sample 2B"),
                LSCSample(activity=2.2 * ureg.Bq, name="Sample 2C"),
                LSCSample(activity=2.3 * ureg.Bq, name="Sample 2D"),
            ],
            time="11/8/2024 4:21 PM",
        ),
        LIBRASample(
            samples=[
                LSCSample(activity=3 * ureg.Bq, name="Sample 3A"),
                LSCSample(activity=3.1 * ureg.Bq, name="Sample 3B"),
                LSCSample(activity=3.2 * ureg.Bq, name="Sample 3C"),
                LSCSample(activity=3.3 * ureg.Bq, name="Sample 3D"),
            ],
            time="11/8/2024 4:22 PM",
        ),
        LIBRASample(
            samples=[
                LSCSample(activity=4 * ureg.Bq, name="Sample 4A"),
                LSCSample(activity=4.1 * ureg.Bq, name="Sample 4B"),
                LSCSample(activity=4.2 * ureg.Bq, name="Sample 4C"),
                LSCSample(activity=4.3 * ureg.Bq, name="Sample 4D"),
            ],
            time="11/8/2024 4:23 PM",
        ),
    ]
    return samples


@pytest.fixture
def sample_run(sample_measurements):
    return GasStream(samples=sample_measurements, start_time="11/7/2024 4:20 PM")


def test_plot_bars_with_samples(sample_measurements):
    plt.figure()
    index = plot_bars(sample_measurements)
    assert len(index) == len(sample_measurements)
    plt.close()


def test_plot_bars_with_run(sample_run):
    plt.figure()
    index = plot_bars(sample_run)
    assert len(index) == len(sample_run.samples)
    plt.close()


def test_plot_bars_with_dict():
    measurements = {
        "sample1": [0, 1 * ureg.Bq, 2 * ureg.Bq, 3 * ureg.Bq, 4 * ureg.Bq],
        "sample2": [0, 2 * ureg.Bq, 3 * ureg.Bq, 4 * ureg.Bq, 5 * ureg.Bq],
    }
    plt.figure()
    index = plot_bars(measurements)
    assert len(index) == len(measurements)
    plt.close()


def test_plot_bars_stacked(sample_measurements):
    plt.figure()
    index = plot_bars(sample_measurements, stacked=True)
    assert len(index) == len(sample_measurements)
    plt.close()


def test_plot_bars_not_stacked(sample_measurements):
    plt.figure()
    index = plot_bars(sample_measurements, stacked=False)
    assert len(index) == len(sample_measurements)
    plt.close()
