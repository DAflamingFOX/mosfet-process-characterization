# mosfet-process-characterization

Extracting simple MOSFET model variables from a complex model file.

See my [blog](https://blog.jeff-m.com) for a detailed walkthrough of this process.

Results from demo file:

```
========================================
Processing NMOS
========================================
k'       = 107.564 µA/V^2
V_T0     = 983.833 mV
2phi_F   = 914.761 mV
gamma    = 1.104 V^1/2
lambda_1 = 1.566 V^−1 (L = 300.00 nm)
lambda_2 = 228.343 mV^−1 (L = 500.00 nm)
lambda_3 = 99.304 mV^−1 (L = 1.00 µm)
lambda_4 = 76.922 mV^−1 (L = 1.50 µm)
lambda_5 = 62.114 mV^−1 (L = 2.00 µm)

========================================
Processing PMOS
========================================
k'       = 33.094 µA/V^2
V_T0     = −1.034 V
2phi_F   = 811.851 mV
gamma    = 717.640 mV^1/2
lambda_1 = 662.718 mV^−1 (L = 300.00 nm)
lambda_2 = 285.793 mV^−1 (L = 500.00 nm)
lambda_3 = 120.081 mV^−1 (L = 1.00 µm)
lambda_4 = 77.865 mV^−1 (L = 1.50 µm)
lambda_5 = 57.474 mV^−1 (L = 2.00 µm)
```