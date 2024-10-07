import pytest
import math
from adaptive_curve import AdaptiveCurveIrm


@pytest.fixture
def irm():
    return AdaptiveCurveIrm()


def test_constants(irm):
    assert 1 * irm.WAD <= irm.CURVE_STEEPNESS <= 100 * irm.WAD
    assert 0 <= irm.ADJUSTMENT_SPEED <= 1000 * irm.WAD // irm.SECONDS_PER_YEAR
    assert 0 < irm.TARGET_UTILIZATION < irm.WAD
    assert irm.MIN_RATE_AT_TARGET <= irm.INITIAL_RATE_AT_TARGET <= irm.MAX_RATE_AT_TARGET


def test_first_borrow_rate_utilization_zero(irm):
    rate = irm.borrow_rate(0, irm.WAD, 0)
    expected_rate = irm.INITIAL_RATE_AT_TARGET // 4
    assert math.isclose(rate, expected_rate, rel_tol=1e-4)
    assert irm.rate_at_target == irm.INITIAL_RATE_AT_TARGET


def test_first_borrow_rate_utilization_one(irm):
    rate = irm.borrow_rate(irm.WAD, irm.WAD, 0)
    expected_rate = irm.INITIAL_RATE_AT_TARGET * 4
    assert math.isclose(rate, expected_rate, rel_tol=1e-4)
    assert irm.rate_at_target == irm.INITIAL_RATE_AT_TARGET


def test_rate_after_utilization_one(irm):
    irm.borrow_rate(0, irm.WAD, 0)

    first_rate = irm.borrow_rate(
        0, irm.WAD, 365 * 24 * 60 * 60 * 2) * irm.SECONDS_PER_YEAR / irm.WAD
    expected_rate = irm.INITIAL_RATE_AT_TARGET // 4 * irm.SECONDS_PER_YEAR / irm.WAD
    assert math.isclose(first_rate, expected_rate, rel_tol=0.1)

    irm.last_update = 365 * 24 * 60 * 60 * 2 - 5 * 24 * 60 * 60
    rate = irm.borrow_rate(irm.WAD, irm.WAD, 365 * 24 *
                           60 * 60 * 2) * irm.SECONDS_PER_YEAR / irm.WAD
    expected_rate = irm.INITIAL_RATE_AT_TARGET * 4 * \
        14361 // 10000 * irm.SECONDS_PER_YEAR / irm.WAD
    assert math.isclose(rate, expected_rate, rel_tol=0.1)
    assert math.isclose(rate, 0.22976, rel_tol=0.1)


def test_rate_after_utilization_zero(irm):
    irm.borrow_rate(irm.WAD, irm.WAD, 365 * 24 * 60 * 60 * 2)

    rate = irm.borrow_rate(0, irm.WAD, 365 * 24 * 60 *
                           60 * 2 + 5 * 24 * 60 * 60)
    expected_rate = irm.INITIAL_RATE_AT_TARGET // 4 * 724 // 1000
    assert math.isclose(rate, expected_rate, rel_tol=0.1)
    assert math.isclose(rate, 0.00724 * irm.WAD //
                        irm.SECONDS_PER_YEAR, rel_tol=0.1)


def test_rate_after_45_days_utilization_above_target_no_ping(irm):
    irm.borrow_rate(irm.TARGET_UTILIZATION, irm.WAD, 1)
    assert irm.rate_at_target == irm.INITIAL_RATE_AT_TARGET

    rate = irm.borrow_rate(
        (irm.TARGET_UTILIZATION + irm.WAD) // 2, irm.WAD, 1+45 * 24 * 60 * 60) * irm.SECONDS_PER_YEAR / irm.WAD
    rate_at_target = irm.rate_at_target * irm.SECONDS_PER_YEAR / irm.WAD
    expected_rate = 0.04 * math.exp(50 * 45 / 365 * 0.5)
    assert math.isclose(rate_at_target, expected_rate, rel_tol=0.005)


def test_rate_after_45_days_utilization_above_target_ping_every_minute(irm):
    irm.borrow_rate(irm.TARGET_UTILIZATION, irm.WAD, 1)
    assert irm.rate_at_target == irm.INITIAL_RATE_AT_TARGET

    initial_borrow_assets = (irm.TARGET_UTILIZATION + irm.WAD) // 2
    total_supply_assets = irm.WAD
    current_time = 1

    for _ in range(45 * 24 * 60):
        rate = irm.borrow_rate(initial_borrow_assets,
                               total_supply_assets, 1+current_time)
        interest = initial_borrow_assets * \
            irm.wTaylorCompounded(rate, 60) // irm.WAD
        initial_borrow_assets += interest
        total_supply_assets += interest
        current_time += 60

    utilization = initial_borrow_assets * irm.WAD // total_supply_assets
    assert math.isclose(utilization / irm.WAD, 0.95, rel_tol=0.01)

    expected_rate = int(0.8722 * irm.WAD) // irm.SECONDS_PER_YEAR
    assert irm.rate_at_target >= expected_rate
    assert math.isclose(irm.rate_at_target / irm.WAD,
                        expected_rate / irm.WAD, rel_tol=0.08)

    growth = initial_borrow_assets * \
        irm.WAD // ((irm.TARGET_UTILIZATION + irm.WAD) // 2)
    expected_growth = int(1.457 * irm.WAD)
    assert math.isclose(
        growth / irm.WAD, expected_growth / irm.WAD, rel_tol=0.3)


def test_rate_after_utilization_target_no_ping(irm):
    irm.borrow_rate(irm.TARGET_UTILIZATION, irm.WAD, 0)
    assert irm.rate_at_target == irm.INITIAL_RATE_AT_TARGET

    elapsed = 365 * 24 * 60 * 60  # 1 year
    irm.borrow_rate(irm.TARGET_UTILIZATION, irm.WAD, elapsed)
    assert irm.rate_at_target == irm.INITIAL_RATE_AT_TARGET


def test_ge_min_rate_at_target(irm):
    rate = irm.borrow_rate(9 * irm.WAD // 10, irm.WAD, 0)
    assert rate >= irm.MIN_RATE_AT_TARGET // irm.CURVE_STEEPNESS


def test_le_max_rate_at_target(irm):
    rate = irm.borrow_rate(9 * irm.WAD // 10, irm.WAD, 0)
    assert rate <= irm.MAX_RATE_AT_TARGET * irm.CURVE_STEEPNESS // irm.WAD
