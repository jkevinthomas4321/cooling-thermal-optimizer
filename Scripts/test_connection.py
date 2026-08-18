import matlab.engine

print("Starting MATLAB engine...")
eng = matlab.engine.start_matlab()
print("Connected.")

result = eng.sqrt(16.0)
print(f"Test calculation (sqrt of 16): {result}")

eng.quit()