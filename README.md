# Adaptive Curve IRM Python Implementation

## Overview

This repository contains a Python implementation of the Adaptive Curve Interest Rate Model (IRM) that performs exactly the same computations as its Solidity counterpart.
The main purpose of this project is to provide a Python-based tool for simulating and testing the Adaptive Curve IRM outside of the Ethereum blockchain environment.

## Key Features

1. **Identical Computation**: The Python implementation mirrors the Solidity version, ensuring that the interest rate calculations are consistent across both platforms.

2. **AdaptiveCurveIrm Class**: The core functionality is encapsulated in the `AdaptiveCurveIrm` class, which includes all the necessary methods and constants for interest rate calculations.

3. **MathLib Class**: Implementation of arithmetic operations that should behave similarly to the Solidity implementation.

4. **Precision Handling**: The implementation uses integer arithmetic and scaling factors (WAD) to maintain the same level of precision as the Solidity version, avoiding floating-point discrepancies.

5. **Key Methods**:
   - `borrow_rate`: Calculates the borrow rate based on total borrow assets, total supply assets, and current time.
   - `_curve`: Implements the interest rate curve calculation.
   - `_new_rate_at_target`: Calculates the new rate at target utilization.
   - `_w_exp`: A custom exponential function implementation for integer math.

6. **Visualization**: Includes a method to plot borrow rates over time using matplotlib.

7. **Test Suite**: Comprehensive test cases in `test_adaptive_curve_irm.py` to verify the correctness of the implementation.

## Usage

The script can be run standalone to simulate interest rate behavior:
```
python adaptive_curve.py
```


This will generate a series of random market states and calculate corresponding interest rates, then plot the results.

## Testing

To run the test suite:

```
pytest test_adaptive_curve_irm.py
```


## Dependencies

- Python 3.x
- matplotlib (for visualization)
- pytest (for running tests)

## Note

This Python implementation is designed for simulation and testing purposes.
For actual deployment of the Adaptive Curve IRM, please refer to the official Solidity implementation.
Don't hesitate to raise an issue if you find any bug in this implementation.
