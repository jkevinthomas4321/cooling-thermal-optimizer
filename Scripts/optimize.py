import pandas as pd

df = pd.read_csv(r'S:\Projects\datacenter_cooling\results\full_sweep_final.csv')

RHO_WATER = 1000
THERMAL_LIMIT_K = 368.15

df['delta_p_Pa'] = df['pump_pressure_out'] - df['pump_pressure_in']
df['volumetric_flow_m3s'] = df['flow_rate_kg_s'] / RHO_WATER
df['pump_power_W'] = df['delta_p_Pa'] * df['volumetric_flow_m3s']

results = []

for heat in sorted(df['heat_load_W'].unique()):
    subset = df[df['heat_load_W'] == heat].sort_values('pump_speed_rad_s')
    
    # Filter to only speeds that satisfy the thermal constraint
    feasible = subset[subset['cpu_temp_K'] <= THERMAL_LIMIT_K]
    
    if feasible.empty:
        results.append({
            'heat_load_W': heat,
            'status': 'NO FEASIBLE SPEED FOUND',
            'optimal_speed_rad_s': None,
            'cpu_temp_K': None,
            'pump_power_W': None
        })
    else:
        # Among feasible options, pick the one with minimum pump power
        best = feasible.loc[feasible['pump_power_W'].idxmin()]
        results.append({
            'heat_load_W': heat,
            'status': 'OK',
            'optimal_speed_rad_s': best['pump_speed_rad_s'],
            'cpu_temp_K': round(best['cpu_temp_K'], 2),
            'pump_power_W': round(best['pump_power_W'], 3)
        })

opt_df = pd.DataFrame(results)
print(opt_df.to_string(index=False))

opt_df.to_csv(r'S:\Projects\datacenter_cooling\results\optimization_results.csv', index=False)
print("\nSaved to results/optimization_results.csv")