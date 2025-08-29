# opstool
*Pre-Processing, Post-Processing, and Visualization Tailored for OpenSeesPy and OpenSees*

[![pypi](https://img.shields.io/pypi/v/opstool)](https://pypi.org/project/opstool/)
[![Downloads](https://static.pepy.tech/badge/opstool)](https://pepy.tech/project/opstool)
[![Documentation Status](https://readthedocs.org/projects/opstool/badge/?version=latest)](https://opstool.readthedocs.io/en/latest/?badge=latest)
[![github stars](https://img.shields.io/github/stars/yexiang1992/opstool?style=social)](https://github.com/yexiang1992/opstool)
[![GitHub License](https://img.shields.io/github/license/yexiang1992/opstool?style=flat)](https://img.shields.io/github/license/yexiang1992/opstool?style=flat)
[![CodeFactor](https://www.codefactor.io/repository/github/yexiang92/opstool/badge)](https://www.codefactor.io/repository/github/yexiang92/opstool)

``opstool`` is a powerful and user-friendly package designed to simplify and enhance structural analysis workflows 
with [OpenSees](https://opensees.berkeley.edu/) and [OpenSeesPy](https://openseespydoc.readthedocs.io/en/latest/). 
It provides advanced tools for preprocessing, postprocessing, and visualization, making structural 
simulations more efficient and accessible.


## Installation
The package is still under development.
To use, install `opstool` from [opstool-PyPI](https://pypi.org/project/opstool/):

```bash
pip install --upgrade opstool
```

The restriction on the python version mainly depends on `openseespy`,
it is recommended that you use [Miniconda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html) or [Anaconda Distribution](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html) to avoid library version incompatibilities.

After installing, open Anaconda Prompt to execute the following code:
```bash
conda create -n opensees python=3.12 numpy scipy pandas xarray notebook matplotlib
conda activate opensees
pip install openseespy
pip install opstool
```

![image.png](https://s2.loli.net/2025/07/12/WIkihvDXMKBcwJF.png)

* The first line of code will create an environment called ``opensees`` and install Python 3.12 and libraries such as numpy, scipy, pandas, xarray, notebook, matplotlib, etc. 
* Please use ``conda activate opensees`` to activate the environment, and then you can install various third-party packages in the environment, such as ``pip install openseespy`` and ``pip install opstool``.
* You can also install the packages from [anaconda / packages](https://anaconda.org/anaconda/repo), such as ``conda install conda-forge::scikit-learn``.



## Document

**Latest**: See [https://opstool.readthedocs.io/en/latest/](https://opstool.readthedocs.io/en/latest/).

**Stable**: See [https://opstool.readthedocs.io/en/stable/](https://opstool.readthedocs.io/en/stable/)

> [!TIP]
> Since an opstool version **v1.0.1**, the API and features have undergone significant changes and upgrades. As a result, it feels more like a new library, and you should take some time to familiarize yourself with the new interface usage.



## Citing

If you use `opstool` in your work, please cite the following publication:

Yexiang Yan and Yazhou Xie. *"opstool: A Python library for OpenSeesPy analysis automation, streamlined pre-and post-processing, and enhanced data visualization."* SoftwareX 30 (2025): 102126.
DOI: [https://doi.org/10.1016/j.softx.2025.102126](https://www.sciencedirect.com/science/article/pii/S2352711025000937)

## Key Features

1. **Preprocessing Tools**:
   - *Fiber Section Meshing*: Generate detailed fiber meshes for various geometries.
      - <a href="https://opstool.readthedocs.io/en/latest/src/pre/sec_mesh.html" target="_blank"><img src="https://s2.loli.net/2025/07/12/thTxbWLXoeFrq2d.png" height="200"></a> 
        <a href="https://opstool.readthedocs.io/en/latest/examples/section.mesh/composite_mesh.html" target="_blank"><img src="https://s2.loli.net/2025/02/09/nIxAhN8rLBEQi2t.png" height="200"></a>
   - *GMSH Integration*: Import and convert [Gmsh](https://gmsh.info/) models, including geometry, mesh, and physical groups.
      - <a href="https://opstool.readthedocs.io/en/latest/src/pre/read_gmsh.html" target="_blank"><img src="https://s2.loli.net/2025/02/09/MjoviYLrtqNHKCO.png" height="200"></a>
        <a href="https://opstool.readthedocs.io/en/latest/examples/pre/read_gmsh2.html" target="_blank"><img src="https://s2.loli.net/2025/02/09/XBVvRcGnePsJK8A.png" height="200"></a>
   - *Unit System Management*: Ensure consistency with automatic unit conversions.
   - *Mass Generation*: Automate lumped mass calculations.
2. **Postprocessing Capabilities**:
   - Easy retrieval and interpretation of analysis results using [xarray](https://docs.xarray.dev/en/stable/index.html#).
     - <a href="https://opstool.readthedocs.io/en/latest/src/post/index.html" target="_blank"><img src="https://s2.loli.net/2025/02/09/Q3OV9FLR5oGPMdn.png" height="160"></a>
       <a href="https://opstool.readthedocs.io/en/latest/examples/post/excavation/test_excavation.html" target="_blank"><img src="https://s2.loli.net/2025/02/09/HzkTF7xdav6eLOt.gif" height="200"></a>
3. **Visualization**:
   - Powered by [Pyvista](https://docs.pyvista.org/) (VTK-based) and [Plotly](https://plotly.com/python/) (web-based).
   - Nearly identical APIs for flexible visualization of model geometry, modal analysis, and simulation results.
   - Supports most common OpenSees elements.
   - <a href="https://opstool.readthedocs.io/en/latest/src/vis/plot_model_plotly.html" target="_blank"><img src="https://s2.loli.net/2025/02/09/HrzPk1cqSJyxTlY.png" height="160"></a>
     <a href="https://opstool.readthedocs.io/en/latest/src/vis/plot_eigen_plotly.html" target="_blank"><img src="https://s2.loli.net/2025/02/09/gxy8LZPkAwa3QEI.png" height="160"></a>
     <a href="https://opstool.readthedocs.io/en/latest/src/vis/plot_nodal_resp_plotly.html" target="_blank"><img src="https://s2.loli.net/2025/02/09/LCqVG9Df7RmHou6.png" height="160"></a>
     <a href="https://opstool.readthedocs.io/en/latest/src/vis/plot_brick_resp_plotly.html" target="_blank"><img src="https://s2.loli.net/2025/07/12/raBmf6uP2RdKE73.png" ></a>
     <a href="https://opstool.readthedocs.io/en/latest/src/vis/plot_shell_resp_plotly.html" target="_blank"><img src="https://s2.loli.net/2025/02/09/lcw5rXuaAKHCB3g.png" height="200"></a>
     <a href="https://opstool.readthedocs.io/en/latest/src/vis/plot_truss_resp_pyvista.html" target="_blank"><img src="https://s2.loli.net/2025/02/09/Rp2icyNbFgZOa6Y.png" height="200"></a>
4. **Intelligent Analysis**:
   - Features like automatic step size adjustment and algorithm switching to optimize simulation workflows.
   See [Smart Analysis](https://opstool.readthedocs.io/en/latest/src/analysis/smart_analysis.html).
   - Moment-Curvature Analysis: Generate moment-curvature curves for various sections.
     - <a href="https://opstool.readthedocs.io/en/latest/src/analysis/mc_analysis.html" target="_blank"><img src="https://s2.loli.net/2025/02/09/mlNHEbfuoIzehri.png" height="200"></a>
       <a href="https://opstool.readthedocs.io/en/latest/src/analysis/mc_analysis.html" target="_blank"><img src="https://s2.loli.net/2025/02/09/9MFf4JQrZVpv6bi.png" height="200"></a>

## Why Choose opstool?

- **Efficiency**: Streamlines complex workflows, reducing time spent on repetitive tasks.
- **Flexibility**: Provides nearly identical interfaces for different visualization engines.
- **Accessibility**: Makes advanced structural analysis tools like OpenSeesPy more approachable to users of all levels.

``opstool`` is actively evolving, with continuous additions of new features planned for the future.
With ``opstool``, you can focus on what matters most: 
understanding and solving your structural engineering challenges. 
Whether you are building models, visualizing results, or interpreting data, 
``opstool`` is your go-to solution for OpenSeesPy workflows.

> [!NOTE]  
> This project is a non-profit open-source initiative. Use at your own risk.

## License

This software is published under the [GPLv3 license](https://www.gnu.org/licenses/gpl-3.0.en.html).
