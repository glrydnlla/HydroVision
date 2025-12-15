import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import streamlit as st
import io
import imageio

def get_uv(u0, v0, a, b, x_grid, y_grid):
  # print(x_grid[0], " ", x_grid[-1])
  # print(u0 * (1 + a * x_grid[-1]))
  u = np.zeros((len(x_grid), len(y_grid)))
  v = np.zeros((len(x_grid), len(y_grid)))

  for y in range(len(y_grid)):
    for x in range(len(x_grid)):
      u[x, y] = u0 * (1 + a * x_grid[x])

  for x in range(len(x_grid)):
    for y in range(len(y_grid)):
      v[x, y] = v0 * (1 + b * y_grid[y])
  print(f"u max = {u.max()}")
  return u, v


def get_pr(P0, R0, a, b, x_grid, y_grid):
  P = np.zeros((len(x_grid), len(y_grid)))
  R = np.zeros((len(x_grid), len(y_grid)))

  for y in range(len(y_grid)):
    for x in range(len(x_grid)):
      P[x, y] = P0 * ((1 + a * x_grid[x])**2)

  for x in range(len(x_grid)):
    for y in range(len(y_grid)):
      R[x, y] = R0 * ((1 + b * y_grid[y])**2)

  return P, R

def get_delta_t(u, v, delta_x, delta_y, P, R):
    u_max = u.max() # m/s
    v_max = v.max() # m/s
    P_max = P.max() # m/s
    R_max = R.max() # m/s

    # Stabilitas advective
    denom_adv = (abs(u_max)/delta_x) + (abs(v_max)/delta_y)
    dt_adv = 1.0 / denom_adv if denom_adv > 0 else float('inf')

    # Stabilitas diffusive
    dt_diff = 0.5 / (P_max / delta_x**2 + R_max / delta_y**2)

    # Pilih timestep yang aman
    dt_max = min(dt_adv, dt_diff)

    print(u_max)
    print(v_max)
    print(dt_max)
    return dt_max

def check_stability(u, v, P, R, delta_x, delta_y, delta_t):
    u_max = abs(u.max())
    v_max = abs(v.max())
    P_max = P.max()
    R_max = R.max()

    # Advection CFL check
    CFL = delta_t * (u_max/delta_x + v_max/delta_y)
    advective_stable = CFL <= 1.0

    # Diffusion check
    dt_diff_limit = 0.5 / (P_max / delta_x**2 + R_max / delta_y**2)
    diffusive_stable = delta_t <= dt_diff_limit

    return advective_stable and diffusive_stable, CFL, dt_diff_limit

def apply_bc(c, t):
    c[t, -1, :] = c[t, -2, :] # x = m
    c[t, :, 0] = c[t, :, 1] # y = 0
    c[t, :, -1] = c[t, :, -2] # y = n
    return c

def cs_1_x(var, delta_x):
    return (var[2:,1:-1] - var[0:-2,1:-1]) / (2*delta_x)

def cs_1_y(var, delta_y):
    return (var[1:-1,2:] - var[1:-1,0:-2]) / (2*delta_y)

def cs_2_x(var, delta_x):
    return (var[2:,1:-1] - 2*var[1:-1,1:-1] + var[0:-2,1:-1]) / (delta_x**2)

def cs_2_y(var, delta_y):
    return (var[1:-1,2:] - 2*var[1:-1,1:-1] + var[1:-1,0:-2]) / (delta_y**2)

