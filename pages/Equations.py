import streamlit as st

st.set_page_config(
    page_title="Equations behind Hyetographs",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="auto"
)

st.header('Equations behind Hyetographs 🌧️🌧️')

r'''
To estimate a hyetograph you should specify: 
- the LSPP parameter values
- the total duration of the rain
- the time intervals for which you want to recover the precipitation
- the position of the peak $r$
- and the return period.

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