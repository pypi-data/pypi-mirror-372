# %%
import uwacan
geod = uwacan.positional.geod
import numpy as np
import plotly.graph_objects as go
import folium
5

from importlib import reload
reload(uwacan.positional)
hydrophone_position = uwacan.positional.Position.from_degrees_minutes_seconds(57, 35.424, 11, 48.350)
# %%
import gpxpy
path = 'c:/Users/carl4189/OneDrive - IVL Svenska Miljöinstitutet AB/Elvy maj 22/GPS-data/GPS1_dag.gpx'
file = open(path, 'r')
contents = gpxpy.parse(file)
latitudes = []
longitudes = []
times = []
for point in contents.get_points_data():
    latitudes.append(point.point.latitude)
    longitudes.append(point.point.longitude)
    times.append(point.point.time)

# %%
track = uwacan.positional.GPXTrack('c:/Users/carl4189/OneDrive - IVL Svenska Miljöinstitutet AB/Elvy maj 22/GPS-data/GPS1_dag.gpx')

# %%
track = uwacan.positional.Blueflow('c:/Users/carl4189/OneDrive - IVL Svenska Miljöinstitutet AB/Elvy maj 22/Blueflow/Blueflow data Elvy 17 maj.xlsx')

# %%

m = folium.Map(location=[np.mean(track.latitude), np.mean(track.longitude)], zoom_start=13, control_scale=True)
folium.PolyLine(
    np.stack([track.latitude, track.longitude], axis=1),
    weight=1,
    lineCap='bevel',
    color='red'
).add_to(m)
display.display(m)

# %%
subtrack = track[40:50]
revtrack = reversed(subtrack)
list(revtrack)
# %%
start_idx = 3100
track_len = 400
stop_idx = start_idx + track_len
subtrack = track[start_idx:stop_idx]
# latitude = track.latitude[start_idx:stop_idx]
# longitude = track.longitude[start_idx:stop_idx]
# pos = np.stack([subtrack.latitude, subtrack.longitude], axis=1)
# times = [(t - track.time.timestamps[start_idx]).total_seconds() for t in track.time.timestamps[start_idx:stop_idx]]
times = subtrack.track_time

time_windows = subtrack.aspect_windows(hydrophone_position, 5, 45, 100, None)

m = folium.Map(location=subtrack.mean.coordinates, zoom_start=15, control_scale=True)
folium.PolyLine(
    subtrack.coordinates.transpose(),
    weight=1,
    lineCap='bevel',
    color='red'
).add_to(m)
folium.Marker(hydrophone_position.coordinates, popup='hydrophone').add_to(m)
for idx, window in enumerate(time_windows):
    start_pos = subtrack[window.start]
    stop_pos = subtrack[window.stop]
    print(f'{idx = }: {hydrophone_position.angle_between(start_pos, stop_pos)} degrees, {start_pos.distance_to(stop_pos)} meters')
    folium.Marker(start_pos.coordinates, icon=folium.Icon(color='green', icon='marker'), tooltip=f'{idx}', popup=str(start_pos)).add_to(m)
    folium.Marker(stop_pos.coordinates, icon=folium.Icon(color='red', icon='marker'), tooltip=f'{idx}', popup=str(stop_pos)).add_to(m)
folium.Marker(subtrack.closest_point(hydrophone_position).coordinates, icon=folium.Icon(color='blue', icon='marker'), tooltip=f'cpa').add_to(m)
display.display(m)

# %%
subtrack[window.start]
# %%
blueflow_heading = track.data['Heading [deg]'].iloc[start_idx:stop_idx].to_numpy()
# blueflow_speed = uwacan.positional.speed_conversion(knots=track.blueflow['Speed over ground [kts]'].iloc[start_idx:stop_idx].to_numpy())
blueflow_speed = track.data['Speed over ground [kts]'].iloc[start_idx:stop_idx].to_numpy() / uwacan.positional.one_knot
headings = []
speeds = []
for (early_lat, early_lon), (late_lat, late_lon), early_t, late_t in zip(pos[:-1], pos[1:], times[:-1], times[1:]):
    outs = geod.Inverse(early_lat, early_lon, late_lat, late_lon, outmask=geod.AZIMUTH | geod.DISTANCE)
    headings.append(outs['azi2'])
    speeds.append(outs['s12'] / (late_t - early_t))

go.Figure([go.Scatter(y=blueflow_heading), go.Scatter(y=headings)]).show()
go.Figure([go.Scatter(y=blueflow_speed), go.Scatter(y=speeds)]).show()

# %%

duration = 260
sampling_interval = 2
jitter = 1
n_samples = round(duration / sampling_interval)
time = np.arange(n_samples) * sampling_interval + np.random.normal(size=n_samples, scale=jitter)
time -= time[0]
time = np.insert(time, 4, time[4])

latitude = np.random.normal(size=time.shape, scale=0.5) + np.linspace(-1, 1, time.size) ** 2 + 58
longitude = np.random.normal(size=time.shape, scale=0.5) + np.linspace(11.4, 12, time.size)

# %%
track = uwacan.positional.Track(latitude=latitude, longitude=longitude, time=time)
# %%
track.resample(0.25).smooth(20)
# %%
go.Figure([
    go.Scatter(x=track.time, y=track.longitude, mode='lines'),
    go.Scatter(x=track.resample.time, y=track.resample.longitude, mode='lines'),
    go.Scatter(x=track.resample.smooth.time, y=track.resample.smooth.longitude, mode='lines'),
])
# %%
