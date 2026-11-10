# Model parameters

This page documents the `props`/`statev` array layout as used by the Fortran API in this
repository. For the meaning of the underlying physical quantities, see the
[theory manual](https://j-machacek.github.io/numgeo/2026-09/theory/constitutive-models/mechanical-models/hardening-soil-MN-bricks.html){ target="_blank" }.

All three components described under [Components](components/index.md) — the incremental driver,
the calibration tool and the UMAT interface — use exactly this layout.

---

## Model identifier

The model is selected by name:

```
Hardening-Soil-MN-Bricks
```

!!! note "Exact matching, not a substring search"
    `Hardening-Soil-MN` (the base model's identifier) is itself a prefix of
    `Hardening-Soil-MN-Bricks`. The dispatch code in `material_models.f90` and `umat.f90`
    therefore compares the **first whitespace-delimited token** of the material name exactly,
    rather than searching for it as a substring — a substring search would risk one model
    silently swallowing requests meant for the other.

---

## Material parameters (`props`)

The model requires **`nprops = 16`** parameters, in the following order:

| # | Symbol | Unit | Description |
|---|--------|------|-------------|
| 1 | `E50` | F/A | Secant stiffness at 50 % of the deviatoric strength (at `pref`) |
| 2 | `Eoed` | F/A | Oedometric (constrained) tangent stiffness (at `pref`) |
| 3 | `Eur` | F/A | Unloading/reloading stiffness (at `pref`); also sets $G_{ur}^{ref} = E_{ur}/2(1+\nu)$ |
| 4 | `m` | – | Exponent of the power-law stress dependency of stiffness |
| 5 | `c` | F/A | Cohesion |
| 6 | `phi` | deg | Friction angle (converted to radians internally) |
| 7 | `psi` | deg | Dilatancy angle (converted to radians internally) |
| 8 | `nu` | – | Unloading/reloading Poisson's ratio (assumed constant across the small-strain range) |
| 9 | `pref` | F/A | Reference stress for the stiffness laws |
| 10 | `K0nc` | – | Coefficient of lateral earth pressure for normal consolidation |
| 11 | `Rf` | – | Failure ratio $q_f / q_a$ |
| 12 | `Ei` | F/A | Initial loading stiffness (at `pref`) |
| 13 | `alpha` | – | Cap shape constant — **internal**, see [below](#the-internal-constants-alpha-and-hpp) |
| 14 | `Hpp` | – | Cap hardening modulus — **internal**, see [below](#the-internal-constants-alpha-and-hpp) |
| 15 | `gamma07` | – | Shear strain at which the small-strain secant shear modulus has decayed to 72.2 % of `G0` (Hardin–Drnevich threshold strain) |
| 16 | `G0` | F/A | Small-strain reference shear modulus (at `pref`), valid immediately after a strain reversal |

!!! warning "Parameter validity"
    `G0` must not be smaller than $G_{ur}^{ref}=E_{ur}/2(1+\nu)$. If `G0 > Gur_ref`, `gamma07`
    must be strictly positive. Setting `G0 = Gur_ref` degenerates the model exactly to the base
    Hardening Soil (MN) model — a convenient way to disable the small-strain extension without
    switching models. Both conditions are checked and enforced with a diagnostic `error stop` if
    violated.

---

## State variables (`statev`)

The model requires **`nstatev = 73`** state variables:

| # | Symbol | Description |
|---|--------|-------------|
| 1 | `void_ratio` | Reserved (not used by this model) |
| 2 | `gammapss` | Accumulated plastic shear strain measure $\gamma^p$ |
| 3 | `pp` | Preconsolidation stress / cap size $p_p$ |
| 4 | `p` | Current mean stress $p$ (output) |
| 5 | `q` | Current deviatoric stress $q$ (output) |
| 6 | `Gm` | Small-strain stiffness ratio $G_m$ (running minimum of $G_{ref,t}/G_{ur}^{ref}$, always $\ge 1$) |
| 7 | `n_bricks` | Number of currently active ("dragged") bricks, `0`–`10` — diagnostic only |
| 8–13 | `sn` | "Man" strain, tensorial shear components (order 11, 22, 33, 12, 13, 23) |
| 14–73 | `snb` | Brick anchor-point strains — 6 tensorial shear components per brick, 10 bricks |

All 73 state variables can be initialised to zero. On the very first increment of an analysis
(`kstep = 1`, `kinc = 1`) the model initialises `gammapss`/`pp` from the initial stress state (as
in the base model), and the BRICK state (variables 6–73) to the virgin small-strain condition:
`Gm = G0/Gur_ref`, no strings taut yet.

---

## Sign convention

Stress and strain follow the standard Abaqus/numgeo convention: **compression is negative**.
Voigt components are ordered `[11, 22, 33, 12, 13, 23]`.

---

## The internal constants `alpha` and `Hpp`

`props(13)` (`alpha`) and `props(14)` (`Hpp`) are **not independent physical inputs** — they are
internal cap constants, calibrated so that the model reproduces the prescribed `Eoed` and `K0nc`
under oedometric loading. They are obtained once, from the twelve primary parameters, with

```fortran
call optimize_hs_bricks_internal_constants(props, nprops)   ! fills props(13)=alpha, props(14)=Hpp
```

a routine provided directly by `numgeo_hardening_soil_MN_bricks_.f90`. It performs the identical
virtual-oedometer calibration as the base model, evaluated at the fully degraded (base-model)
stiffness — `gamma07`/`G0` (parameters 15/16) do not influence the result.

!!! info "Where this matters"
    This is exactly what the [calibration tool](components/calibration.md) automates, and it is
    why it exists as a separate, standalone program: computing `alpha`/`Hpp` runs a small Newton
    iteration that is only meant to be executed **once per parameter set** — not automatically on
    every element/integration point, which is why the [UMAT interface](components/umat.md)
    deliberately does *not* calibrate automatically (see that page for details).
