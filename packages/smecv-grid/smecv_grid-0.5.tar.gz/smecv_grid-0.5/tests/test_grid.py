# -*- coding: utf-8 -*-
# The MIT License (MIT)
#
# Copyright (c) 2020, TU Wien
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import numpy as np
from smecv_grid import SMECV_Grid_v042, SMECV_Grid_v052, SMECV_Grid_MR_v01
import pytest


@pytest.mark.parametrize("SMECV_Grid, gpi, size, activesize",
                         [(SMECV_Grid_v042, 739040, 1036800, 244243,),
                          (SMECV_Grid_v052, 739040, 1036800, 244243,),
                          (SMECV_Grid_MR_v01, 4619601, 6480000, 1526598,), ])
def test_SMECV_Grid_land(SMECV_Grid, gpi, size, activesize):
    grid = SMECV_Grid(subset_flag='land')
    gp, dist = grid.find_nearest_gpi(-99.87, 38.37)
    assert gp == gpi
    lon, lat = grid.gpi2lonlat(gp)
    np.testing.assert_almost_equal([lon], [-99.875], 1)
    np.testing.assert_almost_equal([lat], [38.375], 1)
    assert grid.gpi2cell(gp) == 601
    assert grid.gpis.size == size
    assert grid.activegpis.size == activesize


@pytest.mark.parametrize("SMECV_Grid", [SMECV_Grid_v042, SMECV_Grid_v052])
def test_SMECV_Grid_global(SMECV_Grid):
    grid = SMECV_Grid(subset_flag=None)
    gp, dist = grid.find_nearest_gpi(-99.87, 38.37)
    assert gp == 739040
    lon, lat = grid.gpi2lonlat(739040)
    assert lon == -99.875
    assert lat == 38.375
    assert grid.gpi2cell(739040) == 601
    assert grid.gpis.size == 1036800
    assert grid.activegpis.size == 1036800


@pytest.mark.parametrize("SMECV_Grid", [SMECV_Grid_v042, SMECV_Grid_v052])
def test_SMECV_Grid_rainforest(SMECV_Grid):
    grid = SMECV_Grid(subset_flag='rainforest')
    gp, dist = grid.find_nearest_gpi(27.44, -0.33)
    assert gp == 516349
    lon, lat = grid.gpi2lonlat(516349)
    assert lon == 27.375
    assert lat == -0.375
    assert grid.gpi2cell(516349) == 1493
    assert grid.gpis.size == 1036800
    assert grid.activegpis.size == 14851


@pytest.mark.parametrize("SMECV_Grid", [SMECV_Grid_v052])
def test_SMECV_Grid_denseveg(SMECV_Grid):
    grid = SMECV_Grid(subset_flag='high_vod')
    gp, dist = grid.find_nearest_gpi(27.44, -0.33)
    assert gp == 516349
    lon, lat = grid.gpi2lonlat(516349)
    assert lon == 27.375
    assert lat == -0.375
    assert grid.gpi2cell(516349) == 1493
    assert grid.gpis.size == 1036800
    assert grid.activegpis.size == 33082
    assert grid.gpis[0] == 0
    assert grid.activegpis[0] == 922916


@pytest.mark.parametrize("SMECV_Grid", [SMECV_Grid_v052])
def test_SMECV_Grid_urban(SMECV_Grid):
    grid = SMECV_Grid(subset_flag='landcover_class', subset_value=190.)
    gp, dist = grid.find_nearest_gpi(139.65, 35.68)
    assert gp == 724158
    lon, lat = grid.gpi2lonlat(724158)
    assert lon == 139.625
    assert lat == 35.625
    assert grid.gpi2cell(724158) == 2293
    assert grid.gpis.size == 1036800
    assert grid.activegpis.size == 421
    assert grid.gpis[0] == 0
    assert grid.activegpis[0] == 890802


