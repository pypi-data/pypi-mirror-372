Commands after loading the grid
===============================

The smecv-grid inherits from the `pygeogrids CellGrid <https://github.com/TUW-GEO/pygeogrids/blob/366c6a456e1bb360768b49b6c94c6bf4ae311611/pygeogrids/grids.py#L720>`_.
For details on available functions, see the `pygeogrids docs <https://pygeogrids.readthedocs.io/en/latest/examples.html>`_.
Some of the main functions that pygeogrids provides are:

.. code-block:: python

    from smecv_grid import SMECV_Grid_v052
    # Load a land grid
    landgrid = SMECV_Grid_v052(subset_flag='land')

.. code-block:: python

    >>> landgrid.get_grid_points() # returns GPIs, Lons, Lats and Cells
    (masked_array(data=[196291, 197727, 197730, ..., 999942, 999943, 999944], mask=False, fill_value=999999),
     masked_array(data=[-67.125, -68.125, -67.375, ..., -34.375, -34.125, -33.875], mask=False, fill_value=1e+20),
     masked_array(data=[-55.875, -55.625, -55.625, ...,  83.625,  83.625, 83.625], mask=False, fill_value=1e+20),
     masked_array(data=[ 798,  798,  798, ..., 1078, 1078, 1078], mask=False, fill_value=999999, dtype=int16))

    >> landgrid.gpi2cell(795665) # returns the cell of a GPI
    1431

    >> landgrid.gpi2lonlat(795665) # returns the coordinates of a GPI
    (16.375, 48.125)

    >> landgrid.find_nearest_gpi(16.375, 48.125) # find the closest GPI in the grid.
    (795665, 0.0)

    >> gpis, lons, lats = landgrid.grid_points_for_cell(1431) # get all points for a cell

