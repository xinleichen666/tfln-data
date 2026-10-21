#!/usr/bin/env python3
"""
Bot E · skyrmion_noise
Classical noise budget: skyrmion number (Stokes texture integral) vs concurrence vs discord
under depolarizing / phase-flip / bit-phase-flip channels.
Self-defined spin–orbit texture + companion qubit. Fixed seeds.
NOT a reproduction of Zhao Nat. Phys. 2026 device numbers.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.optimize import minimize_scalar

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

SEEDS = {
    "master": 20261014,
    "depolarizing_sweep": 401,
    "phase_flip_sweep": 402,
    "bit_phase_flip_sweep": 403,
    "grid_probe": 404,
}

# Spatial grid / LG modes (assumption; NOT experiment)
ELL = 1
WAIST = 1.0
GRID_N = 97
GRID_HALF = 4.0  # in units of waist
DX = None  # set in main

# Noise grids
XI_GRID = np.round(np.linspace(0.0, 1.0, 21), 10)  # depolarizing ξ
P_GRID = np.round(np.linspace(0.0, 1.0, 21), 10)   # mix fraction for Z / Y

ZERO_THR = 0.02  # |metric| <= thr → treated as zero for crossing

DISCLAIMER = (
    "本稿仅限课题组内部：仿真与方案工作稿，实测待做，无伪造数据，"
    "Fiber-Q 对本方向 N/A，无自有流片；不得作为公开或可引用结果；"
    "verify/ 第三方 PDF 禁止入库。"
)


# ---------------------------------------------------------------------------
# Two-qubit helpers (A = L/R of skyrmion photon, B = companion path/pol)
# ---------------------------------------------------------------------------

def ket_phi_plus() -> np.ndarray:
    """(|L 0> + |R 1>)/√2  in basis |00>,|01>,|10>,|11>."""
    psi = np.zeros(4, dtype=complex)
    psi[0] = 1.0 / np.sqrt(2)  # |00> = |L 0>
    psi[3] = 1.0 / np.sqrt(2)  # |11> = |R 1>
    return psi


def pure_dm(psi: np.ndarray) -> np.ndarray:
    return np.outer(psi, psi.conj())


def apply_depolarizing(rho: np.ndarray, xi: float) -> np.ndarray:
    """ρ' = (1-ξ)ρ + (ξ/4) I_4."""
    return (1.0 - xi) * rho + (xi / 4.0) * np.eye(4, dtype=complex)


def apply_mix_unitary(rho: np.ndarray, p: float, U: np.ndarray) -> np.ndarray:
    """ρ' = (1-p)ρ + p U ρ U†."""
    Ur = U @ rho @ U.conj().T
    return (1.0 - p) * rho + p * Ur


def z_a() -> np.ndarray:
    """Phase flip on A: Z ⊗ I."""
    Z = np.array([[1, 0], [0, -1]], dtype=complex)
    return np.kron(Z, np.eye(2, dtype=complex))


def y_a() -> np.ndarray:
    """Bit-phase flip on A: Y ⊗ I."""
    Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
    return np.kron(Y, np.eye(2, dtype=complex))


def fidelity_to_psi(rho: np.ndarray, psi: np.ndarray) -> float:
    return float(np.real(psi.conj() @ rho @ psi))


def purity(rho: np.ndarray) -> float:
    return float(np.real(np.trace(rho @ rho)))


