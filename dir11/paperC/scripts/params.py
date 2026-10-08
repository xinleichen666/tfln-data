"""Sourced parameters for concept paper C. Every number has a source tag; 'ASSUMPTION' marks non-sourced choices."""
import numpy as np
c = 2.998e8; h = 6.626e-34; kB = 1.381e-23
# Optical
n_g_TFLN = 2.3          # ASSUMPTION: typical TFLN ridge group index (not sourced)
v_o = c / n_g_TFLN
loss_TFLN_ring = 1.3     # dB/m, Zhu et al. Photon. Res. 12, A63 (2024), arXiv:2402.16161 (Q_i=29.3M)
loss_TFLN_ODL = 2.5      # dB/m (0.025 dB/cm), 30-cm TFLN ODL, Opt. Lett. 2023 (abstract only), 2.05 ns delay
loss_TFLN_material = 0.2 # dB/m, Shams-Ansari APL Photonics 7, 081301 (2022) material-limited (annealed)
loss_SMF = 0.2e-3        # dB/m, ASSUMPTION: standard SMF-28 class value (textbook, not re-verified)
n_g_SMF = 1.468          # ASSUMPTION: standard SMF group index
# Acoustic (LN-on-sapphire guided phonons, Mayor et al. PRApplied 15, 014039 (2021), arXiv:2007.04961 full text)
v_ac = 3.1e3             # m/s, measured group velocity in racetrack (Mayor 2021)
loss_ac_RT = 4.0         # dB/mm, delay-line impulse response, RT (Mayor 2021), f~3.4 GHz
loss_ac_4K = 0.7         # dB/mm, racetrack Q_i=46000 at 4 K (Mayor 2021), f~3.4 GHz
f_ac_mayor = 3.4e9
# Brillouin in TFLN (Ye/... arXiv:2311.14697, full text): x-cut 0 deg uncladded, G_B=26.1 /W/m, linewidth 11.9 MHz (same device)
G_B = 26.1               # 1/(W m)
Gam_SBS_RT = 2*np.pi*11.9e6   # s^-1, measured Brillouin linewidth (FWHM, energy decay rate)
f_SBS = 8.0e9            # ~8 GHz Brillouin shift (8.06-8.34 GHz reported)
GBGam = G_B*Gam_SBS_RT   # g0^2-related, temperature-independent product (ASSUMPTION of standard theory)
def gam_from_dBmm(a_dBmm, v=v_ac):
    a = a_dBmm*1e3*np.log(10)/10   # power attenuation 1/m
    return a*v                     # energy decay rate s^-1
def nth(f, T):
    x = h*f/(kB*T); return 1/np.expm1(x)
