Different grid versions
=======================

**SMECV_Grid_v042** : Grid used in the generation of ESA CCI SM v4.x / C3S SM v201x.x.x data.
Global quarter degree grid, with 5 degree cell partitioning, contains masks
for landpoints and rainforest areas as defined in ``src/smecv_grid/definition_files/ESA-CCI-SOILMOISTURE-LAND_AND_RAINFOREST_MASK-fv04.2.nc``.

**SMECV_Grid_v052** : Grid used in the generation of ESA CCI SM v5.x / C3S SM v202x.x.x data.
Global quarter degree grid, with 5 degree cell partitioning, contains masks
for landpoints, rainforests, multiple landcover/climate classes and
high VOD (based on AMSR-E VOD) regions as defined in ``src/smecv_grid/definition_files/ESA-CCI-SOILMOISTURE-LAND_AND_RAINFOREST_MASK-fv05.2.nc``.
Compared to v4 grid, the latitudes and gpis in the grid are sorted differently, this means that

.. code::

    >> SMECV_Grid_v052(None).activegpis[0]
    0

    >> SMECV_Grid_v052(None).find_nearest_gpi(-100.375,38.375)[0]
    739038

    >> SMECV_Grid_v052(None).arrlat[739038]
    38.375

while in the old version

.. code::

    >> SMECV_Grid_v042(None).activegpis[0]
    1035360

    >> SMECV_Grid_v042(None).find_nearest_gpi(-100.375,38.375)[0]
    739038

    >> SMECV_Grid_v042(None).arrlat[739038]
    -38.375

But in both cases

.. code::

    >> SMECV_Grid_v042('land').find_nearest_gpi(16.3,48.1) == SMECV_Grid_v052('land').find_nearest_gpi(16.3,48.1)
    True

    >> SMECV_Grid_v042('land').gpi2cell(795665) == SMECV_Grid_v052('land').gpi2cell(795665) == 1431
    True