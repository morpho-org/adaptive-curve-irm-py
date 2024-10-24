class MathLib:
    # Define WAD constant as 10^18

    WAD = int(1e18)  # Since Python doesn't need separate int/uint types

    @staticmethod
    def w_mul_down(x: int, y: int) -> int:
        """Returns (x * y) / WAD rounded down."""
        return MathLib.mul_div_down(x, y, MathLib.WAD)

    @staticmethod
    def w_div_down(x: int, y: int) -> int:
        """Returns (x * WAD) / y rounded down."""
        return MathLib.mul_div_down(x, MathLib.WAD, y)

    @staticmethod
    def w_div_up(x: int, y: int) -> int:
        """Returns (x * WAD) / y rounded up."""
        return MathLib.mul_div_up(x, MathLib.WAD, y)

    @staticmethod
    def mul_div_down(x: int, y: int, d: int) -> int:
        """Returns (x * y) / d rounded down."""
        return (x * y) // d

    @staticmethod
    def mul_div_up(x: int, y: int, d: int) -> int:
        """Returns (x * y) / d rounded up."""
        return (x * y + (d - 1)) // d

    @staticmethod
    def w_taylor_compounded(x: int, n: int) -> int:
        """
        Returns the sum of the first three non-zero terms of a Taylor expansion of e^(nx) - 1,
        to approximate a continuous compound interest rate.
        """
        first_term = x * n
        second_term = MathLib.mul_div_down(
            first_term, first_term, 2 * MathLib.WAD)
        third_term = MathLib.mul_div_down(
            second_term, first_term, 3 * MathLib.WAD)
        return first_term + second_term + third_term

    @staticmethod
    def w_mul_to_zero(x: int, y: int) -> int:
        """
        Returns the multiplication of x by y (in WAD) rounded towards 0.

        Args:
            x (int): First number
            y (int): Second number

        Returns:
            int: Result of (x * y) / WAD rounded towards 0
        """
        return (x * y) // MathLib.WAD  # Using integer division '//' for rounding towards 0

    @staticmethod
    def w_div_to_zero(x: int, y: int) -> int:
        """
        Returns the division of x by y (in WAD) rounded towards 0.

        Args:
            x (int): Numerator
            y (int): Denominator (must not be 0)

        Returns:
            int: Result of (x * WAD) / y rounded towards 0

        Raises:
            ZeroDivisionError: If y is 0
        """
        if y == 0:
            raise ZeroDivisionError("Division by zero")
        return (x * MathLib.WAD) // y
