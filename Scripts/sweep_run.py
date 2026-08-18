import matlab.engine
import numpy as np
import pandas as pd

eng = matlab.engine.start_matlab()
eng.cd(r'S:\Projects\datacenter_cooling\models', nargout=0)

model_name = 'server_cooling_loop_v2_working'
eng.load_system(model_name, nargout=0)
eng.set_param(model_name, 'ReturnWorkspaceOutputs', 'off', nargout=0)
eng.set_param(model_name, 'StopTime', '400', nargout=0)

pump_block_path = f'{model_name}/mech_input'
heat_block_path = f'{model_name}/heat_flow'

#speed_values = [50, 75, 100, 125, 150, 175, 200, 250, 300, 350]  # rad/s - we found 50 is the optimal angular velocity in this set of values
#optimizing further with lower speed values
#speed_values_opt = list(range(30,37,1)) - found that pump produces positive pressure above 33rad/s

speed_values = [40, 60, 80, 100, 125, 150, 175, 200, 250, 300, 350]  # rad/s
heat_values = [40, 65, 90, 115, 150]  # Watts

results = []
total_runs = len(speed_values) * len(heat_values)
run_count = 0

for heat in heat_values:
    eng.set_param(heat_block_path, 'Time', '0', nargout=0)
    eng.set_param(heat_block_path, 'Before', str(heat), nargout=0)
    eng.set_param(heat_block_path, 'After', str(heat), nargout=0)

    for speed in speed_values:
        run_count += 1
        print(f"Run {run_count}/{total_runs}: speed={speed} rad/s, heat={heat} W...")

        eng.set_param(pump_block_path, 'constant', str(speed), nargout=0)
        eng.sim(model_name, nargout=0)

        cpu_temp_values = np.array(eng.eval("cpu_temp_out.Data", nargout=1))
        flow_rate_values = np.array(eng.eval("flow_rate_out.Data", nargout=1))
        pump_pressure_in_values = np.array(eng.eval("pump_pressure_in.Data", nargout=1))
        pump_pressure_out_values = np.array(eng.eval("pump_pressure_out.Data", nargout=1))

        final_cpu_temp = cpu_temp_values[-1][0]
        final_flow_rate = flow_rate_values[-1][0]
        pump_pressure_in = pump_pressure_in_values[-1][0]
        pump_pressure_out = pump_pressure_out_values[-1][0]

        print(f"  -> CPU Temp: {final_cpu_temp:.2f} K | Flow Rate: {final_flow_rate:.4f} kg/s")

        results.append({
            'heat_load_W': heat,
            'pump_speed_rad_s': speed,
            'cpu_temp_K': final_cpu_temp,
            'flow_rate_kg_s': final_flow_rate,
            'pump_pressure_in' : pump_pressure_in,
            'pump_pressure_out' : pump_pressure_out
        })

eng.close_system(model_name, 0, nargout=0)
eng.quit()

df = pd.DataFrame(results)
print("\n--- Full Sweep Results ---")
print(df)

df.to_csv(r'S:\Projects\datacenter_cooling\results\full_sweep_test.csv', index=False)
print("\nSaved to results/full_sweep_test.csv")