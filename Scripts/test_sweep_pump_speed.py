import matlab.engine
import numpy as np
import pandas as pd

eng = matlab.engine.start_matlab()
eng.cd(r'S:\Projects\datacenter_cooling\models', nargout=0)

model_name = 'server_cooling_loop_v2_working'
eng.load_system(model_name, nargout=0)
eng.set_param(model_name, 'ReturnWorkspaceOutputs', 'off', nargout=0)
eng.set_param(model_name, 'StopTime', '400', nargout=0)

block_path = f'{model_name}/mech_input'

# --- Test sweep ---
speed_values = [50, 75, 100, 125, 150, 175, 200, 250, 300, 350]  # rad/s

results = []

for speed in speed_values:
    print(f"\nRunning at pump speed = {speed} rad/s...")

    # Write new pump speed into the model
    eng.set_param(block_path, 'constant', str(speed), nargout=0)

    # Run simulation
    eng.sim(model_name, nargout=0)

    # Extract results
    cpu_temp_values = np.array(eng.eval("cpu_temp_out.Data", nargout=1))
    flow_rate_values = np.array(eng.eval("flow_rate_out.Data", nargout=1))

    final_cpu_temp = cpu_temp_values[-1][0]
    final_flow_rate = flow_rate_values[-1][0]

    print(f"  -> CPU Temp: {final_cpu_temp:.2f} K | Flow Rate: {final_flow_rate:.4f} kg/s")

    results.append({
        'pump_speed_rad_s': speed,
        'cpu_temp_K': final_cpu_temp,
        'flow_rate_kg_s': final_flow_rate
    })

eng.close_system(model_name, 0, nargout=0)
eng.quit()

# --- Save results ---
df = pd.DataFrame(results)
print("\n--- Sweep Results ---")
print(df)

df.to_csv(r'S:\Projects\datacenter_cooling\results\pump_speed_sweep_test.csv', index=False)
print("\nSaved to results/pump_speed_sweep_test.csv")