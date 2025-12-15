import streamlit as st
import tutorial
from streamlit_option_menu import option_menu

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

def init_app_state():
    if "welcome_shown" not in st.session_state:
        st.session_state.welcome_shown = False
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Welcome"

def render_welcome():
    st.title("HydroVision: An Advection–Diffusion Based River Pollution Model")
    st.write("HydroVision is a simulation application designed to model and analyze the dispersion of pollutants in a river. The application helps users understand how pollutants are transported and spread over time due to river flow (advection) and diffusion processes, based on the parameters specified by the user.")
    st.write("You can use the tutorial or the help menu to get started.")

    if st.button("Continue"):
        st.session_state.welcome_shown = True
        st.session_state.current_page = "Analyze"
        st.rerun()

def show_sidebar_menu():
    with st.sidebar:
        selected = option_menu(
            None,
            ["Analyze", "Help", "About Us"],
            icons=["calculator-fill", "question-circle-fill", "file-earmark-person-fill"],
            menu_icon="list",
            default_index=0
        )

    # st.sidebar.title("Menu")
    # menu = st.sidebar.radio("Navigate", ["Analyze", "Help", "About Us"])
        st.session_state.current_page = selected

        st.sidebar.markdown("---")
        if selected == "Analyze":
            if st.sidebar.button("Show tutorial", use_container_width=True):
                tutorial.open_tutorial()
                st.session_state.show_tutorial = True
        

def render_input_panel():
    col1, col2 = st.columns(2)
    ss2 = "\u00B2"
    ss3 = "\u00B3"
    params = {}
    with col1:
        col1_1, col1_2 = st.columns(2)
        with col1_1:
            params['grid_x'] = st.number_input("Number of X grid", min_value=2, max_value=300, value=100)
            params['len_x'] = st.number_input("River Length (m)", min_value=1, max_value=4000, value=1000)
            params['a'] = st.number_input("Inhomogeneity a (for X axis)", min_value=0.0, max_value=1.0, value=0.01, step=0.01, format="%.2f")
        with col1_2:
            params['grid_y'] = st.number_input("Number of Y grid", min_value=2, max_value=300, value=100)
            params['len_y'] = st.number_input("River Width (m)", min_value=1, max_value=4000, value=1000)
            params['b'] = st.number_input("Inhomogeneity b (for Y axis)", min_value=0.0, max_value=1.0, value=0.01, step=0.01, format="%.2f")
        params['c_in'] = st.number_input(f"Initial Pollutant Concentration (kg/m{ss3})", min_value=0.0, max_value=100.0, value=1.00, step=0.01, format="%.2f")
        params['m'] = st.number_input("Injected Pollutant Mass M (kg)", min_value=0, max_value=10000000, value=10000)
        col1_3, col1_4 = st.columns(2)
        with col1_3:
            params['x0'] = st.number_input("X Coordinate of Pollutant Release Point", min_value=0, max_value=10000, value=1)
        with col1_4:
            params['y0'] = st.number_input("Y Coordinate of Pollutant Release Point", min_value=0, max_value=10000, value=1)

    with col2:
        params['P0'] = st.number_input(f"Initial Diffusion Coeff for X axis (m{ss2}/s)", min_value=0.0, max_value=3000.0, value=80.0, step=0.01, format="%.2f")
        params['R0'] = st.number_input(f"Initial Diffusion Coeff for Y axis (m{ss2}/s)", min_value=0.0, max_value=3000.0, value=0.01, step=0.01, format="%.2f")
        col2_1, col2_2 = st.columns(2)
        with col2_1:
            params['u0'] = st.number_input("Initial Velocity u0 for X axis (m/s)", min_value=0.0, max_value=100.0, value=0.5, step=0.01, format="%.2f")
        with col2_2:
            params['v0'] = st.number_input("Initial Velocity v0 for Y axis (m/s)", min_value=0.0, max_value=100.0, value=0.02, step=0.01, format="%.2f")
        params['t'] = st.number_input("Iterations", min_value=1, max_value=4000, value=100)
        params['Q'] = st.number_input(f"Volumetric Flow Rate Q (m{ss3}/s)", min_value=0.0001, max_value=1000.0, value=5.0)
        col2_3, col2_4 = st.columns(2)
        with col2_3:
            params['xt'] = st.number_input("X Coordinate of Target Point", min_value=0, max_value=10000, value=1)
        with col2_4:
            params['yt'] = st.number_input("Y Coordinate of Target Point", min_value=0, max_value=10000, value=1)

    return params

