# # -*- coding: utf-8 -*-
# """
# Created on Fri May  8 17:08:43 2020
#%%
import numpy as np
import matplotlib.pyplot as plt
from scipy.constants import pi, c
from numpy.fft import fft, ifft, fftshift

#%%
def calculate_spectrum(z, E, H, f=3.7e9):
    k0 = 2*pi*f/c
    lambda0 = c/f
    # fourier domain points
    B = 2**20
    Efft = np.fft.fftshift(np.fft.fft(E,B))
    Hfft = np.fft.fftshift(np.fft.fft(H,B))
    # fourier domain bins
    dz = z[1] - z[0] # assumes spatial period is constant
    df = 1/(B*dz)
    K = np.arange(-B/2,+B/2)
    # spatial frequency bins
    Fz= K*df
    # parallel index is kz/k0
    nz= (2*pi/k0)*Fz
    # ~ power density spectrum
    p = (dz)**2/lambda0 * (1/2*Efft*np.conj(Hfft))
    
    return(nz,p)


#%%
def spectrum_from_HFSS_file(Ereal, Eimag, Hreal, Himag, f):

    x,y,z,Ex_re,Ey_re,Ez_re = np.loadtxt(Ereal, skiprows=2, unpack=True)
    x,y,z,Ex_im,Ey_im,Ez_im = np.loadtxt(Eimag, skiprows=2, unpack=True)
    x,y,z,Hx_re,Hy_re,Hz_re = np.loadtxt(Hreal, skiprows=2, unpack=True)
    x,y,z,Hx_im,Hy_im,Hz_im = np.loadtxt(Himag, skiprows=2, unpack=True)
    
    # create a curvilinear 
    _s = np.sqrt((x - x[0])**2 + (y - y[0])**2 + (z - z[0])**2)
    
    _Ex = Ex_re + 1j*Ex_im
    _Ey = Ey_re + 1j*Ey_im
    _Ez = Ez_re + 1j*Ez_im
    _Hx = Hx_re + 1j*Hx_im
    _Hy = Hy_re + 1j*Hy_im
    _Hz = Hz_re + 1j*Hz_im
    # replace NaN with 0
    _Ex = np.nan_to_num(_Ex)
    _Ey = np.nan_to_num(_Ey)
    _Ez = np.nan_to_num(_Ez)
    _Hx = np.nan_to_num(_Hx)
    _Hy = np.nan_to_num(_Hy)
    _Hz = np.nan_to_num(_Hz)
    
    # nextpow 2
    nb_s = int(2**np.ceil(np.log2(len(_s))))
    s = np.linspace(np.min(_s), np.max(_s), num=nb_s)
    
    # interpolated field on this regular mesh
    Ex = np.interp(s, _s, _Ex)
    Ey = np.interp(s, _s, _Ey)
    Ez = np.interp(s, _s, _Ez)
    Hx = np.interp(s, _s, _Hx)
    Hy = np.interp(s, _s, _Hy)
    Hz = np.interp(s, _s, _Hz)
    
    N = 1000
    s = np.pad(s, N, mode='reflect', reflect_type='odd')
    Ey = np.pad(Ey, N)
    Hx = np.pad(Ey, N)
    
    nz, p = calculate_spectrum(s, Ey, -Hx, f=f0)
    return p, nz

#%% create HFSS point file
Nx, Ny, Nz = 1, 101, 101
x_list = np.linspace(0, 0, num=Nx)
y_list = np.linspace(-500, 500, num=Ny)
z_list = np.linspace(-500, 500, num=Nz)
X,Y,Z = np.meshgrid(x_list, y_list, z_list)
np.savetxt('points.pts', 
           np.vstack([X.reshape(Nx*Ny*Nz), Y.reshape(Nx*Ny*Nz), Z.reshape(Nx*Ny*Nz)]).T, 
           delimiter=' ', header='Unit=mm', comments='')

#%% Read 2D data
Ereal = 'WEST_ICRH_Flat_Dielectric_2D_Ereal.fld'
Eimag = 'WEST_ICRH_Flat_Dielectric_2D_Eimag.fld'
Hreal = 'WEST_ICRH_Flat_Dielectric_2D_Hreal.fld'
Himag = 'WEST_ICRH_Flat_Dielectric_2D_Himag.fld'