def concurrence(rho: np.ndarray) -> float:
    """Wootters concurrence for two qubits."""
    rho = 0.5 * (rho + rho.conj().T)
    sy = np.array([[0, -1j], [1j, 0]], dtype=complex)
    R_op = np.kron(sy, sy)
    rho_tilde = R_op @ rho.conj() @ R_op
    M = rho @ rho_tilde
    ev = np.linalg.eigvals(M)
    # numerical: take real parts of sqrt of eigenvalues, sort descending
    lam = np.sort(np.sqrt(np.maximum(np.real(ev), 0.0)))[::-1]
    # Ensure hermiticity path: use singular values of sqrt(sqrt(rho) rho_tilde sqrt(rho))
    # More stable:
    try:
        sqrt_rho = _sqrtm_h(rho)
        W = sqrt_rho @ rho_tilde @ sqrt_rho
        sv = np.sort(np.sqrt(np.maximum(np.real(np.linalg.eigvalsh(0.5 * (W + W.conj().T))), 0.0)))[::-1]
        lam = sv
    except Exception:
        pass
    c = float(max(0.0, lam[0] - lam[1] - lam[2] - lam[3]))
    return c


def _sqrtm_h(a: np.ndarray) -> np.ndarray:
    w, v = np.linalg.eigh(0.5 * (a + a.conj().T))
    w = np.maximum(w, 0.0)
    return (v * np.sqrt(w)) @ v.conj().T


def von_neumann(rho: np.ndarray) -> float:
    w = np.linalg.eigvalsh(0.5 * (rho + rho.conj().T))
    w = w[w > 1e-14]
    return float(-np.sum(w * np.log2(w)))


def conditional_entropy_after_measure(rho: np.ndarray, theta: float, phi: float) -> float:
    """S(A|B) after projective measure of B along Bloch (theta,phi)."""
    # Measurement projectors on B
    n = np.array(
        [
            np.sin(theta) * np.cos(phi),
            np.sin(theta) * np.sin(phi),
            np.cos(theta),
        ]
    )
    # |n+>, |n->
    # projector (I + n·σ)/2
    sx = np.array([[0, 1], [1, 0]], dtype=complex)
    sy = np.array([[0, -1j], [1j, 0]], dtype=complex)
    sz = np.array([[1, 0], [0, -1]], dtype=complex)
    nsig = n[0] * sx + n[1] * sy + n[2] * sz
    pplus = 0.5 * (np.eye(2) + nsig)
    pminus = 0.5 * (np.eye(2) - nsig)
    # Lift to 4×4: I_A ⊗ P_B
    Pp = np.kron(np.eye(2), pplus)
    Pm = np.kron(np.eye(2), pminus)
    # Unnormalized post-measurement states on AB, then partial trace? 
    # Classical-quantum: p_k, ρ_A|k = Tr_B( (I⊗Π_k) ρ (I⊗Π_k) ) / p_k
    def post_A(P):
        r = P @ rho @ P
        pk = float(np.real(np.trace(r)))
        if pk < 1e-14:
            return 0.0, np.eye(2) / 2
        # reshape to 2×2×2×2 and trace B
        r4 = r.reshape(2, 2, 2, 2)
        rhoA = np.trace(r4, axis1=1, axis2=3)  # sum over B
        rhoA = rhoA / pk
        return pk, rhoA

    p1, r1 = post_A(Pp)
    p2, r2 = post_A(Pm)
    return p1 * von_neumann(r1) + p2 * von_neumann(r2)


