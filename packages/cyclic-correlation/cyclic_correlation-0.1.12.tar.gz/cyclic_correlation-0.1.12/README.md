# Cyclic Correlation Module

This module provides functions to compute the cyclic cross-correlation between two 1D signals using either FFT-based or analytic methods, and to generate Zadoff-Chu sequences. It supports automatic input validation, optional zero-padding, and normalization.

**Current version:** 0.1.12

## Features

- **Input validation**: Ensures signals are 1D and compatible in length.
- **Flexible methods**: Choose between `"fft"` (fast) and `"analytic"` (direct computation).
- **Padding/truncation**: Automatically pads or truncates signals to match lengths if needed.
- **Normalization**: Optionally normalizes the correlation output.
- **Zadoff-Chu sequence generation**: Generate ZC sequences for communication applications.

## Functions

### `cyclic_corr(s1, s2, method="fft", wrt="short", normalized=True, ccwindow=0, shift=0)`

Computes the cyclic cross-correlation between signals `s1` and `s2`.

#### Parameters

- `s1`, `s2`: 1D lists or numpy arrays (input signals).
- `method`: `"fft"` (default) or `"analytic"`.
- `wrt`: `"short"` (default) or `"long"`; specifies the correlation window reference.
- `normalized`: If `True`, normalizes the correlation output.
- `ccwindow`: If >0, sets the length of the correlation window (default 0, meaning full).
- `shift`: If >0, shifts the window start index.

#### Returns

- `Z`: Cyclic cross-correlation array.
- `max_val`: Maximum absolute value of the correlation.
- `t_max`: Index of the maximum correlation.
- `min_val`: Minimum absolute value of the correlation.

### `check_inputs_define_limits(s1, s2, method, wrt, normalized=True, ccwindow=0, shift=0)`

Validates and prepares input signals for correlation computation.

### `ZC_sequence(r, q, N)`

Generates a discrete Zadoff-Chu (ZC) sequence.

#### Parameters

- `r` (int): Root index of the ZC sequence. Must satisfy 1 <= r <= N.
- `q` (int): Cyclic shift of the sequence. Must satisfy q >= 0.
- `N` (int): Length of the sequence. Must satisfy N >= 1.

#### Returns

- `numpy.ndarray`: The generated Zadoff-Chu sequence of length N.

#### Example

```python
from cyclic_correlation import ZC_sequence

zc = ZC_sequence(r=1, q=0, N=13)
print("Zadoff-Chu sequence:", zc)
```

## Example

```python
from cyclic_correlation import cyclic_corr

s1 = [1, 2, 3, 4]
s2 = [4, 3, 2, 1]
Z, max_val, t_max, min_val = cyclic_corr(s1, s2, method="fft", wrt="short", normalized=True)
print("Correlation:", Z)
print("Max value:", max_val)
print("Index of max:", t_max)
print("Min value:", min_val)
```

## Requirements

- numpy

## License

BSD-3-Clause