==========
smecv_grid
==========

|ci| |cov| |pip| |doc|


.. |ci| image:: https://github.com/TUW-GEO/smecv-grid/actions/workflows/ci.yml/badge.svg?branch=master
   :target: https://github.com/TUW-GEO/smecv-grid/actions

.. |cov| image:: https://coveralls.io/repos/TUW-GEO/smecv-grid/badge.png?branch=master
  :target: https://coveralls.io/r/TUW-GEO/smecv-grid?branch=master

.. |pip| image:: https://badge.fury.io/py/smecv-grid.svg
    :target: http://badge.fury.io/py/smecv-grid

.. |doc| image:: https://readthedocs.org/projects/smecv-grid/badge/?version=latest
   :target: http://ismn.readthedocs.org/

Description
===========
Grid definition of the 0.25 degree Discrete Global Grid (DGG) used for the creation of the CCI
soil moisture products and the Copernicus Climate Change Service products.

Full Documentation
==================
For the `full documentation  <http://smecv-grid.readthedocs.io/en/latest>`_,
click on the docs-badge at the top.

Installation
============

The package is available on pypi and can be installed via pip:

.. code::

    pip install smecv_grid


Loading and using the SMECV grid
================================

The smecv_grid package contains the global quarter degree (0.25x0.25 DEG) grid
definition, used for organising the ESA CCI SM and C3S SM data products.
It contains masks for:

- Land Points (default)
- Dense Vegetation (AMSR-E LPRMv6 VOD>0.526),
- Rainforest Areas
- One or multiple ESA CCI LC classes (reference year 2010)
- One or multiple Koeppen-Geiger climate classes (`Peel et al. 2007 <https://www.hydrol-earth-syst-sci.net/11/1633/2007/>`_, DOI:10.5194/hess-11-1633-2007).

For more information on grid definitions and the usage of grids in general, we refer to
the `pygeogrids package <https://github.com/TUW-GEO/pygeogrids>`_ in the background.


Loading the grid
----------------

For loading the grid, simply run the following code. Then use it as described
in `pygeogrids <https://github.com/TUW-GEO/pygeogrids>`_

.. code-block:: python

    from smecv_grid import SMECV_Grid_v052
    # Load a global grid
    glob_grid = SMECV_Grid_v052(subset_flag=None)
    # Load a land grid
    land_grid = SMECV_Grid_v052(subset_flag='land')
    # Load a rainforest grid
    rainforest_grid = SMECV_Grid_v052(subset_flag='rainforest')
    # Load grid with points where VOD > 0.526 (based on AMSR-E VOD)
    dense_vegetation_grid = SMECV_Grid_v052(subset_flag='high_vod')
    # Load a grid with points over urban areas
    urban_grid = SMECV_Grid_v052(subset_flag='landcover_class', subset_value=190.)
    # Load a landcover with points over grassland areas
    grassland_grid = SMECV_Grid_v052(subset_flag='landcover_class',
        subset_value=[120., 121., 122., 130., 180.])
    # Load a climate grid with points over tropical areas
    tropical_grid = SMECV_Grid_v052(subset_flag='climate_class',
        subset_value=[0., 1., 2.])

To see all available classes and subset values see tables on implemented
`ESA CCI LC <https://smecv-grid.readthedocs.io/en/latest/?badge=latest#esa-cci-land-cover-classes>`_
and `KG Climate classes <https://smecv-grid.readthedocs.io/en/latest/?badge=latest#kg-climate-classification>`_
