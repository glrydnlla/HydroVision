import streamlit as st
import numpy as np

from simulation import (
    get_uv, get_pr, 
    get_delta_t, 
    check_stability,
    get_meshgrid, 
    get_x_y_input,
    analyze, 
    concentration_at_target_point, 
    concentration_at_y_across_x, 
    show_animation,
    export_gif
)
import tutorial
import ui
import io
from datetime import datetime

st.set_page_config(page_title="HydroVision", layout="wide")

st.markdown(
    """
    <style>
    h1 a, h3 a {
        display: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)


ui.init_app_state()
tutorial.init_tutorial_state()

if not st.session_state.welcome_shown:
    ui.render_welcome()
else:
    ui.show_sidebar_menu()

    if st.session_state.show_tutorial:
        tutorial.render_tutorial_modal()

    page = st.session_state.current_page

    if page == "Analyze":
        st.title("Analyze")
        st.write("You can click the Show Tutorial button to display the tutorial and parameter explanation.")
        params = ui.render_input_panel()
        ss3 = "\u00B3"
        st.write("")

        if st.button("Analyze and Run Simulation", use_container_width=True, type="primary"):
            if "animation_gif" in st.session_state:
                del st.session_state["animation_gif"]
            grid_x = int(params['grid_x'])
            grid_y = int(params['grid_y'])
            t = int(params['t'])
            c = np.zeros((t+1, grid_x, grid_y))
            delta_x = params['len_x'] / (grid_x-1)
            delta_y = params['len_y'] / (grid_y-1)
            x, y, X, Y = get_meshgrid(c, delta_x, delta_y)
            
            u, v = get_uv(params['u0'], params['v0'], params['a'], params['b'], x, y)
            P, R = get_pr(params['P0'], params['R0'], params['a'], params['b'], x, y)

            delta_t = get_delta_t(u, v, delta_x, delta_y, P, R)
            print("delta t =", delta_t)

            stable, CFL, dt_diff_limit = check_stability(u, v, P, R, delta_x, delta_y, delta_t)

            # advection = """
            #                 Advection (Courant–Friedrichs–Lewy condition):
            #                     |u| Δt / Δx  +  |v| Δt / Δy  ≤  1"""

            # diffusion = """
            #                 Diffusion stability:
            #                     Δt  ≤  1 / ( 2 * ( P/Δx²  +  R/Δy² ) )"""

            advection = " |u|·Δt/Δx  +  |v|·Δt/Δy  ≤  1 "
            diffusion = " Δt ≤ 1 / ( 2·(P/Δx² + R/Δy²) ) "

            if not stable:
                st.error(f"Computed delta_t is unstable with the CFL value of {CFL} and delta t limit of {dt_diff_limit}. Adjust parameters. You can refer to the advection and diffusion stability formula below.\n\nAdvection (Courant–Friedrichs–Lewy condition):\n\n\t{advection}\n\nDiffusion stability:\n\n\t{diffusion}")
                st.session_state.analyzed = False
            else:
                c[0, :, :] = np.ones_like(c[0, :, :]) * params.get('c_in', 0.1)
                xt = params['xt']
                yt = params['yt']
                x_in_coordinate, y_in_coordinate, x_in, y_in, xt_coordinate, yt_coordinate, xt_idx, yt_idx = get_x_y_input(x, params['x0'], y, params['y0'], xt, yt)
                c[0, x_in, y_in] = (params['m'] / params['Q'])
                print(f"concentration at {x_in} {y_in}", c[0, x_in, y_in])
                c, c_history, c_x_history = analyze(t, c, P, R, u, v, delta_x, delta_y, delta_t, xt_idx, yt_idx)
                fig1, max_concentration, max_concentration_idx, max_concentration_t, delta_t, end_time = concentration_at_target_point(t, delta_t, c_history, xt_coordinate, yt_coordinate)
                buf1 = io.BytesIO()
                fig1.savefig(buf1, format="png")
                buf1.seek(0)
                fig2 = concentration_at_y_across_x(c_x_history, x, yt_coordinate)
                buf2 = io.BytesIO()
                fig2.savefig(buf2, format="png")
                buf2.seek(0)
                st.session_state.analyzed = True

                st.session_state.xi = params['x0']
                st.session_state.yi = params['y0']
                st.session_state.xi_coordinate = x_in_coordinate
                st.session_state.yi_coordinate = y_in_coordinate

                st.session_state.xt = xt
                st.session_state.yt = yt
                st.session_state.grid_x = grid_x
                st.session_state.grid_y = grid_y

                st.session_state.fig1 = fig1
                st.session_state.max_concentration = max_concentration
                st.session_state.max_concentration_idx = max_concentration_idx
                st.session_state.max_concentration_t = max_concentration_t
                st.session_state.delta_t = delta_t
                st.session_state.end_time = end_time
                st.session_state.xt_coordinate = xt_coordinate
                st.session_state.yt_coordinate = yt_coordinate

                st.session_state.fig2 = fig2
                st.session_state.buf1 = buf1
                st.session_state.buf2 = buf2


                
                with st.spinner("Running simulation... please wait..."):
                    animation_fig, html_buf, animation_frames = show_animation(c, delta_t, x, y)
                    # st.write("")
                    st.session_state.animation_fig = animation_fig
                    st.session_state.animation_html = html_buf
                    st.session_state.animation_frames = animation_frames

        if "analyzed" in st.session_state and st.session_state.analyzed == True:
            fig1 = st.session_state.fig1
            fig2 = st.session_state.fig2
            buf1 = st.session_state.buf1
            buf2 = st.session_state.buf2
            fig = st.session_state.animation_fig
            html_buf = st.session_state.animation_html

            xt = st.session_state.xt
            yt = st.session_state.yt
            grid_x = st.session_state.grid_x
            grid_y = st.session_state.grid_y

            max_concentration = st.session_state.max_concentration
            max_concentration_idx = st.session_state.max_concentration_idx
            max_concentration_t = st.session_state.max_concentration_t
            delta_t = st.session_state.delta_t
            end_time = st.session_state.end_time
            xt_coordinate = st.session_state.xt_coordinate
            yt_coordinate = st.session_state.yt_coordinate

            xi = st.session_state.xi
            yi = st.session_state.yi
            xi_coordinate = st.session_state.xi_coordinate
            yi_coordinate = st.session_state.yi_coordinate
            
            st.write("")
            st.write(f"You have entered the release point ({xi}, {yi}) and target point ({xt}, {yt}). This program will automatically divide x and y into {grid_x} x grids and {grid_y} y grids, so the release and target points you entered may not be in the resulting grid. Therefore, the program will automatically search for the closest point to your release and target point. Based on your input, the release point will be at ({round(xi_coordinate,2)}, {round(yi_coordinate,2)}) and the target point will be at ({round(xt_coordinate,2)}, {round(yt_coordinate,2)})")

            col_1, col_2 = st.columns(2)
            with col_1:
                st.pyplot(fig1)
                st.write(f"The plot above shows the concentration at the target point ({round(xt_coordinate,2)}, {round(yt_coordinate,2)}) throughout the iteration with a delta t of {round(delta_t, 5)} seconds, with a total time of {round(end_time, 5)} seconds. The highest concentration is {round(max_concentration,2)} kg/m{ss3} at t = {round(max_concentration_t,5)} second(s).")
                st.download_button(
                    label="Download Plot 1 as PNG",
                    data=buf1,
                    file_name=f"concentration_at_target_point_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                    mime="image/png",
                    use_container_width=True
                )
            with col_2:
                st.pyplot(fig2)
                st.write(f"The plot above shows the pollutant concentration along the river (x-axis) at y = {round(yt_coordinate,2)} at various timestamps.")
                st.download_button(
                    label="Download Plot 2 as PNG",
                    data=buf2,
                    file_name=f"concentration_at_y_across_x_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                    mime="image/png",
                    use_container_width=True
                )
            
            if "animation_fig" in st.session_state:
                st.plotly_chart(st.session_state.animation_fig)

                st.write("\n\n")
                st.subheader("What the map means")
                st.write("This map represents a river seen from above. The horizontal axis (X-axis) shows the length of the river (in meters), while the vertical axis (Y-axis) shows the width of the river (in meters) from one side to the other. Each colored section corresponds to a specific area of the river.")

                st.subheader("Color = Pollution Level")
                st.write(f"The color bar on the right indicates the pollutant concentration measured in kilograms per cubic meter (kg/m{ss3}). Lighter colors represent lower pollution levels, while darker or brighter colors indicate higher concentrations of pollutants in the water.")

                st.subheader("What the animation shows")
                st.write("The animation illustrates how pollution spreads in the river over time. The pollutant is released from a source and then moves along the river flow, spreads sideways across the river width, and gradually becomes more diluted as it mixes with the surrounding water.")

                st.subheader("How to use the controls & time")
                st.write("You can press Play to run the simulation and Pause to stop it at any moment. To view a specific moment, pause the simulation first, then use the timeline slider to select the time. The time display shows how many seconds have passed since the pollutant was released.")


                if "animation_html" in st.session_state:
                    # print(st.session_state.animation_html)
                    st.download_button(
                        "Download Animation (HTML)",
                        st.session_state.animation_html,
                        file_name="animation.html",
                        mime="text/html",
                        use_container_width=True,
                        type="secondary"
                    )

                if "animation_gif" in st.session_state:
                    st.download_button(
                        "Download GIF File",
                        data=st.session_state.animation_gif,
                        file_name="animation.gif",
                        mime="image/gif",
                        type="secondary",
                        use_container_width=True
                    )
                elif "animation_fig" in st.session_state and "animation_frames" in st.session_state:
                    if st.button("Generate GIF", use_container_width=True, type="secondary"):
                        progress = st.progress(0)
                        with st.spinner("Generating GIF... please wait. This might take a while."):
                            gif_bytes = export_gif(
                                st.session_state.animation_fig,
                                st.session_state.animation_frames,
                                progress=progress
                            )

                            st.session_state.animation_gif = gif_bytes

                            st.success("GIF generated!")

                            st.download_button(
                                "Download GIF File",
                                data=gif_bytes,
                                file_name=f"animation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.gif",
                                mime="image/gif",
                                use_container_width=True,
                                type="secondary"
                            )
                
                

    elif page == "Help":
        ui.render_help()

    elif page == "About Us":
        ui.render_about_us()
