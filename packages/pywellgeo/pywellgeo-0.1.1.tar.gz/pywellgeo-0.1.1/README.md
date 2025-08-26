# PyWellGeo

**PyWellGeo** is a Python library for advanced well trajectory modeling, well data handling, and geothermal engineering workflows.  
It provides tools for representing, analyzing, and visualizing complex well architectures, including multi-branch wells, and supports a variety of input formats and engineering calculations.

## Features

- Flexible well trajectory modeling (vertical, deviated, multi-branch)
- Well data utilities (water properties, constants, DC1D well models)
- Well tree structures for advanced branching and perforation logic
- Geometric transformations (azimuth/dip, vector math)
- Integration with geothermal techno-economic workflows

### Reference in the literature

The PyWellGeo has been used in:
 
Barros, E.G.D.; Szklarz, S.P.; Khoshnevis Gargar, N.; Wollenweber, J.; van Wees, J.D. Optimization of Well Locations and Trajectories: Comparing Sub-Vertical, Sub-Horizontal and Multi-Lateral Well Concepts for Marginal Geothermal Reservoir in The Netherlands. Energies 2025, 18, 627. [DOI](https://doi.org/10.3390/en18030627)

## Installation

Install the latest version using pip:

```sh
pip install pywellgeo
```

Or install from source:

```sh
git clone https://github.com/TNO/pywellgeo.git
cd pywellgeo
pip install .
```

## Usage Examples

### Load and Work with a Well Trajectory

```python
from pywellgeo.welltrajectory.trajectory import Trajectory

# Create a trajectory from survey data or parameters
traj = Trajectory.from_xyz(
    x=[0, 100, 200],
    y=[0, 0, 0],
    z=[0, -500, -1000]
)

print(traj.length())
print(traj.get_md_tvd())
```

### Use Well Data Utilities

```python
from pywellgeo.well_data.names_constants import Constants

print(Constants.GRAVITY)
```

### Perform Azimuth/Dip Transformations

```python
from pywellgeo.transformations.azim_dip import AzimDip

azim, dip = AzimDip.vector_to_azim_dip([1, 1, -1])
print(f"Azimuth: {azim}, Dip: {dip}")
```

## Documentation

Full documentation is available at:  
[GitHub](https://github.com/TNO/pywellgeo)

## License

GNU General Public License v3 (GPLv3)

## Contact information

Stephan de Hoop (stephan.dehoop@tno.nl)

## Acknowledgements

This study has been performed as part of the RESULT project (Enhancing REServoirs in Urban deveLopmenT: smart wells and reservoir development). [RESULT](https://www.result-geothermica.eu/home.html) has been subsidized through the ERANET Cofund GEOTHERMICA (EC Project no. 731117), by the Ministry of Economic Affairs and Climate Policy (the Netherlands), Rannis (Iceland) and GSI (Ireland).

<p float="left">
  <img src="docs/logo/RESULT_LOGO.png" alt="RESULT Logo" width="15%" />
  <img src="docs/logo/GEOTHERMICA_LOGO.png" alt="GEOTHERMICA Logo" width="30%" />
</p>

---

For more examples and API details, see the [online documentation](https://tno.github.io/pywellgeo/).