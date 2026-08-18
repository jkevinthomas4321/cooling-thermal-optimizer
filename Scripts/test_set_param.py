import matlab.engine

eng = matlab.engine.start_matlab()
eng.cd(r'S:\Projects\datacenter_cooling\models', nargout=0)

model_name = 'server_cooling_loop_v2_working'
eng.load_system(model_name, nargout=0)

# Path to your Constant block driving pump speed
block_path = f'{model_name}/mech_input'

# Set a new value (e.g., 200 rad/s)
eng.set_param(block_path, 'constant', '200', nargout=0)
print("Pump speed set to 200 rad/s.")

# Confirm it actually took effect by reading it back
current_value = eng.get_param(block_path, 'constant')
print(f"Confirmed value in model: {current_value}")

eng.close_system(model_name, 0, nargout=0)
eng.quit()