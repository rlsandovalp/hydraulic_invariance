import streamlit as st

st.set_page_config(
    page_title="About this tool",
    page_icon="ℹ️",
    layout="wide",
    initial_sidebar_state="auto"
)

st.header('About this tool 📄')

r'''
This tool was developed by [Leonardo Sandoval](https://www.linkedin.com/in/rafael-leonardo-sandoval-pab%C3%B3n-6a04b89b/) to estimate hyetographs for hydrological studies, following the LSPP (Linee Segnalatrici di Possibilità Pluviometrica) methodology typically employed in the Lombardy region of Italy.

The tool request information of the effective parameters of the LSPP method for a given area as well as the total duration of the rain, the time intervals for which you want to recover the precipitation, the position of the peak $r$, and the return period. Then it calculates the rain depth for an uniform hyetogram and a Chicago hyetogram, plotting the results. The user can download the hyetogram data than can then be used in SWMM (or any other software) for further analysis.
'''