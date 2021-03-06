# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 21:18:23 2015

Matching a single conjugate-T.


 _ GD
 |
 [Z1]
 |__[C1]__
          |
          |-- Z_T ----[imp transf]----[window]---
  __[C2]__|  
 |
 [Z2]
 |
 - GD


@author: J.Hillairet
"""
from matplotlib.pylab import *

import skrf as rf

from antenna.conjugate_t import ConjugateT
from antenna.topica import *

f_match = 55e6 # matching frequency
Z_match = 30-0*1j # matching impedance 
Z_load = 0.5 + 30*1j
Pin = 1 # W

######
bridge = rf.io.hfss_touchstone_2_network(\
        './data/Sparameters/WEST/WEST_ICRH_bridge.s3p', f_unit='MHz')
impedance_transformer = rf.io.hfss_touchstone_2_network(\
        './data/Sparameters/WEST/WEST_ICRH_impedance-transformer.s2p', f_unit='MHz')
window = rf.io.hfss_touchstone_2_network(\
        './data/Sparameters/WEST/WEST_ICRH_window.s2p', f_unit='MHz')
idx_f = np.argmin(np.abs(bridge.frequency.f - f_match))

# Characteristic Impedance depends of the prototype number.
# TSproto10: 13.7 Ohm
# TSproto12: 46.7 Ohm
CT = ConjugateT(bridge, impedance_transformer, window)

# Match the capacitors of the ConjugateT
sol=CT.match(f_match=f_match, z_load=Z_load, z_match=Z_match)
CT.C = sol.x
print(sol.x*1e12)

# plot S11
figure(1)
clf()
CT.load(Z_load).plot_s_db(show_legend=False)

# Calculates Currents and Voltages at capacitors (plasma side)
I_capa, V_capa = CT.get_capacitor_currents_voltages([Z_load, Z_load], Pin)

# Print results
print(np.abs(I_capa[idx_f,:])/1e3)
print(180/pi*np.angle(I_capa[idx_f,:]))

print(CT.load(Z_load).s_vswr[idx_f])

print(np.abs(V_capa[idx_f,:])/1e3)
print(180/pi*np.angle(V_capa[idx_f,:]))