def quantum_discord(rho: np.ndarray) -> float:
    """
    Two-qubit discord D(A|B) = I(A:B) - max_{Π_B} J(A:B).
    Measurement optimized numerically over Bloch angles of B.
    """
    rho = 0.5 * (rho + rho.conj().T)
    # Reduced states
    r4 = rho.reshape(2, 2, 2, 2)
    rhoA = np.trace(r4, axis1=1, axis2=3)
    rhoB = np.trace(r4, axis1=0, axis2=2)
    sa = von_neumann(rhoA)
    sb = von_neumann(rhoB)
    sab = von_neumann(rho)
    mutual = sa + sb - sab

    # Maximize J = S(A) - S(A|{Π_B})  i.e. minimize conditional entropy
    best_cond = sab  # upper bound fallback

    def cond(theta, phi):
        return conditional_entropy_after_measure(rho, theta, phi)

    # grid + local refine
    thetas = np.linspace(0, np.pi, 12)
    phis = np.linspace(0, 2 * np.pi, 24, endpoint=False)
    for th in thetas:
        for ph in phis:
            c = cond(th, ph)
            if c < best_cond:
                best_cond = c

    # refine around best from coarse (re-scan with finer not needed if we minimize)
    def objective(x):
        return cond(x[0], x[1])

    # a few random starts + poles
    rng = np.random.default_rng(SEEDS["grid_probe"])
    starts = [(0.0, 0.0), (np.pi / 2, 0.0), (np.pi / 2, np.pi / 2), (np.pi, 0.0)]
    for _ in range(8):
        starts.append((rng.uniform(0, np.pi), rng.uniform(0, 2 * np.pi)))
    for th0, ph0 in starts:
        # 1D in theta then phi
        res_th = minimize_scalar(lambda t: cond(t, ph0), bounds=(0, np.pi), method="bounded", options={"xatol": 1e-8})
        th = float(res_th.x)
        res_ph = minimize_scalar(
            lambda p: cond(th, p), bounds=(0, 2 * np.pi), method="bounded", options={"xatol": 1e-8}
        )
        c = cond(th, float(res_ph.x))
        if c < best_cond:
            best_cond = c

    j_max = sa - best_cond
    d = mutual - j_max
    return float(max(0.0, d))


# ---------------------------------------------------------------------------
# Spatial LG modes + Stokes skyrmion number
# ---------------------------------------------------------------------------

def lg_p0(X: np.ndarray, Y: np.ndarray, ell: int, w: float) -> np.ndarray:
    """LG_{0,ℓ} complex amplitude on Cartesian grid."""
    r2 = X**2 + Y**2
    r = np.sqrt(r2)
    phi = np.arctan2(Y, X)
    # Normalization: ∫|u|² = 1 over plane (continuous); discrete approx
    # C = sqrt(2 / (π |ℓ|!)) / w
    from math import factorial

    pref = np.sqrt(2.0 / (np.pi * factorial(abs(ell)))) / w
    amp = pref * (np.sqrt(2.0) * r / w) ** abs(ell) * np.exp(-r2 / w**2) * np.exp(1j * ell * phi)
    return amp


def conditional_pol_rho(rho: np.ndarray) -> np.ndarray:
    """
    2×2 polarization density of A after projecting B onto |+⟩=(|0⟩+|1⟩)/√2.
    This keeps L–R coherence for a Bell-like state and yields a Stokes texture.
    """
    # M_ik = (1/2) sum_{b,b'} ρ_{(i,b),(k,b')}
    r = rho.reshape(2, 2, 2, 2)  # A_out, B_out, A_in, B_in  — wait standard reshape
    # rho indices: (a,b),(a',b') flattened as 2*a+b
    # reshape(2,2,2,2) → [a, b, a', b']
    rr = rho.reshape(2, 2, 2, 2)
    # ⟨+|ρ|+⟩_aa' = sum_bb' (+)_b* ρ_{a b, a' b'} (+)_b' with (+)=1/√2
    M = 0.5 * (
        rr[:, 0, :, 0] + rr[:, 0, :, 1] + rr[:, 1, :, 0] + rr[:, 1, :, 1]
    )
    tr = float(np.real(np.trace(M)))
    if tr < 1e-14:
        return np.eye(2, dtype=complex) / 2
    return M / tr


def stokes_field(rho_pol: np.ndarray, u_L: np.ndarray, u_R: np.ndarray):
    """Local Stokes S0..S3 from 2×2 pol matrix + spatial envelopes."""
    rLL = rho_pol[0, 0]
    rRR = rho_pol[1, 1]
    rLR = rho_pol[0, 1]
    s0 = np.real(rLL) * np.abs(u_L) ** 2 + np.real(rRR) * np.abs(u_R) ** 2
    s3 = np.real(rLL) * np.abs(u_L) ** 2 - np.real(rRR) * np.abs(u_R) ** 2
    s1 = 2.0 * np.real(rLR * np.conj(u_L) * u_R)
    s2 = 2.0 * np.imag(rLR * np.conj(u_L) * u_R)
    return s0, s1, s2, s3


