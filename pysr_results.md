# Phase 3: Symbolic Regression Results (PySR)

We applied evolutionary symbolic regression to discover closed-form analytical formulas for Unity CPU and GPU inference latency.

## Targets & Features
- **Target**: `log(t+1)` where `t` is inference time in milliseconds.
- **Features**: `Flog` (log FLOPs), `Plog` (log Parameters), `L` (Total Layers).

## Discovered Equations
- **CPU Latency Equation**: `log(t_cpu + 1) = log(0.15827991*L)`
- **GPU Latency Equation**: `log(t_gpu + 1) = exp(Plog*0.10758593)`

## Interpretation
These equations demonstrate that inference latency is non-linear and device-heterogeneous. The GPU and CPU require qualitatively different mathematical models to capture their bottlenecks.
