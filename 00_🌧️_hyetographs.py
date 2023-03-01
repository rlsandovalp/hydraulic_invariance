import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st


st.set_page_config(
    page_title="Hyetographs",
    page_icon="🌧️",
    layout="wide",
    initial_sidebar_state="auto"
)

def plot_chicago():
    fig, ax = plt.subplots(figsize = (10,3))
    ax.bar(chicago[:,0], chicago[:,1], width = -0.9*dt, align = 'edge')
    for i in range(1, len(chicago[:,0])):
        ax.text(chicago[i,0]-0.7*dt, chicago[i,1]+1, round(chicago[i,1],2))
    ax.set_xlim(0,duration_m)
    ax.set_ylim(0, 1.2*np.max(chicago[:,1]))
    ax.set_title('Chicago Hyetograph')
    ax.set_xlabel('Time [minutes]')
    ax.set_ylabel('Rain depth [mm]')
    return fig

def plot_uniform():
    fig, ax = plt.subplots(figsize = (10,3))
    ax.bar(uniform[:,0], uniform[:,1], width = -0.9*dt, align = 'edge')
    for i in range(len(uniform[:,0])-1):
        ax.text(uniform[i,0]+0.2*dt, uniform[i,1]+0.5, round(uniform[i,1],2))
    ax.set_xlim(0,duration_m)
    ax.set_ylim(0, 1.2*np.max(uniform[:,1]))
    ax.set_title('Uniform Hyetograph')
    ax.set_xlabel('Time [minutes]')
    ax.set_ylabel('Rain depth [mm]')
    return fig

def plot_LSPP():
    fig, ax = plt.subplots(figsize = (5,3))
    x = np.linspace(0,5,100)
    Tr = [10,50,100]
    for tr in Tr:
        wtr = epsilon + alpha/kappa*(1-(np.log(tr/(tr-1)))**kappa)
        h = a1*wtr*x**n
        ax.plot(x, h, label = 'TR '+str(tr)+' anni')
    ax.set_xlim(0,5)
    ax.set_ylim(0, 140)
    ax.set_xlabel(r'$d$ [ore]')
    ax.set_ylabel(r'$h_{d,tr}$ [mm]')
    plt.grid()
    plt.legend()
    return fig

r'''
### Hyetographs 🌧️🌧️

Code to compute the chicago and uniform hyetographs by employing the LSPP
parameters of the Lombardy region in italy. Later I will add the equations.

You should specify, the parameter values, the duration of the rain, the intervals at which you want
to recover the precipitation, the position of the peak, and the return period.

Rain depth for an uniform hyetogram:

$$
W_{T_r} = \varepsilon + \frac{\alpha}{\kappa}\left[1-\left[\ln\left(\frac{Tr}{Tr-1}\right)\right]^{\kappa}\right]
$$

$$
a_{T_r} = a_1 * W_{T_r}
$$

$$
i(t) = a1*W_{T_r}*d^{n-1}
$$

$$
h(t) = i(t) \frac{dt}{60}
$$

Rain depth for an Chicago hyetogram $t_p = rd$:

When $t<t_p$
$$
H(t) = r a_{T_r} \left[\left(\frac{t_p}{r}\right)^n-\left(\frac{t_p-t}{r}\right)^n\right]
$$

When $t>t_p$
$$
H(t) = a_{T_r} \left[r \left(\frac{t_p}{r}\right)^n-(1-r)\left(\frac{t_p-t}{1-r}\right)^n\right]
$$

$$
h(t) = H(t+\Delta t) - H(t)
$$
'''


### rain duration [hours], interval of hyetograph [min], position of the peak [0,1], and return period [years]
duration_h = st.sidebar.number_input('Rain Duration [Hours]', 0.2, 6.0, 1.0)
dt = st.sidebar.number_input('Hyetograph interval [Minutes]', 1, 15, 5)
r = st.sidebar.number_input('Position of the peak [0-1] (r)', 0.1, 0.9, 0.5)
Tr = st.sidebar.number_input('Return period [Years]', 2, 500, 100)

r'''
### LSPP curves
'''
col1, col2 = st.columns([1,2.5])

with col1:
    a1 = st.number_input('a1', 20.00, 40.00, 30.00, format = '%.3f')
    n = st.number_input('n', 0.10, 0.60, 0.30, format = '%.3f')
    alpha = st.number_input("Alpha", 0.10, 0.60, 0.30, format = '%.3f')
    epsilon = st.number_input('Epsilon', 0.20, 1.10, 0.80, format = '%.3f')
    kappa = st.number_input('Kappa', -1.0000, 1.0000, -0.0010, format = '%.4f')
with col2:
    st.pyplot(plot_LSPP())


### Compute rain duration, total rain depth, and time to the peak 
duration_m = duration_h*60
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

r'''
### Chicago hyetograph
'''

st.write('Total rain depth Chicago: ' + str(round(np.sum(chicago[:,1]), 2)) + ' mm')

st.pyplot(plot_chicago())

veces = chicago.shape[0]+1

dates = ['07/09/2020']*veces

time_list, hour, minute = [], 1, 0
for vez in range(veces):
    time_list.append(f"{hour:02d}:{minute:02d}")
    minute = minute + dt
    if vez%(60/dt-1) == 0 and vez >0:
        hour = hour + 1
        minute = 0

df = pd.DataFrame(np.transpose([dates, time_list, chicago[:,1]]))

chicago_hyetograph = df.to_csv(sep = ' ', index = False, header = False).encode('utf-8')

st.download_button(
    label = "Download Chicago",
    data = chicago_hyetograph,
    file_name = 'RG_Chicago_'+str(Tr)+'.dat',
    mime = 'text/csv',
)

r'''
### Uniform hyetograph
'''

st.write('Total rain depth Uniform: ' + str(round(np.sum(uniform[:-1,1]), 2)) + ' mm')

st.pyplot(plot_uniform())

df_u = pd.DataFrame(np.transpose([dates, time_list, uniform[:,1]]))

uniform_hyetograph = df_u.to_csv(sep = ' ', index = False, header = False).encode('utf-8')

st.download_button(
    label = "Download Uniform",
    data = uniform_hyetograph,
    file_name = 'RG_Uniform_'+str(Tr)+'.dat',
    mime = 'text/csv',
)