def skyrmion_number(s0, s1, s2, s3, dx: float, dy: float) -> float:
    """
    N_sk = (1/4π) ∬ n · (∂x n × ∂y n) dx dy
    with n = (S1,S2,S3)/|S| where |S|=sqrt(S1²+S2²+S3²); mask S0 below floor.
    """
    mag = np.sqrt(s1**2 + s2**2 + s3**2)
    floor = 1e-10 * (np.max(mag) + 1e-30)
    mask = mag > floor
    n1 = np.zeros_like(s1)
    n2 = np.zeros_like(s2)
    n3 = np.zeros_like(s3)
    n1[mask] = s1[mask] / mag[mask]
    n2[mask] = s2[mask] / mag[mask]
    n3[mask] = s3[mask] / mag[mask]

    # central differences
    def ddx(a):
        g = np.zeros_like(a)
        g[1:-1, :] = (a[2:, :] - a[:-2, :]) / (2 * dx)
        g[0, :] = (a[1, :] - a[0, :]) / dx
        g[-1, :] = (a[-1, :] - a[-2, :]) / dx
        return g

    def ddy(a):
        g = np.zeros_like(a)
        g[:, 1:-1] = (a[:, 2:] - a[:, :-2]) / (2 * dy)
        g[:, 0] = (a[:, 1] - a[:, 0]) / dy
        g[:, -1] = (a[:, -1] - a[:, -2]) / dy
        return g

    # Note: arrays indexed [ix, iy] with X[i,:]=const x, or meshgrid indexing
    # We use meshgrid(x,y, indexing='xy') → shape (ny, nx) if X,Y from xy...
    # We'll use indexing='ij' so a[i,j] = a(x_i, y_j), ∂x → axis0, ∂y → axis1
    dxn1, dyn1 = ddx(n1), ddy(n1)
    dxn2, dyn2 = ddx(n2), ddy(n2)
    dxn3, dyn3 = ddx(n3), ddy(n3)

    # ∂x n × ∂y n
    cx = dxn2 * dyn3 - dxn3 * dyn2
    cy = dxn3 * dyn1 - dxn1 * dyn3
    cz = dxn1 * dyn2 - dxn2 * dyn1
    dens = n1 * cx + n2 * cy + n3 * cz
    dens = np.where(mask, dens, 0.0)
    nsk = float(np.sum(dens) * dx * dy / (4.0 * np.pi))
    return nsk


def metrics_for_rho(rho: np.ndarray, psi0: np.ndarray, u_L, u_R, dx, dy) -> dict:
    rho = 0.5 * (rho + rho.conj().T)
    # enforce trace 1
    rho = rho / np.trace(rho)
    pol = conditional_pol_rho(rho)
    s0, s1, s2, s3 = stokes_field(pol, u_L, u_R)
    nsk = skyrmion_number(s0, s1, s2, s3, dx, dy)
    return {
        "skyrmion_number": nsk,
        "skyrmion_abs": abs(nsk),
        "concurrence": concurrence(rho),
        "discord": quantum_discord(rho),
        "fidelity": fidelity_to_psi(rho, psi0),
        "purity": purity(rho),
    }


def first_zero_crossing(xs, ys, thr=ZERO_THR) -> dict:
    """First x where |y|<=thr; else note 本扫范围内未到零."""
    xs = list(xs)
    ys = list(ys)
    for x, y in zip(xs, ys):
        if abs(y) <= thr:
            return {
                "crossed": True,
                "cross_x": float(x),
                "cross_y": float(y),
                "note": None,
            }
    return {
        "crossed": False,
        "cross_x": None,
        "cross_y": None,
        "note": "本扫范围内未到零",
    }


