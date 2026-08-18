import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv(r'S:\Projects\datacenter_cooling\results\full_sweep_final.csv')
opt_df = pd.read_csv(r'S:\Projects\datacenter_cooling\results\optimization_results.csv')

RHO_WATER = 1000
THERMAL_LIMIT_K = 368.15

df['delta_p_Pa'] = df['pump_pressure_out'] - df['pump_pressure_in']
df['volumetric_flow_m3s'] = df['flow_rate_kg_s'] / RHO_WATER
df['pump_power_W'] = df['delta_p_Pa'] * df['volumetric_flow_m3s']

fig, ax = plt.subplots(figsize=(10, 6))

heat_loads = sorted(df['heat_load_W'].unique())
colors = plt.cm.viridis_r([i / len(heat_loads) for i in range(len(heat_loads))])

for heat, color in zip(heat_loads, colors):
    subset = df[df['heat_load_W'] == heat].sort_values('pump_speed_rad_s')
    ax.plot(subset['pump_speed_rad_s'], subset['cpu_temp_K'],
            marker='o', label=f'{heat} W', color=color)

    # Mark the optimal point for this heat load
    opt_row = opt_df[opt_df['heat_load_W'] == heat].iloc[0]
    if opt_row['status'] == 'OK':
        ax.scatter(opt_row['optimal_speed_rad_s'], opt_row['cpu_temp_K'],
                   s=200, facecolors='none', edgecolors=color, linewidths=2.5, zorder=5)

ax.axhline(THERMAL_LIMIT_K, color='red', linestyle='--', linewidth=1.5,
           label=f'Thermal Limit ({THERMAL_LIMIT_K:.1f} K / {THERMAL_LIMIT_K-273.15:.0f}°C)')

ax.set_xlabel('Pump Speed (rad/s)')
ax.set_ylabel('Steady-State CPU Temperature (K)')
ax.set_title('CPU Cooling Trade-off: Temperature vs. Pump Speed\n(circled points = minimum-power feasible operating point)')
ax.legend(title='CPU Heat Load', loc='upper right')
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(r'S:\Projects\datacenter_cooling\results\final_plot.png', dpi=200)
plt.show()

print("Saved final annotated plot.")