def get_x_y_input(x, x0, y, y0, xt, yt):
    nearest_x_to_target_idx = (np.abs(x - x0)).argmin()
    nearest_y_to_target_idx = (np.abs(y - y0)).argmin()

    if (nearest_x_to_target_idx==0):
        nearest_x_to_target_idx += 1
    if (nearest_x_to_target_idx==len(x)-1):
        nearest_x_to_target_idx -= 1

    if (nearest_y_to_target_idx==0):
        nearest_y_to_target_idx += 1
    if (nearest_y_to_target_idx==len(y)-1):
        nearest_y_to_target_idx -= 1

    nearest_x_to_target = x[nearest_x_to_target_idx]
    nearest_y_to_target = y[nearest_y_to_target_idx]

    nearest_xt_to_target_idx = (np.abs(x - xt)).argmin()
    nearest_yt_to_target_idx = (np.abs(y - yt)).argmin()

    if (nearest_xt_to_target_idx==0):
        nearest_xt_to_target_idx += 1
    if (nearest_xt_to_target_idx==len(x)-1):
        nearest_xt_to_target_idx -= 1

    if (nearest_yt_to_target_idx==0):
        nearest_yt_to_target_idx += 1
    if (nearest_yt_to_target_idx==len(y)-1):
        nearest_yt_to_target_idx -= 1

    nearest_xt_to_target = x[nearest_xt_to_target_idx]
    nearest_yt_to_target = y[nearest_yt_to_target_idx]

    return nearest_x_to_target, nearest_y_to_target, nearest_x_to_target_idx, nearest_y_to_target_idx, nearest_xt_to_target, nearest_yt_to_target, nearest_xt_to_target_idx, nearest_yt_to_target_idx

def get_meshgrid(c, delta_x, delta_y):
    nx, ny = c.shape[1], c.shape[2]

    x = 0 + np.arange(nx) * delta_x
    y = 0 + np.arange(ny) * delta_y

    X, Y = np.meshgrid(x, y, indexing='ij')

    return x, y, X, Y

def analyze(t, c, P, R, u, v, delta_x, delta_y, delta_t, xt, yt):
    print(delta_x, " ", delta_y, " ", delta_t, " ", xt, " ", yt)
    c_history = []
    c_x_history = {}
    c_history = []
    c_history.append(c[0, xt, yt])
    print("c history at ", xt, yt, c[0, xt, yt])
    c_x_profile = c[0, :, yt].copy()  # ambil semua x di y tertentu
    c_x_history[0] = c_x_profile
    for k in range(1, t+1):
        apply_bc(c, k)
        RHS = (cs_1_x(P, delta_x) *  cs_1_x(c[k-1], delta_x) +
                P[1:-1,1:-1] * cs_2_x(c[k-1], delta_x) +
                cs_1_y(R, delta_y) * cs_1_y(c[k-1], delta_y) +
                R[1:-1,1:-1] * cs_2_y(c[k-1], delta_y) -
                c[k-1][1:-1,1:-1] * cs_1_x(u, delta_x) -
                u[1:-1,1:-1] * cs_1_x(c[k-1], delta_x) -
                c[k-1][1:-1,1:-1] * cs_1_y(v, delta_y) -
                v[1:-1,1:-1] * cs_1_y(c[k-1], delta_y))
        c[k, 1:-1, 1:-1] = c[k-1, 1:-1, 1:-1] + delta_t * RHS
        c_history.append(c[k, xt, yt])
        c_x_profile = c[k, :, yt].copy()  # ambil semua x di y tertentu
        c_x_history[k] = c_x_profile
        # print(c[k])
        apply_bc(c, k)
        if (k%1000==0):
            print(f"Step {k}: c.min={c[k].min()}, c.max={c[k].max()}")
    return c, c_history, c_x_history
  

def concentration_at_target_point(t, delta_t, c_history, xt, yt):
    time_points = np.arange(0, t+1) * delta_t
    max_concentration = np.max(c_history)
    max_concentration_idx = c_history.index(max_concentration)
    print("len c history", len(c_history))
    fig = plt.figure(figsize=(8, 6))
    print("t*delta t", t*delta_t, "time point trakhir", time_points[-1])
    plt.plot(time_points, c_history, marker='o')
    plt.xlabel('Time (s)')
    plt.ylabel('Concentration at target')
    plt.title(f'Concentration Evolution at Target Point ({round(xt,2)}, {round(yt,2)})')
    plt.grid(True)
    return fig, max_concentration, max_concentration_idx, time_points[max_concentration_idx], delta_t, time_points[-1]

