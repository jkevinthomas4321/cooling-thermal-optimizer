import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv(r'S:\Projects\datacenter_cooling\results\final_data.csv')

RHO_WATER = 1000  # kg/m^3

# Pressure rise across the pump
df['delta_p_Pa'] = df['pump_pressure_out'] - df['pump_pressure_in']

# Volumetric flow rate
df['volumetric_flow_m3s'] = df['flow_rate_kg_s'] / RHO_WATER

# Hydraulic pump power
df['pump_power_W'] = df['delta_p_Pa'] * df['volumetric_flow_m3s']

print(df[['heat_load_W', 'pump_speed_rad_s', 'delta_p_Pa', 'pump_power_W']].head(15))

# --- Plot: Pump Power vs Pump Speed ---
# (Power depends only on speed/flow, not heat load, since the fluid side
#  is independent of the thermal side in this model — so this should
#  collapse to a single curve, not one per heat load)

fig, ax = plt.subplots(figsize=(8, 6))

# Use just one heat load's rows since pump power should be identical across all of them
single_load = df[df['heat_load_W'] == df['heat_load_W'].unique()[0]].sort_values('pump_speed_rad_s')

ax.plot(single_load['pump_speed_rad_s'], single_load['pump_power_W'],
        marker='o', color='darkorange')

ax.set_xlabel('Pump Speed (rad/s)')
ax.set_ylabel('Pump Hydraulic Power (W)')
ax.set_title('Pump Power vs. Pump Speed')
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(r'S:\Projects\datacenter_cooling\results\pump_power_plot.png', dpi=200)
plt.show()

print("\nSaved to results/pump_power_plot.png")

# Save updated CSV with power column included
df.to_csv(r'S:\Projects\datacenter_cooling\results\final_data_with_power.csv', index=False)
print("Saved updated CSV with power calculations.")