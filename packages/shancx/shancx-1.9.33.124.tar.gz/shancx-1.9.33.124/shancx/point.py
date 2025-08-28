import numpy as np
from scipy.interpolate import griddata
def getPoint(field,lats=None,lons=None,obs_lats=None,obs_lons=None):
    lon_mesh, lat_mesh = np.meshgrid(lons, lats)
    grid_points = np.column_stack([lon_mesh.ravel(), lat_mesh.ravel()])
    interp_values = griddata(grid_points, field.ravel(), (obs_lons, obs_lats), method='linear')
    valid_mask = ~np.isnan(interp_values)
    return interp_values[valid_mask]
"""
nlat, nlon = background.shape
lons = np.linspace(-180, 180, nlon, endpoint=False)
lats = np.linspace(90, -90, nlat)
obs_lats = df["lat"]
obs_lons = df["lon"]
"""  