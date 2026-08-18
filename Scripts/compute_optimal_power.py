"""
Computes pump hydraulic power for each heat load's optimal (minimum-power,
thermally-safe) operating point, and saves the result.

Inputs:
    results/full_sweep_final.csv       (from sweep_pump_speed.py)
    results/optimization_results.csv   (from optimize.py)

Output:
    results/optimal_power.csv          (one row per heat load, with pump power)
"""

import pandas as pd

RHO_WATER = 1000  # kg/m^3

SWEEP_PATH = r'S:\Projects\datacenter_cooling\results\final_data.csv'
OPT_PATH = r'S:\Projects\datacenter_cooling\results\optimization_results.csv'
OUT_PATH = r'S:\Projects\datacenter_cooling\results\optimal_power.csv'

sweep_df = pd.read_csv(SWEEP_PATH)
opt_df = pd.read_csv(OPT_PATH)

results = []

for _, row in opt_df.iterrows():
    heat = row['heat_load_W']

    if row['status'] != 'OK':
        results.append({
            'heat_load_W': heat,
            'optimal_speed_rad_s': None,
            'cpu_temp_K': None,
            'pump_power_W': None,
            'status': row['status']
        })
        continue

    speed = row['optimal_speed_rad_s']

    # Find the matching row in the full sweep for this exact (heat, speed) pair
    match = sweep_df[
        (sweep_df['heat_load_W'] == heat) &
        (sweep_df['pump_speed_rad_s'] == speed)
    ]

    if match.empty:
        print(f"Warning: no matching sweep row for heat={heat}W, speed={speed} rad/s")
        continue

    match = match.iloc[0]

    delta_p_Pa = match['pump_pressure_out'] - match['pump_pressure_in']
    volumetric_flow_m3s = match['flow_rate_kg_s'] / RHO_WATER
    pump_power_W = delta_p_Pa * volumetric_flow_m3s

    results.append({
        'heat_load_W': heat,
        'optimal_speed_rad_s': speed,
        'cpu_temp_K': round(match['cpu_temp_K'], 2),
        'delta_p_Pa': round(delta_p_Pa, 2),
        'flow_rate_kg_s': round(match['flow_rate_kg_s'], 5),
        'pump_power_W': round(pump_power_W, 4),
        'status': 'OK'
    })

out_df = pd.DataFrame(results)
print(out_df.to_string(index=False))

out_df.to_csv(OUT_PATH, index=False)
print(f"\nSaved to {OUT_PATH}")