def render_help():
    sbs0 = "\u2080"
    st.title("Help")
    st.write("This menu is used to provide an explanation of how the model works and the meaning of each parameter available in the Analyze menu.")
    st.subheader("Forward Time Centered Space")
    st.write("FTCS (Forward Time–Central Space) scheme is a simple numerical method used to estimate how something changes over time and space. In the context of a river, it helps us predict how pollution moves and spreads by updating the pollutant concentration step by step: moving forward in time and looking at differences between neighboring points along the river. \n\nWhen applied to pollutant transport, FTCS works by dividing the river into small segments (grids) and repeatedly calculating how the pollutant drifts downstream with the flow and spreads out naturally. By running these calculations many times, we can simulate how the pollutant moves, how quickly it spreads, and how its concentration changes over time.")
    st.subheader("Parameters Explanation")
    st.subheader("Grid & Domain")
    st.write("The X and Y grid numbers define how many grid points are used along the river\'s length and width; higher values produce a finer spatial discretization and improved accuracy, at the expense of greater computational cost. The lengths of X and Y represent the physical dimensions of the observed river domain in meters and are used to compute the grid spacing.")
    st.subheader("Inhomogeneity")
    st.write("Parameters a and b are used to simulate the inhomogeneity of the river by allowing diffusion and flow velocity to change with position along the river domain. Physically, they represent non-uniform river conditions such as variations in water depth, changes in channel width due to narrowing or widening, and differences in bed roughness. By adjusting their values, the model can capture how transport processes become stronger or weaker in different regions of the river. Larger values correspond to greater spatial variability, meaning the river properties deviate more significantly from uniform conditions across the domain.")
    st.subheader("Diffusion")
    st.write(f"P{sbs0} and Q{sbs0} represent the initial diffusion coefficients in the longitudinal (x) and lateral (y) directions, respectively. The longitudinal diffusion controls how quickly a pollutant spreads along the river flow, while the lateral diffusion governs how the pollutant disperses across the river width. The spatially varying diffusion coefficients describe how these diffusion effects change from one location to another due to non-uniform river conditions, with their variability influenced by the inhomogeneity parameters (a and b). Physically, higher diffusion leads to faster smoothing and wider spreading of pollutant concentrations, whereas lower diffusion results in sharper, more localized pollutant plumes.")
    st.subheader("Velocity")
    st.write(f"u{sbs0} and v{sbs0} represent the baseline flow velocities in the downstream (x) and cross-stream (y) directions, respectively. The downstream velocity is the primary driver of pollutant transport along the river, while the cross-stream velocity influences the movement of pollutants across the river width. The spatially varying velocity fields describe how flow conditions change throughout the river domain due to variations in channel geometry or flow structure. Physically, advection represents the transport of pollutants by the river flow, where higher velocities cause pollutants to travel farther within the same time interval.")
    st.subheader("Initial Pollutant Concentration")
    st.write("The initial pollutant concentration represents the amount of pollutant present per unit volume of water at the start of the simulation, expressed in kilograms per cubic meter. It defines the starting condition for pollutant transport within the river domain before advection and diffusion processes take place.")
    st.subheader("Pollutant Injection & Flow")
    st.write("The parameter (m) represents the total mass of pollutant injected into the river, while (Q) denotes the volumetric flow rate associated with the injection process. Together, these parameters determine the initial strength and distribution of the pollutant source in the model. A larger injected mass results in higher initial pollutant concentrations, while the flow rate influences how the pollutant is introduced into the river system and affects its initial dilution and transport behavior.")
    st.subheader("Iteration")
    st.write("t is the number of iterations or time steps. Concentration for each time step will be calculated based on the forward time and centered space scheme. The pollutant dispersion will be simulated and animated after the calculation has finished.")
    st.subheader("Injection and Target Point")
    st.write("The pollutant injection coordinate specifies the location where the pollutant is released into the river, while the target coordinate represents the point of interest where the pollutant concentration is observed and plotted. The application discretizes the river domain by automatically dividing the x- and y-directions into a fixed number of grid cells. As a result, the exact release and target coordinates entered by the user may not coincide exactly with the grid points used in the numerical model. To address this, the program automatically identifies and uses the grid points closest to the specified release and target locations.")

def render_about_us():
    st.title("About Us")
    st.write("HydroVision is a simulation application designed to model and analyze the dispersion of pollutants in a river. The application helps users understand how pollutants are transported and spread over time due to river flow (advection) and diffusion processes, based on the parameters specified by the user.")
    st.write("The application employs the Forward Time–Centered Space (FTCS) numerical method, which is a finite difference scheme that computes changes in pollutant concentration using a forward time approach and central spatial differencing. This method is applied to the two-dimensional advection–diffusion equation, which is commonly used in modeling pollutant transport in river flows.")
    st.write("HydroVision was developed by Glory Daniella from BINUS University.")