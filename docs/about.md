# About &amp; contact

## Development

This implementation is a development of **Jan Machaček**, **Leonardo José Cocco** and
**Marcin Cudny**, developed for and derived from the free finite-element software
<a href="https://www.numgeo.de/" target="_blank">numgeo</a>.

- **Leonardo José Cocco** provided the original Fortran UMAT implementation of the base Hardening Soil model (Cocco &amp; Ruiz 2018), which was modernized, refactored and optimized for the integration into numgeo as the base Hardening-Soil-MN model.
- **Marcin Cudny** kindly provided some base subroutines for the BRICK string properties and brick-movement mechanism (following Cudny &amp; Truty 2020), which were refactored in the same style and integrated into numgeo as the small-strain stiffness extension documented here.
- **Jan Machaček** is the developer and maintainer of numgeo and of this repository, and modernized, optimized both contributions for the integration into numgeo, the constitutive module, the incremental-driver wrapper, the calibration tool and the UMAT interface shipped here.

!!! info "Contact"
    **Jan Machaček** — <jan-machacek@outlook.com>

    **The numgeo team** — <https://www.numgeo.de/>

Questions, bug reports and feedback on this repository are welcome through either channel above.

---

## numgeo

<div class="hsb-grid" markdown>

<div class="hsb-card" markdown>
### The software
numgeo is a free finite-element framework for geotechnical engineering. The constitutive module shipped in this repository is developed for, and extracted from, numgeo. <br>
[:octicons-link-external-16: numgeo website](https://www.numgeo.de/) ·
[:octicons-book-16: numgeo documentation](https://j-machacek.github.io/numgeo/)
</div>

<div class="hsb-card" markdown>
### Using the model directly in numgeo
If you are already working in numgeo, the most convenient way to use the Hardening-Soil-MN-Bricks
model is directly through numgeo itself, where material-parameter input, state-variable
initialisation and output requests all follow the documented numgeo conventions. This repository
exists for users who specifically want the constitutive routine outside numgeo — in Abaqus, or in
a standalone element-test driver. <br>
[:octicons-arrow-right-16: numgeo reference manual](https://j-machacek.github.io/numgeo/2026-09/reference/material/mechanical/hardening_soil_MN_bricks.html){ target="_blank" }
</div>

</div>

---

## License &amp; availability

Copyright © 2026 Jan Machaček, Leonardo José Cocco, Marcin Cudny.

See the repository for the applicable license terms.