@pytest.mark.parametrize("SMECV_Grid", [SMECV_Grid_v052])
def test_SMECV_Grid_desert(SMECV_Grid):
    grid = SMECV_Grid(subset_flag='landcover_class', subset_value=[190., 200.])
    gp, dist = grid.find_nearest_gpi(9.375, 24.125)
    assert dist == 0.
    assert gp == 657397
    lon, lat = grid.gpi2lonlat(657397)
    assert lon == 9.375
    assert lat == 24.125
    assert grid.gpi2cell(657397) == 1354
    assert grid.gpis.size == 1036800
    assert grid.activegpis.size == 421 + 31162
    assert grid.gpis[0] == 0
    assert grid.activegpis[0] == 995442


@pytest.mark.parametrize("SMECV_Grid", [SMECV_Grid_v052])
def test_SMECV_Grid_tropical(SMECV_Grid):
    grid = SMECV_Grid(subset_flag='climate_class', subset_value=[0., 1., 2.])
    gp, dist = grid.find_nearest_gpi(-66.125, -8.125)
    assert gp == 471335
    assert dist == 0.
    lon, lat = grid.gpi2lonlat(471335)
    assert lon == -66.125
    assert lat == -8.125
    assert grid.gpi2cell(471335) == 808
    assert grid.gpis.size == 1036800
    assert grid.activegpis.size == 36949
    assert grid.gpis[0] == 0
    assert grid.activegpis[0] == 674205


@pytest.mark.parametrize("SMECV_Grid", [SMECV_Grid_v052])
def test_bbox_subgrid(SMECV_Grid):
    grid = SMECV_Grid('land')  # create land-subgrid for europe
    min_lon, min_lat, max_lon, max_lat = -11., 34., 43., 71.
    subgrid = grid.subgrid_from_bbox(min_lon, min_lat, max_lon, max_lat)
    assert all(subgrid.activearrlat >= min_lat) and all(subgrid.activearrlat <= max_lat)
    assert all(subgrid.activearrlon >= min_lon) and all(subgrid.activearrlon <= max_lon)
    assert subgrid.activegpis.size == 18408


@pytest.mark.parametrize("subset", [None, 'land'])
def test_bbox(subset):
    min_lon, min_lat, max_lon, max_lat = -11, 34, 43, 71

    grid = SMECV_Grid_v052(subset).subgrid_from_bbox(min_lon, min_lat, max_lon, max_lat)
    if subset == 'land':
        assert grid.shape == (18408,)
    else:
        assert grid.shape == (148, 216)

    assert all(np.diff(grid.activegpis) > 0)
    assert all(grid.activearrlon >= min_lon)
    assert all(grid.activearrlon <= max_lon)
    assert all(grid.activearrlat <= max_lat)
    assert all(grid.activearrlat >= min_lat)


def test_vers_diff():
    landgrid4, globgrid4 = SMECV_Grid_v042('land'), SMECV_Grid_v042(None)
    landgrid5, globgrid5 = SMECV_Grid_v052('land'), SMECV_Grid_v052(None)
    assert landgrid4.find_nearest_gpi(16.3, 48.1)[0] == landgrid5.find_nearest_gpi(16.3, 48.1)[0]
    assert landgrid4.gpi2cell(landgrid4.find_nearest_gpi(16.3, 48.1)[0]) == \
           landgrid5.gpi2cell(landgrid5.find_nearest_gpi(16.3, 48.1)[0])
    assert landgrid5.arrlat[546546] == -1 * landgrid4.arrlat[546546]  # because lats got flipped
    assert globgrid5.activegpis[0] == 0
    assert globgrid5.activearrcell[0] == 0
    assert globgrid4.activegpis[0] == 1035360
    assert globgrid4.activearrcell[0] == 35

    # the differences are not affecting pygeogrids equals function
    assert globgrid4 == globgrid5
    assert landgrid4 == landgrid5
    assert SMECV_Grid_v042('rainforest') == SMECV_Grid_v052('rainforest')
