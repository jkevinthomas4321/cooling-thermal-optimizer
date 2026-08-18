# 🖥️ Server Cooling Loop — Thermal Optimization Digital Twin

![MATLAB](https://img.shields.io/badge/MATLAB-R2024a-orange)
![Simscape](https://img.shields.io/badge/Simscape-Physical%20Modeling-blue)
![Python](https://img.shields.io/badge/Python-3.11-green)
![Status](https://img.shields.io/badge/status-complete-brightgreen)

A validated Simscape thermal-fluid model of a liquid-cooled server, driven end-to-end by Python (`matlab.engine`) to automatically find the **minimum pump power that keeps a CPU thermally safe** — across a range of heat loads.

<p align="center">
  <img src="results/final_tradeoff_plot.png" width="700">
</p>

---

## TL;DR

- Built a coupled fluid + thermal Simscape model of a pump → cold plate → CPU loop
- Validated every stage against hand calculations (energy balance, transient response, pump laws)
- Automated a 55-run parameter sweep (pump speed × CPU heat load) via `matlab.engine`
- Built an optimizer that finds the minimum-power operating point per heat load, subject to a thermal safety constraint
- **Result:** across all tested heat loads (40–150 W), the design has enough thermal margin that the pump's own minimum valid speed — not CPU temperature — is the binding constraint

---

## The Problem

| Lever | Effect |
|---|---|
| ⬆️ Pump speed | Better cooling, but power cost rises **~cubically** |
| ⬇️ Pump speed | Saves power, but risks thermal throttling |

**Question this project answers:** for a given CPU heat load, what's the slowest (cheapest) pump speed that still keeps the CPU under its thermal limit?

---

## System Model

```
Reservoir (1.5 bar) → Centrifugal Pump → Pipe → Cold Plate ⇄ CPU Thermal Mass → Pipe → Reservoir (1.0 bar)
                                                     ▲
                                          Heat Flow Source (CPU load, W)
```

- **Fluid domain:** pump, pipes, coolant chamber (Simscape Thermal Liquid)
- **Thermal domain:** CPU heat generation + thermal mass (Simscape Thermal)
- **Coupling:** `Q = h·A·(T_cpu − T_coolant)`, with **h flow-dependent** — not a fixed constant (see below)

---

## Key Physics

**Governing equation** (CPU thermal mass, lumped capacitance):

```
m·cp·(dT/dt) = Q_in − Q_out          Q_out = h·A·(T_cpu − T_coolant)
```

**Steady state:** `T_cpu = T_coolant + Q / (h·A)`
**Transient:** first-order exponential, `τ = m·cp / (h·A)`

**Why h had to be flow-dependent:** a fixed `h` made pump speed nearly irrelevant to CPU temperature — no real trade-off existed. Modeled instead as:

```
h = C · ṁ^0.8     (Dittus–Boelter-style turbulent convection scaling)
```

`C` was calibrated against a literature-realistic `h` at a representative flow rate — and **recalibrated** after switching pump types (see [Debugging Notes](#debugging-notes--engineering-decisions)).

| Parameter | Value |
|---|---|
| CPU heat load range | 40 – 150 W |
| Cold-plate contact area | 0.002 m² |
| CPU + cold-plate mass | 0.08 kg, cp = 900 J/(kg·K) |
| Pipe diameter | 8 mm |
| Thermal safety limit | 368.15 K (95 °C) |

---

## Validation

Every stage was checked against hand calculations before automating anything:

| Check | Method | Result |
|---|---|---|
| Transient response | Step input, compared to exponential charging curve | Matched within simulation resolution |
| Steady-state balance | `T = T_coolant + Q/(hA)` at 3 heat loads | Within ~1% |
| Pump flow law | `V̇ = D·N` (fixed-displacement pump) | Within 0.2% |

---

## Automation

```python
eng.set_param(f'{model}/mech_input', 'constant', str(pump_speed), nargout=0)
eng.set_param(f'{model}/heat_flow', 'Before', str(heat_load), nargout=0)
eng.set_param(f'{model}/heat_flow', 'After', str(heat_load), nargout=0)
eng.sim(model, nargout=0)
cpu_temp = np.array(eng.eval("cpu_temp_out.Data", nargout=1))[-1][0]
```

Python drives MATLAB headlessly through **55 simulations** (11 pump speeds × 5 heat loads), logging results to `results/full_sweep_final.csv`.

---

## Results

| Heat Load | Optimal Speed | CPU Temp | Pump Power |
|---|---|---|---|
| 40 W  | 40 rad/s | 309.7 K | ~4.7 W |
| 65 W  | 40 rad/s | 320.1 K | ~4.7 W |
| 90 W  | 40 rad/s | 330.4 K | ~4.7 W |
| 115 W | 40 rad/s | 340.8 K | ~4.7 W |
| 150 W | 40 rad/s | 355.3 K | ~4.7 W |

Every curve shows clear **diminishing returns** (consistent with `h ∝ ṁ^0.8`), while pump power grows near-cubically with speed — the two curves together are the entire trade-off story.

---

## Debugging Notes & Engineering Decisions

The value of this project is as much in the debugging as the final model:

- **Cross-sectional area mismatch** silently broke pump/pipe pressure continuity at compile time — traced to a default `0.01 m²` port area vs. an actual `5×10⁻⁵ m²` pipe.
- **Missing mechanical reference** on the pump's shaft port caused flow rate to stop responding to speed entirely — no error thrown, just silently wrong physics.
- **Wrong coupling block:** `Pipe (TL)` is adiabatic in this Simscape version — no thermal port exists. Correct component was `Constant Volume Chamber (TL)` + a separate `Convective Heat Transfer` block.
- **Constant h masked the entire optimization problem** — confirmed via a controlled flow-rate sweep before fixing it, not assumed.
- **Pump swap required recalibration:** switching fixed-displacement → centrifugal pump increased flow ~10–50×, invalidating the original `h` correlation's calibration range.
- **Invalid low-speed pump region** (< 33 rad/s): centrifugal pump produced negative pressure rise — identified via a `Δp` sign check and excluded from the final dataset.

---

## Limitations & Future Work

- No heat load in the tested range was thermally binding — a higher-load or lower-speed sweep would find a real thermal constraint
- `h` correlation is calibrated, not CFD-derived
- Open-loop reservoir pair, not a closed recirculating loop
- Constant (not time-varying) heat load per run

---

## Repository Structure

```
├── models/                    server_cooling_loop_v2_working.slx
├── scripts/                   sweep_pump_speed.py · optimize.py · plot_final_tradeoff.py
├── results/                   full_sweep_final.csv · optimization_results.csv · final_tradeoff_plot.png
└── README.md
```

## Run It

```bash
python scripts/sweep_pump_speed.py     # full 55-point sweep
python scripts/optimize.py             # find minimum-power feasible points
python scripts/plot_final_tradeoff.py  # generate the annotated plot
```

Requires Python 3.11 (MATLAB R2024a's `matlab.engine` compatibility) and the MATLAB Engine API for Python installed in your environment.

---

*B.E. Mechanical Engineering · M.Sc. Process, Energy & Environmental Systems Engineering, TU Berlin · Python QA Automation background*
