import numpy as np
from pawlabeling.settings import configuration

def interpolate_time_series(data, length=100):
    from scipy import interpolate
    x = np.arange(0, len(data))
    f = interpolate.interp1d(x, data, bounds_error=False)
    x_new = np.linspace(0, len(data)-1, num=length)
    data_new = f(x_new)
    return data_new

def calculate_cop(data, version="scipy"):
    if version == "scipy":
        return calculate_cop_scipy(data)
    elif version == "numpy":
        return calculate_cop_numpy(data)

def calculate_cop_numpy(data):
    y, x, z = np.shape(data)
    cop_x = np.zeros(z, dtype=np.float32)
    cop_y = np.zeros(z, dtype=np.float32)

    x_coordinate, y_coordinate = np.arange(x), np.arange(y)
    temp_x, temp_y = np.zeros(y), np.zeros(x)
    for frame in range(z):
        #print frame, np.sum(data[:, :, frame])
        if np.sum(data[:, :, frame]) > 0.0: # Else divide by zero
            # This can be rewritten as a vector calculation
            for col in range(y):
                temp_x[col] = np.sum(data[col, :, frame] * x_coordinate)
            for row in range(x):
                temp_y[row] = np.sum(data[:, row, frame] * y_coordinate)
            # np.divide should guard against divide by zero
            cop_x[frame] = np.divide(np.sum(temp_x), np.sum(data[:, :, frame]))
            cop_y[frame] = np.divide(np.sum(temp_y), np.sum(data[:, :, frame]))
    return cop_x, cop_y

def calculate_cop_scipy(data):
    from scipy.ndimage.measurements import center_of_mass
    y, x, z = np.shape(data)
    cop_x = np.zeros(z, dtype=np.float32)
    cop_y = np.zeros(z, dtype=np.float32)
    for frame in range(z):
        if np.sum(data[:,:,frame]) > 0:
            # While it may seem odd, x and y are mixed up, must be my own fault
            y, x = center_of_mass(data[:, :, frame])
            # This used to say + 1, but I can't image that's necessary
            cop_x[frame] = x
            cop_y[frame] = y
    return cop_x, cop_y

def force_over_time(data):
    return np.sum(np.sum(data, axis=0), axis=0)

def pixel_count_over_time(data):
    x, y, z = data.shape
    return np.array([np.count_nonzero(data[:, :, frame]) for frame in range(z)])

def surface_over_time(data):
    pixel_counts = pixel_count_over_time(data)
    return[p_c * configuration.sensor_surface for p_c in pixel_counts]

def pressure_over_time(data):
    force = force_over_time(data)
    pixel_counts = pixel_count_over_time(data)
    surface = [p_c * configuration.sensor_surface for p_c in pixel_counts]
    return np.divide(force, surface)