def main():
    DATA.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEEDS["master"])  # reserved; sweeps are deterministic

    # Grid with indexing='ij': a[i,j] at (x_i, y_j)
    xs = np.linspace(-GRID_HALF * WAIST, GRID_HALF * WAIST, GRID_N)
    ys = np.linspace(-GRID_HALF * WAIST, GRID_HALF * WAIST, GRID_N)
    dx = float(xs[1] - xs[0])
    dy = float(ys[1] - ys[0])
    X, Y = np.meshgrid(xs, ys, indexing="ij")

    u_L = lg_p0(X, Y, ell=0, w=WAIST)
    u_R = lg_p0(X, Y, ell=ELL, w=WAIST)
    # Renormalize on discrete grid so ∑|u|² dx dy = 1
    u_L = u_L / np.sqrt(np.sum(np.abs(u_L) ** 2) * dx * dy)
    u_R = u_R / np.sqrt(np.sum(np.abs(u_R) ** 2) * dx * dy)

    psi0 = ket_phi_plus()
    rho0 = pure_dm(psi0)

    clean = metrics_for_rho(rho0, psi0, u_L, u_R, dx, dy)

    # --- sweeps ---
    depol_rows = []
    for xi in XI_GRID:
        rho = apply_depolarizing(rho0, float(xi))
        m = metrics_for_rho(rho, psi0, u_L, u_R, dx, dy)
        depol_rows.append({"xi": float(xi), **m})

    phase_rows = []
    UZ = z_a()
    for p in P_GRID:
        rho = apply_mix_unitary(rho0, float(p), UZ)
        m = metrics_for_rho(rho, psi0, u_L, u_R, dx, dy)
        phase_rows.append({"p": float(p), **m})

    bitphase_rows = []
    UY = y_a()
    for p in P_GRID:
        rho = apply_mix_unitary(rho0, float(p), UY)
        m = metrics_for_rho(rho, psi0, u_L, u_R, dx, dy)
        bitphase_rows.append({"p": float(p), **m})

    def zeros_from_rows(rows, xkey):
        xs_ = [r[xkey] for r in rows]
        out = {}
        for name, ykey in [
            ("skyrmion", "skyrmion_abs"),
            ("concurrence", "concurrence"),
            ("discord", "discord"),
        ]:
            out[name] = first_zero_crossing(xs_, [r[ykey] for r in rows])
        return out

    z_depol = zeros_from_rows(depol_rows, "xi")
    z_phase = zeros_from_rows(phase_rows, "p")
    z_bit = zeros_from_rows(bitphase_rows, "p")

    def order_who_first(zdict, xlabel):
        """Who reaches zero first (smallest cross_x among crossed)."""
        items = []
        for k, v in zdict.items():
            if v["crossed"]:
                items.append((v["cross_x"], k))
        items.sort()
        if not items:
            return {
                "who_first_to_zero": None,
                "order": [],
                "note": "本扫范围内三者均未到零",
            }
        return {
            "who_first_to_zero": items[0][1],
            "order": [{"metric": k, "cross_x": x} for x, k in items],
            "xlabel": xlabel,
        }

    summary = {
        "track": "skyrmion_noise",
        "title_frame": "方法·噪声预算",
        "prior_cite": "Zhao et al., Nat. Phys. (2026), doi:10.1038/s41567-026-03487-x",
        "disclaimer": DISCLAIMER,
        "seeds": SEEDS,
        "protocol": {
            "model_note": "自定自旋–轨道纹理 + 伴侣量子比特的经典噪声预算；不是 Zhao 实验复现",
            "state": "(|L⟩_A|0⟩_B + |R⟩_A|1⟩_B)/√2",
            "spatial": {
                "u_L": "LG_{0,0}",
                "u_R": f"LG_{{0,{ELL}}}",
                "waist": WAIST,
                "ell": ELL,
                "grid_n": GRID_N,
                "grid_half_waist": GRID_HALF,
                "dx": dx,
                "dy": dy,
            },
            "skyrmion_definition": (
                "N_sk=(1/4π)∬ n·(∂x n × ∂y n) dx dy; "
                "n=S/|S| from conditional Stokes after B→|+⟩; "
                "NOT an eigenvalue of the 4×4 density matrix"
            ),
            "conditional_projection": "|+⟩_B=(|0⟩+|1⟩)/√2",
            "channels": {
                "depolarizing": "ρ'=(1-ξ)ρ+(ξ/4)I_4",
                "phase_flip": "ρ'=(1-p)ρ + p (Z⊗I)ρ(Z⊗I); Z on skyrmion qubit A",
                "bit_phase_flip": "ρ'=(1-p)ρ + p (Y⊗I)ρ(Y⊗I); Y on skyrmion qubit A",
            },
            "xi_grid": [float(x) for x in XI_GRID],
            "p_grid": [float(x) for x in P_GRID],
            "zero_threshold_abs": ZERO_THR,
            "concurrence": "Wootters two-qubit",
            "discord": "D(A|B)=I(A:B)-max J; projective measure on B, Bloch angles optimized",
            "no_zhao_device_numbers_in_results": True,
            "no_chip_fabrication": True,
            "no_state_transfer_advantage": True,
            "not_merged_with_floquet": True,
        },
        "clean_limit": clean,
        "headline": {
            "clean_skyrmion_number": clean["skyrmion_number"],
            "clean_skyrmion_abs": clean["skyrmion_abs"],
            "clean_concurrence": clean["concurrence"],
            "clean_discord": clean["discord"],
            "clean_fidelity": clean["fidelity"],
            "clean_purity": clean["purity"],
            "ell": ELL,
            "waist": WAIST,
            "grid_n": GRID_N,
            "xi_range": [float(XI_GRID[0]), float(XI_GRID[-1])],
            "p_range": [float(P_GRID[0]), float(P_GRID[-1])],
            "vanish_depolarizing": z_depol,
            "vanish_phase_flip": z_phase,
            "vanish_bit_phase_flip": z_bit,
            "who_first_depolarizing": order_who_first(z_depol, "xi"),
            "who_first_phase_flip": order_who_first(z_phase, "p"),
            "who_first_bit_phase_flip": order_who_first(z_bit, "p"),
        },
        "sweeps": {
            "depolarizing": depol_rows,
            "phase_flip": phase_rows,
            "bit_phase_flip": bitphase_rows,
        },
        "literature_contrast_only": {
            "role": "仅对照",
            "note": "Zhao 新闻/实验数不得写入结果表",
            "zhao_skyrmion_approx": 1.981,
            "zhao_fidelity_avg_pct": 89,
            "zhao_purity_concurrence_zero": 0.34,
            "zhao_purity_skyrmion_drop": 0.25,
            "zhao_mix_ratio": 0.5,
        },
    }

    out = DATA / "summary.json"
    text = json.dumps(summary, indent=2, ensure_ascii=False) + "\n"
    out.write_text(text, encoding="utf-8")
    sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
    (DATA / "summary.sha256").write_text(sha + "\n", encoding="utf-8")
    print(f"[run_skyrmion_budget] wrote {out}")
    print(f"  clean N_sk={clean['skyrmion_number']:.6f} C={clean['concurrence']:.6f} D={clean['discord']:.6f}")
    print(f"  sha256={sha[:16]}...")
    for label, z in [
        ("depolarizing", z_depol),
        ("phase_flip", z_phase),
        ("bit_phase_flip", z_bit),
    ]:
        parts = []
        for k, v in z.items():
            if v["crossed"]:
                parts.append(f"{k}@{v['cross_x']}")
            else:
                parts.append(f"{k}:未到零")
        print(f"  {label}: " + ", ".join(parts))


if __name__ == "__main__":
    main()
