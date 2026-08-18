import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv(r'S:\Projects\datacenter_cooling\results\final_data.csv')

THERMAL_LIMIT_K = 368.15  # 95°C

fig, ax = plt.subplots(figsize=(10, 6))

heat_loads = sorted(df['heat_load_W'].unique())
colors = plt.cm.viridis_r([i / len(heat_loads) for i in range(len(heat_loads))])

for heat, color in zip(heat_loads, colors):
    subset = df[df['heat_load_W'] == heat].sort_values('pump_speed_rad_s')
    ax.plot(subset['pump_speed_rad_s'], subset['cpu_temp_K'],
            marker='o', label=f'{heat} W', color=color)

ax.axhline(THERMAL_LIMIT_K, color='red', linestyle='--', linewidth=1.5,
           label=f'Thermal Limit ({THERMAL_LIMIT_K:.1f} K / {THERMAL_LIMIT_K-273.15:.0f}°C)')

ax.set_xlabel('Pump Speed (rad/s)')
ax.set_ylabel('Steady-State CPU Temperature (K)')
ax.set_title('CPU Temperature vs. Pump Speed Across Heat Loads')
ax.legend(title='CPU Heat Load')
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(r'S:\Projects\datacenter_cooling\results\tradeoff_plot.png', dpi=200)
plt.show()

print("Plot saved to results/tradeoff_plot.png")