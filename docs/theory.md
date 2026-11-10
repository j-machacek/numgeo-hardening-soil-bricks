# Theory

This page intentionally does **not** repeat the model's mathematical formulation — the full
theory is documented on the numgeo documentation site and is kept there as the single source of
truth, so that this repository's documentation and the numgeo documentation never drift apart.

!!! abstract "Hardening Soil (MN, Bricks) — theory manual"
    The complete derivation is given here:

    [:octicons-book-16: Hardening Soil (MN, Bricks) — numgeo theory manual](https://j-machacek.github.io/numgeo/2026-09/theory/constitutive-models/mechanical-models/hardening-soil-MN-bricks.html){ .md-button .md-button--primary target="_blank" }

    It covers, in order:

    - Stress measures, the shifted (cohesive) mean stress and the Matsuoka–Nakai shape factor
    - Stress-dependent elasticity
    - The shear (cone) and cap yield surfaces
    - Flow rules and the tensile-apex cut-off
    - **The BRICK small-strain stiffness extension**: the man/bricks/string-length mechanical
      analogy, the shear-strain invariant, the sub-incremented elastic predictor, and the
      hardening-enhancement factor $H_i$
    - Degeneration to the base Hardening Soil (MN) model
    - The internal calibration procedure for $\alpha$ and $H_{pp}$
    - The full `props`/`statev` array layout

---

## What's specific to this repository

The theory manual describes the *model*, independent of how it is called. What this repository
adds is purely plumbing: three different ways of calling the same, unmodified constitutive
routine.

<div class="hsb-grid" markdown>

<div class="hsb-card" markdown>
### Model parameters
The `props`/`statev` array layout, described from the point of view of this repository's Fortran
API (rather than numgeo's `*.inp` syntax). <br>
[:octicons-arrow-right-16: Model parameters](parameters.md)
</div>

<div class="hsb-card" markdown>
### Base model
The BRICK extension builds on the base Hardening Soil (MN) model — see its theory page for
everything not specific to small-strain stiffness. <br>
[:octicons-arrow-right-16: Hardening Soil (MN) — theory manual](https://j-machacek.github.io/numgeo/2026-09/theory/constitutive-models/mechanical-models/hardening-soil-MN.html){ target="_blank" }
</div>

</div>

!!! note "Attribution"
    The BRICK extension implemented here is based on Cudny &amp; Truty (2020) and the
    multi-surface concept of Simpson (1992). See [References](references.md) for full citations.
