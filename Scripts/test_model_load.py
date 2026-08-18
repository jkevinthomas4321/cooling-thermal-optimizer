import matlab.engine

eng = matlab.engine.start_matlab()

# Point this to your model's folder
eng.cd(r'S:\Projects\datacenter_cooling\models', nargout=0)

model_name = 'server_cooling_loop_v2_working'  # no .slx extension
eng.load_system(model_name, nargout=0)
print(f"Model '{model_name}' loaded successfully.")

eng.close_system(model_name, 0, nargout=0)  # 0 = don't save
eng.quit()