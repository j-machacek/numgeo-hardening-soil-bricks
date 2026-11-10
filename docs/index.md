# numgeo-hardening-soil-bricks { .hsb-center }

<p align="center">
  <img src="./assets/numgeo-hs-logo.png" class="hsb-logo"/>
</p>

<div class="hsb-hero" markdown>

<p class="hsb-tagline" markdown>
A standalone Fortran implementation of the **Hardening Soil (Matsuoka-Nakai, Bricks)**
constitutive model — the Hardening Soil model with a Matsuoka–Nakai failure surface and the
**BRICK small-strain stiffness extension** of Cudny &amp; Truty (2020). Extracted from
<a href="https://www.numgeo.de/" target="_blank">numgeo</a> and packaged for element testing,
calibration and Abaqus/UMAT use.
</p>

<div class="hsb-cta" markdown>
[Components overview](components/index.md){ .md-button .md-button--primary }
[Theory](theory.md){ .md-button }
[Building the code](building.md){ .md-button }
[Examples](examples.md){ .md-button }
</div>

</div>

<hr class="hsb-rule">

## Three things are shipped

This repository packages the same, unmodified constitutive module three different ways, so you
can use it in whichever environment fits your workflow:

<div class="hsb-grid" markdown>

<div class="hsb-card" markdown>
### :material-play-box-outline: Incremental driver
<span class="hsb-badge">Element tests</span><br>
A ready-to-use build of A. Niemunis' famous **incrementalDriver**, for quick, single-element
simulations of laboratory tests (oedometer, triaxial, ...) without setting up a full boundary-value
problem. <br>
[:octicons-arrow-right-16: Details](components/incremental-driver.md)
</div>

<div class="hsb-card" markdown>
### :material-tune-variant: Calibration tool
<span class="hsb-badge">alpha &amp; Hpp</span><br>
A small helper program that calibrates the model's internal cap constants `alpha` and `Hpp`
from the primary material parameters — especially helpful when using the model in **Abaqus**,
where automatic calibration inside the material routine is not available. <br>
[:octicons-arrow-right-16: Details](components/calibration.md)
</div>

<div class="hsb-card" markdown>
### :material-cube-outline: UMAT (Abaqus) interface
<span class="hsb-badge">Abaqus</span><br>
A minimal, self-contained **UMAT** library — just four Fortran files — that plugs the model
straight into an Abaqus user-material build, with no dependency on the driver or example
infrastructure. <br>
[:octicons-arrow-right-16: Details](components/umat.md)
</div>

</div>

<hr class="hsb-rule">

## How the pieces fit together

All three tools link the same two files: the constitutive module itself and a small
compatibility layer that supplies the stress-invariant and matrix helper routines it needs.
Nothing in the constitutive model differs between the three — only the surrounding driver code
that calls it does, which is why the [UMAT (Abaqus) vs. numgeo](validation/umat-vs-numgeo.md)
validation shows the same physics coming out of Abaqus as out of numgeo directly.

```mermaid
flowchart LR
    M["numgeo_hardening_soil_MN_bricks_.f90<br/>(constitutive module)"] --> A
    C["compatibility_numgeo_.f90<br/>+ precision_.f90"] --> A{{shared by all three}}
    A --> D["incrementalDriver.f<br/>+ material_models.f90"]
    A --> E["calibrate_hs_bricks.f90"]
    A --> F["user.for + umat.f90<br/>+ sdvini.f90"]
    D --> D2["Element-test simulations"]
    E --> E2["alpha, Hpp"]
    F --> F2["Abaqus analyses"]
```

## Theory

The full theoretical background — stress measures, the Matsuoka–Nakai shear cone, the
elliptical cap, the BRICK small-strain formulation, hardening laws and the internal
calibration procedure — is documented on the numgeo documentation site and is **not** repeated
here.

!!! abstract "Theory & equations"
    [:octicons-book-16: Hardening Soil (MN, Bricks) — theory manual](https://j-machacek.github.io/numgeo/2026-09/theory/constitutive-models/mechanical-models/hardening-soil-MN-bricks.html){ target="_blank" }

    See the [Theory](theory.md) page for a short orientation, and [Model parameters](parameters.md)
    for how the theory's symbols map onto the `props`/`statev` arrays used by the code in this
    repository.

<hr class="hsb-rule">

## Development

<div class="hsb-grid" markdown>

<div class="hsb-card" markdown>
### Developed for numgeo
This implementation is a development of **Jan Machaček**, **Leonardo José Cocco** and
**Marcin Cudny**, developed for and derived from the free finite-element software
<a href="https://www.numgeo.de/" target="_blank">numgeo</a>. <br>
[:octicons-link-external-16: numgeo website](https://www.numgeo.de/) ·
[:octicons-book-16: numgeo docs](https://j-machacek.github.io/numgeo/)
</div>

<div class="hsb-card" markdown>
### Get in touch
Questions, issues or feedback are welcome — see [About &amp; contact](about.md) for details. <br>
[:octicons-arrow-right-16: About &amp; contact](about.md)
</div>

</div>
