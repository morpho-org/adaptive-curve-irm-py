import math
from functools import lru_cache


class AdaptiveCurveIrm:
    WAD = 10**18
    SECONDS_PER_YEAR = 365 * 24 * 60 * 60

    def __init__(self):
        # Constants (converted to %/year)
        self.CURVE_STEEPNESS = 4 * self.WAD
        self.ADJUSTMENT_SPEED = 50 * self.WAD // self.SECONDS_PER_YEAR
        self.TARGET_UTILIZATION = 9 * self.WAD // 10
        self.INITIAL_RATE_AT_TARGET = 4 * self.WAD // 100 // self.SECONDS_PER_YEAR
        self.MIN_RATE_AT_TARGET = self.WAD // 1000 // self.SECONDS_PER_YEAR
        self.MAX_RATE_AT_TARGET = 2 * self.WAD // self.SECONDS_PER_YEAR

        # State variables
        self.rate_at_target = self.INITIAL_RATE_AT_TARGET
        self.last_update = 0

    @lru_cache(maxsize=1000)
    def borrow_rate(self, total_borrow_assets: int, total_supply_assets: int, current_time: int) -> int:
        utilization = total_borrow_assets * \
            self.WAD // total_supply_assets if total_supply_assets > 0 else 0

        err_norm_factor = self.WAD - \
            self.TARGET_UTILIZATION if utilization > self.TARGET_UTILIZATION else self.TARGET_UTILIZATION
        err = (utilization - self.TARGET_UTILIZATION) * \
            self.WAD // err_norm_factor

        start_rate_at_target = self.rate_at_target

        if self.last_update == 0:
            avg_rate_at_target = self.INITIAL_RATE_AT_TARGET
            end_rate_at_target = self.INITIAL_RATE_AT_TARGET
        else:
            speed = self.ADJUSTMENT_SPEED * err // self.WAD
            elapsed = (current_time - self.last_update)
            linear_adaptation = speed * elapsed

            if linear_adaptation == 0:
                avg_rate_at_target = start_rate_at_target
                end_rate_at_target = start_rate_at_target
            else:
                end_rate_at_target = self._new_rate_at_target(
                    start_rate_at_target, linear_adaptation)
                mid_rate_at_target = self._new_rate_at_target(
                    start_rate_at_target, linear_adaptation // 2)
                avg_rate_at_target = (
                    start_rate_at_target + end_rate_at_target + 2 * mid_rate_at_target) // 4

        self.rate_at_target = end_rate_at_target
        self.last_update = current_time

        return self._curve(avg_rate_at_target, err)

    def _curve(self, rate_at_target: int, err: int) -> int:
        coeff = self.WAD - self.WAD * \
            self.WAD // self.CURVE_STEEPNESS if err < 0 else self.CURVE_STEEPNESS - self.WAD
        return ((coeff * err // self.WAD + self.WAD) * rate_at_target) // self.WAD

    def _new_rate_at_target(self, start_rate_at_target: int, linear_adaptation: int) -> int:
        new_rate = start_rate_at_target * \
            self._w_exp(linear_adaptation) // self.WAD
        return max(min(new_rate, self.MAX_RATE_AT_TARGET), self.MIN_RATE_AT_TARGET)

    def _w_exp(self, x: int) -> int:
        LN_2_INT = 693147180559945309  # ln(2) * WAD
        LN_WEI_INT = -41446531673892822312  # ln(1e-18) * WAD
        # ln(type(int256).max / 1e36) * WAD
        WEXP_UPPER_BOUND = 93859467695000404319
        # wExp(WEXP_UPPER_BOUND)
        WEXP_UPPER_VALUE = 57716089161558943949701069502944508345128422502756744429568

        if x < LN_WEI_INT:
            return 0
        if x >= WEXP_UPPER_BOUND:
            return WEXP_UPPER_VALUE

        rounding_adjustment = -LN_2_INT // 2 if x < 0 else LN_2_INT // 2
        q = (x + rounding_adjustment) // LN_2_INT
        r = x - q * LN_2_INT

        exp_r = self.WAD + r + (r * r) // self.WAD // 2

        if q >= 0:
            return exp_r << q
        else:
            return exp_r >> (-q)

    def wTaylorCompounded(self, x: int, n: int) -> int:
        first_term = x * n
        second_term = (first_term * first_term) // (2 * self.WAD)
        third_term = (second_term * first_term) // (3 * self.WAD)

        return first_term + second_term + third_term