def concentration_at_y_across_x(c_x_history, x, yt):
    fig = plt.figure(figsize=(8, 6))
    len_c = len(c_x_history)
    # print(c_history)
    t_plot = len_c - 1
    t_print_list = [int(t_plot * frac) for frac in [0.25, 0.5, 0.75, 1]]
    for t_idx in (t_print_list):
        # if (t_idx < 5):
        plt.plot(x[:-1], c_x_history[t_idx][:-1], label=f't = {t_idx}')

    plt.xlabel('x (m)')
    plt.ylabel('Concentration')
    plt.title(f'Concentration Evolution across X at y = {round(yt,2)}')
    plt.legend()
    plt.grid(True)
    return fig

def export_gif(fig, frames, fps=10, progress=None):
    images = []
    total = len(frames)
    for i, frame in enumerate(frames):
        fig.update(data=frame.data)
        png_bytes = fig.to_image(format="png")
        img = imageio.v3.imread(png_bytes)
        images.append(img)
        if progress is not None:
            progress.progress((i + 1) / total)
    gif_bytes = io.BytesIO()
    imageio.mimsave(gif_bytes, images, fps=fps, format="GIF")
    gif_bytes.seek(0)
    return gif_bytes

def show_animation(c, dt_max, x_grid, y_grid):
    st.markdown(
        """
        <style>
            .plotly .updatemenu-button:hover rect {
                fill: var(--secondary-background-color) !important;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    t = c.shape[0]
    ny, nx = c.shape[1], c.shape[2]
    zmax_val = np.max(c)
    frames = [
        go.Frame(
            data=[go.Heatmap(
                z=np.rot90(np.flipud(c[k]), k=-1),
                colorscale='Inferno',
                zmin=0,
                zmax=zmax_val
                # zmax=np.percentile(c, 99)
            )],
            name=f"t={k * dt_max:.2f}s"
        )
        for k in range(t)
    ]

    fig = go.Figure(
        data=[go.Heatmap(
            z=np.rot90(np.flipud(c[0]), k=-1),
            colorscale='Inferno',
            zmin=0,
            zmax=zmax_val
            # zmax=np.percentile(c, 99)
        )],
        frames=frames
    )

    fig.update_layout(
        paper_bgcolor="var(--secondary-background-color)",
        plot_bgcolor="var(--secondary-background-color)",
        font=dict(color="var(--text-color)"),
        title_font=dict(color="var(--text-color)")
    )

    fig.update_layout(
        title="Pollutant Dispersion Simulation",
        width=700,
        height=600,
        xaxis_title='X (m)',
        yaxis_title='Y (m)',
        updatemenus=[{
            "buttons": [
                {"args": [None, {"frame": {"duration": 1000 * dt_max, "redraw": True},
                                 "fromcurrent": True, "mode": "immediate"}],
                 "label": "Play",
                 "method": "animate"},
                {"args": [[None], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate"}],
                 "label": "Pause",
                 "method": "animate"}
            ],
            "type": "buttons",
            "bgcolor": "var(--secondary-background-color)",
            "font": {"color": "var(--text-color)"},
            "x": 0.05,
            "y": -0.05
        }],
        sliders=[{
            "steps": [
                {"args": [[f"t={k * dt_max:.2f}s"],
                          {"frame": {"duration": 0, "redraw": True}}],
                 "label": f"{k * dt_max:.2f}s",
                 "method": "animate"}
                for k in range(t)
            ],
            "x": 0.1,
            "y": -0.1,
            "len": 0.9,
            "currentvalue": {"prefix": "Time: "}
        }]
    )
    # st.plotly_chart(fig, width='content')
    step = 10
    fig.update_xaxes(
        tickmode="array",
        tickvals=list(range(0, nx, step)),
        ticktext=[f"{x_grid[i]:.2f}" for i in range(0, nx, step)]
    )
    fig.update_yaxes(
        tickmode="array",
        tickvals=list(range(0, ny, step)),
        ticktext=[f"{y_grid[::-1][i]:.2f}" for i in range(0, ny, step)]
    )


    html_buf = io.BytesIO()
    html_buf.write(fig.to_html().encode('utf-8'))
    html_buf.seek(0)

    return fig, html_buf, frames

