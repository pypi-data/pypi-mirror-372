fig = uwacan.visualization.make_chart(center=uwacan.positional.position(latitude_grid.mean(), longitude_grid.mean()), zoom=10)
# fig.add_scattermapbox(lat=[], lon=[])
# fig.add_densitymapbox(
#     lat=np.meshgrid(latitude_grid, longitude_grid, indexing='ij')[0].flatten(),
#     lon=np.meshgrid(latitude_grid, longitude_grid, indexing='ij')[1].flatten(),
#     z=mean_speed.flatten(),
#     radius=5
# )
fig.update_layout(margin={'r': 0.2, 'l': 0.1, 't': 0.1, 'b': 0.1})
colormap = pco.convert_colors_to_same_type(pco.sequential.Viridis, 'rgb')[0].copy()
colormap[0] = 'rgba(' + colormap[0].split('(')[1].split(')')[0] + ', 0.0)'
colormap[1] = 'rgba(' + colormap[1].split('(')[1].split(')')[0] + ', 0.3)'

max_speed = np.max(mean_speed)
max_speed = 12
max_counts = np.max(num_detected)
max_counts = 5000
speed_choices = np.linspace(0, max_speed, 25)
color_choices = pco.sample_colorscale('viridis', speed_choices.size)
def make_color(speed, counts):
    # color = pco.sample_colorscale('viridis', speed / max_speed)[0]
    color = color_choices[np.argmin(np.abs(speed - speed_choices))]
    opacity = (np.clip(counts / max_counts, 0, 1))**0.1
    return 'rgba(' + color.split('(')[1].split(')')[0] + f', {opacity:.6f})'
colors = [
    make_color(s, c)
    for (s, c) in zip(mean_speed.flatten(), num_detected.flatten())
]

fig.add_scattermapbox(
    lat=np.meshgrid(latitude_grid, longitude_grid, indexing='ij')[0].flatten(),
    lon=np.meshgrid(latitude_grid, longitude_grid, indexing='ij')[1].flatten(),
    marker=dict(
        # color=np.where(num_detected > 0, mean_speed, np.nan).flatten(),
        # color=mean_speed.flatten(),
        # cmin=0, cmax=10,
        # colorscale=colormap,
        color = colors,
    ),
    mode='markers',
)
# fig.update_layout(
#   paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
#     # xaxis2=dict(overlaying='x'),
#     # yaxis2=dict(overlaying='y'),
#     xaxis=dict(overlaying='x2'),
#     yaxis=dict(overlaying='y2'),
# )
# colormap = pco.sequential.Viridis

# fig.add_heatmap(
#     x=longitude_grid,
#     y=latitude_grid,
#     z=np.where(num_detected > 0, mean_speed, np.nan),
#     xaxis='x2', yaxis='y2',
#     # opacity=num_detected / np.max(num_detected)
# )
fig.show()