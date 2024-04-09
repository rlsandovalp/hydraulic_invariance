import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import plotly.graph_objects as go


st.set_page_config(
    page_title="About this app",
    page_icon="❓",
    layout="wide",
    initial_sidebar_state="auto"
)

st.header('About this app')

r'This App was developed by [Leonardo Sandoval](https://www.linkedin.com/in/rafael-leonardo-sandoval-pab%C3%B3n-6a04b89b/) in the context of the hydraulic invariance project developed between Lario Reti Holding and the Politecnico di Milano. The objective of the project is to facilitate local authorities of the municipalities in the Lecco Region to access and analyze relevant data to the fulfilment of hydraulic invariance studies requested by the Italian Government.'

'The App has three main functionalities:'

'1. **Visualize and Download Maps**: This tool allows the user to visualize and download gis files of different hydrological parameters in the Lecco region of Italy. The user can select the parameter of interest and the municipality of interest, and the app will display the corresponding shapefile on a map. The user can then download the shapefile for further analysis.'

'2. **Sewer Network Analysis under uniform flow conditions**: This tool allows the user to analyze the sewer network of a given municipality in the Lecco region of Italy. The user should provide shapefiles or excel files with the information of the nodes, the conduits, and the area served by the sewer network. Then the app will calculate the flow in each conduit and the depth in each manhole under uniform flow conditions and it can create maps where critical elements of the network are highlighted. The app will then generate the input files of a SWMM simulation that the user can then employ for further analysis.'

'3. **Estimate Hyetographs for Hydrological Studies**: This tool allows the user to estimate hyetographs for hydrological studies, following the LSPP (Linee Segnalatrici di Possibilità Pluviometrica) methodology typically employed in the Lombardy region of Italy. The tool requests information of the effective parameters of the LSPP method for a given area as well as the total duration of the rain, the time intervals for which you want to recover the precipitation, the position of the peak, and the return period. Then it calculates the rain depth for an uniform hyetogram and a Chicago hyetogram, plotting the results. The user can download the hyetogram data than can then be used in SWMM (or any other software) for further analysis.'

'This app is complemented by an ArcGIS plugin provided to Lario Reti Holding that allows the user to extract further data and perform the calculation of hydrologic and hydraulic parameters of user defined areas'






