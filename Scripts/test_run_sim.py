import matlab.engine
import numpy as np

# --- Start MATLAB engine ---
eng = matlab.engine.start_matlab()

# --- Point to your model's folder (UPDATE THIS PATH) ---
eng.cd(r'S:\Projects\datacenter_cooling\models', nargout=0)

model_name = 'server_cooling_loop_v2_working'  
eng.load_system(model_name, nargout=0)
print(f"Model '{model_name}' loaded successfully.")

# --- Force To Workspace variables into the base workspace ---
# (Newer MATLAB versions bundle logged signals into a simOut object by
# default; this setting reverts to the classic behavior where variables
# from 'To Workspace' blocks land directly in the base workspace.)
eng.set_param(model_name, 'ReturnWorkspaceOutputs', 'off', nargout=0)

# --- Set stop time (model needs ~350s to fully settle) ---
eng.set_param(model_name, 'StopTime', '400', nargout=0)

# --- Run the simulation ---
print("Running simulation...")
eng.sim(model_name, nargout=0)
print("Simulation complete.")

# --- Diagnostic: list everything currently in the base workspace ---
print("Variables in MATLAB base workspace:")
print(eng.eval("who", nargout=1))

# --- Extract logged data ---
cpu_temp_values = np.array(eng.eval("cpu_temp_out.Data", nargout=1))
cpu_temp_time = np.array(eng.eval("cpu_temp_out.Time", nargout=1))
flow_rate_values = np.array(eng.eval("flow_rate_out.Data", nargout=1))

# --- Steady-state values = last recorded sample ---
final_cpu_temp = cpu_temp_values[-1][0]
final_flow_rate = flow_rate_values[-1][0]

print(f"Final CPU Temp: {final_cpu_temp:.2f} K")
print(f"Final Flow Rate: {final_flow_rate:.4f} kg/s")

# --- Cleanup ---
eng.close_system(model_name, 0, nargout=0)
eng.quit()