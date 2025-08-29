from libra_toolbox.tritium.model import (
    activity_to_quantity,
    quantity_to_activity,
    SPECIFIC_ACT,
    MOLAR_MASS,
    ureg,
)

import pytest


@pytest.mark.parametrize(
    "units", [None, ureg.Bq, ureg.Ci, ureg.Bq / ureg.g, ureg.Ci / ureg.L]
)
@pytest.mark.parametrize("activity", [0, 1e-2, 0.5, 1, 2])
def test_activity_to_quantity(activity, units):
    if units:
        activity = activity * units
    assert activity_to_quantity(activity) == activity / (SPECIFIC_ACT * MOLAR_MASS)
    if units:
        assert activity_to_quantity(activity).dimensionality != activity.dimensionality


@pytest.mark.parametrize("units", [None, ureg.g, ureg.mol, ureg.kg, ureg.mol / ureg.L])
@pytest.mark.parametrize("quantity", [0, 1e-2, 0.5, 1, 2])
def test_quantity_to_activity(quantity, units):
    if units:
        quantity = quantity * units
    assert quantity_to_activity(quantity) == quantity * (SPECIFIC_ACT * MOLAR_MASS)
    if units:
        assert quantity_to_activity(quantity).dimensionality != quantity.dimensionality
