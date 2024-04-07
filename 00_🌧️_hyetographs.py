import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import plotly.graph_objects as go


st.set_page_config(
    page_title="Hyetographs",
    page_icon="🌧️",
    layout="wide",
    initial_sidebar_state="auto"
)

def plot_chicago():
    fig = go.Figure()
    fig.add_trace(go.Bar(x=chicago[:,0], y=chicago[:,1], name='Rain depth'))
    fig.update_layout(
        xaxis_title = 'Time [minutes]',
        yaxis_title = 'Rain depth [mm]',
        xaxis = dict(range = [0, duration_m+dt]),
        yaxis = dict(range = [0, 1.2*np.max(chicago[:,1])]),
        showlegend = False
    )
    return fig

def plot_uniform():
    fig = go.Figure()
    fig.add_trace(go.Bar(x=uniform[1:,0], y=uniform[1:,1], name='Rain depth', offset = -5))
    fig.update_layout(
        xaxis_title = 'Time [minutes]',
        yaxis_title = 'Rain depth [mm]',
        xaxis = dict(range = [0, duration_m+dt]),
        yaxis = dict(range = [0, 1.2*np.max(uniform[:,1])]),
        showlegend = False
    )
    return fig

def plot_LSPP():
    x = np.linspace(0,5,1000)
    Tr = [10,50,100]

    fig = go.Figure()
    for tr in Tr:
        wtr = epsilon + alpha/kappa*(1-(np.log(tr/(tr-1)))**kappa)
        h = a1*wtr*x**n
        fig.add_trace(go.Scatter(x=x, y=h, mode='lines', name='Tr '+str(tr)+' years'))

    fig.update_layout(
        xaxis_title = 'd [hours]',
        yaxis_title = 'h<sub>d, tr</sub> [mm]',
        xaxis = dict(range = [0, 5]),
        yaxis = dict(range = [0, 140]),
        legend = dict(x = 0, y = 1, traceorder = "normal", font = dict(family = "sans-serif", size = 12, color = "black"), 
                      bgcolor = "LightSteelBlue", bordercolor = "Black", borderwidth = 1),
        plot_bgcolor = 'white',
        showlegend = True,
        )
    return fig


### rain duration [hours], interval of hyetograph [min], position of the peak [0,1], and return period [years]
duration_m = st.sidebar.number_input('Rain Duration [Minutes]', 10, 600, 60)
dt = st.sidebar.number_input('Hyetograph interval [Minutes]', 1, 30, 5)
r = st.sidebar.number_input('Position of the peak [0-1] (r)', 0.1, 0.9, 0.5)
Tr = st.sidebar.number_input('Return period [Years]', 2, 500, 100)

st.header('LSPP Curves')

col1, col2 = st.columns([1,2])

with col1:
    a1 = st.number_input('a1', 20.00, 40.00, 30.00, format = '%.3f')
    n = st.number_input('n', 0.10, 0.60, 0.30, format = '%.3f')
    alpha = st.number_input("Alpha", 0.10, 0.60, 0.30, format = '%.3f')
    epsilon = st.number_input('Epsilon', 0.20, 1.10, 0.80, format = '%.3f')
    kappa = st.number_input('Kappa', -1.0000, 1.0000, -0.0010, format = '%.4f')
with col2:
    st.plotly_chart(plot_LSPP(), use_container_width=True)


### Compute rain duration, total rain depth, and time to the peak 
duration_h = duration_m/60
wtr = epsilon + alpha/kappa*(1-(np.log(Tr/(Tr-1)))**kappa)
atr = a1*wtr
h = atr*duration_h**n
tp = r*duration_h

aaa = np.zeros((int(duration_m/dt)+1, 3))
aaa[:,0]= np.linspace(0,duration_m,int(duration_m/dt)+1)

for i in range(int(duration_m/dt)+1):
    if aaa[i,0]>r*duration_m:
        aaa[i,1] = atr*(r*(tp/r)**n+(1-r)*((aaa[i,0]/60-tp)/(1-r))**n)
    else:
        aaa[i,1] = r*atr*((tp/r)**n-((tp-aaa[i,0]/60)/r)**n)

for i in range(1, int(duration_m/dt)+1):
    aaa[i,2] = aaa[i,1]-aaa[i-1,1]


chicago = np.zeros((int(duration_m/dt)+1,2))
uniform = np.zeros((int(duration_m/dt)+1,2))
chicago[:,0] = aaa[:,0]
chicago[:,1] = aaa[:,2]
uniform[:,0] = aaa[:,0]
uniform[:,1] = a1*wtr*duration_h**(n-1)*dt/60


col1, col2 = st.columns([1,1])

with col1:
    ##### CHICAGO

    veces = chicago.shape[0]

    dates = ['07/09/2020']*veces

    time_list, hour, minute = [], 1, 0
    for vez in range(veces):
        time_list.append(f"{hour:02d}:{minute:02d}")
        minute = minute + dt
        if minute == 60:
            hour = hour + 1
            minute = 0

    df = pd.DataFrame(np.transpose([dates, time_list, chicago[:,1]]))
    chicago_hyetograph = df.to_csv(sep = ' ', index = False, header = False).encode('utf-8')


    st.header('Chicago Hyetograph')
    st.download_button(label = "Download Chicago for SWMM", data = chicago_hyetograph, file_name = 'RG_Chicago_'+str(Tr)+'.dat', mime = 'text/csv',)
    st.write('Total rain depth Chicago: ' + str(round(np.sum(chicago[:,1]), 2)) + ' mm')
    st.plotly_chart(plot_chicago(), use_container_width=True)

with col2:
    ##### UNIFORM

    df_u = pd.DataFrame(np.transpose([dates, time_list, uniform[:,1]]))
    uniform_hyetograph = df_u.to_csv(sep = ' ', index = False, header = False).encode('utf-8')

    st.header('Uniform Hyetograph')
    st.download_button(label = "Download Uniform for SWMM", data = uniform_hyetograph, file_name = 'RG_Uniform_'+str(Tr)+'.dat', mime = 'text/csv',)
    st.write('Total rain depth Uniform: ' + str(round(np.sum(uniform[:-1,1]), 2)) + ' mm')
    st.plotly_chart(plot_uniform(), use_container_width=True)