#%%
x, y, z, Ex_re, Ey_re, Ez_re = np.loadtxt('WEST_ICRH_Flat_Dielectric_2D_Ereal.fld', skiprows=2, unpack=True)   
  ;                                                                                  
#%%
from scipy.interpolate import interp2d

# f will be a function with two arguments (x and y coordinates),
# but those can be array_like structures too, in which case the
# result will be a matrix representing the values in the grid 
# specified by those arguments

f = interp2d(z, y, Ey_re, kind="linear")

y_coords = np.linspace(np.min(y), np.max(y)+1, 1001)
z_coords = np.linspace(np.min(z), np.max(z)+1, 1001)
Z = f(z_coords, y_coords)

fig = plt.imshow(Z,
            extent=[np.min(z), np.max(z), np.min(y), np.max(y)],
            origin="lower")


# #%%
# fig, ax = plt.subplots()
# ax.

# #%%  monopole and dipole in curved model
# f0 = 50e6
# w0 = 2*pi*f0
# k0 = w0/c


# p_curved_monopole, nz_curved_monopole = spectrum_from_HFSS_file(Ereal, Eimag, Hreal, Himag, f=f0)
# Ereal = 'WEST_ICRH_Curved_Vacuum_dipole_Ereal.fld'
# Eimag = 'WEST_ICRH_Curved_Vacuum_dipole_Eimag.fld'
# Hreal = 'WEST_ICRH_Curved_Vacuum_dipole_Hreal.fld'
# Himag = 'WEST_ICRH_Curved_Vacuum_dipole_Himag.fld'
# p_curved_dipole, nz_curved_dipole = spectrum_from_HFSS_file(Ereal, Eimag, Hreal, Himag, f=f0)

# #%%
# fig, ax = plt.subplots()
# # ax.plot(k0*nz_flat, np.abs(p_flat)/np.max(np.abs(p_flat)) )
# # ax.plot(k0*nz_curved_dipole, np.abs(p_curved_dipole)/np.max(np.abs(p_curved_dipole)), lw=2 )
# # ax.plot(k0*nz_curved_monopole, np.abs(p_curved_monopole)/np.max(np.abs(p_curved_monopole)), lw=2 )
# ax.plot(k0*nz_curved_dipole, np.abs(p_curved_dipole), lw=2 )
# ax.plot(k0*nz_curved_monopole, np.abs(p_curved_monopole), lw=2 )

# ax.set_xlim(-30, +30)
# ax.set_ylabel('Power spectrum density [a.u.]', fontsize=14)
# ax.set_xlabel('Toroidal wavenumber $k_z$ [$m^{-1}$]', fontsize=14)
# ax.set_title('WEST ICRH Antenna Power Spectrum Density (Vacuum)', fontsize=14)
# ax.tick_params(labelsize=14)
# ax.grid(True, alpha=0.2)
# fig.tight_layout()
# fig.savefig('WEST_ICRH_Spectrum_Vacuum.png', dpi=150)

# # % Power conservation checking
# # disp(['Power conservation checking : total transmited power [W] :', num2str(dnz*sum(real(dP_nz)))])
  

# #%% flat model - dielectric medium
# Ereal = 'WEST_ICRH_Flat_Dielectric_Ereal.fld'
# Eimag = 'WEST_ICRH_Flat_Dielectric_Eimag.fld'
# Hreal = 'WEST_ICRH_Flat_Dielectric_Hreal.fld'
# Himag = 'WEST_ICRH_Flat_Dielectric_Himag.fld'
# p_flat_dielectric, nz_flat_dielectric = spectrum_from_HFSS_file(Ereal, Eimag, Hreal, Himag, f=f0)
# #%%
# fig, ax = plt.subplots()
# ax.plot(k0*nz_flat_dielectric, np.abs(p_flat_dielectric)/np.max(np.abs(p_flat_dielectric)) )
# ax.set_xlim(-30, +30)
# ax.set_ylabel('Power spectrum density [a.u.]', fontsize=14)
# ax.set_xlabel('Toroidal wavenumber $k_z$ [$m^{-1}$]', fontsize=14)
# ax.set_title('WEST ICRH Antenna Power Spectrum Density (Vacuum)', fontsize=14)
# ax.tick_params(labelsize=14)
# ax.grid(True, alpha=0.2)
# fig.tight_layout()

