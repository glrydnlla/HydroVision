import streamlit as st

STEPS = [
    {
        "title": "Welcome", 
        "text": "This quick tutorial will guide you through the main inputs and buttons. If you want to know the main concept of this simulation, please refer to the help menu."
    },
    {
        "title": "Grid & Domain", 
        "text": "Set Numbers of X and Y grid, and Lengths. These define spatial resolution and domain size. The grid sizes will be calculated automatically."
    },
    {
        "title": "Inhomogeneity", 
        "text": "Parameters a and b are used to simulate the inhomogeneity of the river."
    },
    {
        "title": "Diffusion", 
        "text": "Input the initial diffusion coefficients for X and Y. These will vary across x and y according to the value of a and b."
    },
    {
        "title": "Velocity", 
        "text": "u0 and v0 are initial velocities for X and Y. u and v will vary across x and y according to the value of a and b."
    },
    {
        "title": "Injection", 
        "text": "The coordinate of pollutant release point is the location of the pollutant release."
    },
    {
        "title": "Pollutant Injection & Flow", 
        "text": "m is the mass of injected pollutant. Q is volumetric flow rate used when injecting pollutant."
    },
    {
        "title": "Iteration", 
        "text": "t is the number of iterations or time steps. If the t value is too big you might need to wait longer for the plot to finish rendering."
    },
    {
        "title": "Analyze and Run Simulation", 
        "text": "Concentration for each time step will be calculated based on the forward time and centered space scheme. The pollutant dispersion will be simulated and animated after the calculation has finished."
    },
    {
        "title": "Finish", 
        "text": "End of tutorial. You can re-open this tutorial by clicking the 'Show tutorial' menu in the sidebar."
    },
]

def init_tutorial_state():
    if "show_tutorial" not in st.session_state:
        st.session_state.show_tutorial = False
    if "tutorial_step" not in st.session_state:
        st.session_state.tutorial_step = 0
    if "tutorial_finished" not in st.session_state:
        st.session_state.tutorial_finished = False

def open_tutorial():
    st.session_state.show_tutorial = True
    st.session_state.tutorial_step = 0
    st.session_state.tutorial_finished = False

def close_tutorial(finish=False):
    st.session_state.show_tutorial = False
    if finish:
        st.session_state.tutorial_finished = True

def tutorial_next():
    st.session_state.tutorial_step = min(st.session_state.tutorial_step + 1, len(STEPS) - 1)
    print(st.session_state.tutorial_step)

def tutorial_previous():
    st.session_state.tutorial_step = max(st.session_state.tutorial_step - 1, 0)

def render_tutorial_modal():
    step_idx = st.session_state.tutorial_step
    step = STEPS[step_idx]

    def modal_contents(container):
        container.header(step["title"])
        container.write(step["text"])
        container.caption(f"Step {step_idx + 1} of {len(STEPS)}")

        cols = container.columns([1,1,1])
        if cols[0].button("Back", key=f"tut_back_{step_idx}", disabled=(step_idx == 0)):
            tutorial_previous()
            st.rerun()

        if cols[1].button("Finish", key=f"tut_finish_final"):
            close_tutorial(finish=True)
            st.rerun()
        
        if cols[2].button("Next", key=f"tut_next_{step_idx}", disabled=(step_idx == len(STEPS) - 1)):
            tutorial_next()
            st.rerun()
        
    try:
        with st.modal("Tutorial", clear_on_close=False) as m:
            modal_contents(m)
    except Exception:
        with st.container():
            modal_contents(st)