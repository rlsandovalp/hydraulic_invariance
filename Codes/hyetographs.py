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
    ax.set_xlabel('Time [hours]')
    ax.set_ylabel('Rain depth [mm]')
    return fig

def plot_uniform():
    fig, ax = plt.subplots(figsize = (10,3))
    ax.bar(uniform[:,0], uniform[:,1], width = 0.9*dt, align = 'edge')
    for i in range(len(uniform[:,0])):
        ax.text(uniform[i,0]+0.2*dt, uniform[i,1]+0.5, round(uniform[i,1],2))
    ax.set_xlim(0,duration_m)
    ax.set_ylim(0, 1.2*np.max(uniform[:,1]))
    ax.set_title('Uniform Hyetograph')
    ax.set_xlabel('Time [hours]')
    ax.set_ylabel('Rain depth [mm]')
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

## LSPP parameters
a1 = st.sidebar.number_input('a1', 20.0, 40.0, 30.0)
n = st.sidebar.number_input('n', 0.1, 0.6, 0.3)
alpha = st.sidebar.number_input(r"$\alpha$", 0.1, 0.6, 0.3)
epsilon = st.sidebar.number_input(r'\varepsilon', 0.2, 1.1, 0.8)
kappa = st.sidebar.number_input(r'\varepsilon', -1.0, 1.0, -0.001)


### rain duration [hours], interval of hyetograph [min], position of the peak [0,1], and return period [years]
duration_h = st.sidebar.number_input('Rain Duration [Hours]', 0.2, 6.0, 1.0)
dt = st.sidebar.number_input('Hyetograph interval [Minutes]', 1, 15, 5)
r = st.sidebar.number_input('Position of the peak [0-1] (r)', 0.1, 0.9, 0.5)
Tr = st.sidebar.number_input('Return period [Years]', 2, 500, 100)


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
uniform = np.zeros((int(duration_m/dt),2))
chicago[:,0] = aaa[:,0]
chicago[:,1] = aaa[:,2]
uniform[:,0] = aaa[:-1,0]
uniform[:,1] = a1*wtr*duration_h**(n-1)*dt/60

st.write('Total rain depth Chicago: ' + str(round(np.sum(chicago[:,1]), 2)) + ' mm')

st.pyplot(plot_chicago())

df = pd.DataFrame(chicago, columns = ['Time [min]', 'h[mm]'])

aa = df.to_csv().encode('utf-8')

st.download_button(
    label="Download data as CSV",
    data=aa,
    file_name='large_df.csv',
    mime='text/csv',
)

st.write('Total rain depth Uniform: ' + str(round(np.sum(uniform[:,1]), 2)) + ' mm')

st.pyplot(plot_uniform())


dfb = pd.DataFrame(chicago, columns = ['Time [min]', 'h[mm]'])

aab = df.to_csv().encode('utf-8')

st.download_button(
    label="Download data as CSV",
    data=aab,
    file_name='large_df.csv',
    mime='text/csv',
)