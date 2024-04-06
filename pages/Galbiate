import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Galbiate Precipitation Parameters",
    page_icon="🌧️",
    layout="wide",
    initial_sidebar_state="auto"
)



data_from_qgis = ((31.21,	0.3201,	0.3022,	0.8229,	-0.0079,	.3),
                (31.52,	0.3207,	0.3005,	0.8263,	-0.0003,	6.7),
                (31.51,	0.3187,	0.3032,	0.8246,	-0.0009,	52.1),
                (31.02,	0.3276,	0.3107,	0.8225,	0.0064,	132.5),
                (31.28,	0.3162,	0.3027,	0.823,	-0.007,	0.2),
                (31.55,	0.3172,	0.2995,	0.8262,	-0.0026,	63.3),
                (31.48,	0.3174,	0.2999,	0.8249,	-0.0062,	225.1),
                (31.37,	0.3206,	0.3056,	0.8238,	0.0013,	151.7),
                (31.54,	0.3172,	0.2985,	0.8256,	-0.0057,	61.6),
                (31.52,	0.3159,	0.3005,	0.8247,	-0.0057,	210.7),
                (31.29,	0.3191,	0.3029,	0.8252,	0.0003,	150.7),
                (31.54,	0.3152,	0.3006,	0.8269,	0.0014,	84.8),
                (31.4,	0.3194,	0.3041,	0.8246,	0.0008,	182.5),
                (31.47,	0.3164,	0.301,	0.8255,	-0.0027,	66.0),
                (31.38,	0.3195,	0.3048,	0.8244,	0.0014,	123.0),
                (31.57,	0.3155,	0.3007,	0.8257,	-0.0021,	16.5),
                (31.37,	0.3207,	0.3066,	0.8241,	0.0035,	65.2))

df = pd.DataFrame(
   data_from_qgis,
   columns=('a1', 'n', 'Alpha', 'Epsilon', 'Kappa', 'Area [ha]'))

'''
## LSPP Parameters of Galbiate

The following table list the LSPP parameters associated with polygons over 
the area of Galbiate. Since the values of the parameters are close among different areas, 
we combined them (via weighted average) to generate a unique set of parameters that is then employed 
to generate the hyetographs employed for the hydrologic analysis.
'''

st.table(df)

df1 = pd.DataFrame(columns = ('a1', 'n', 'Alpha', 'Epsilon', 'Kappa'))
df1.loc[0] = [31.41,	0.32,	0.30,	0.82,	-0.001]

'''
The averaged parameters to generate the hytographs are:
'''

st.table(df1)

