"""
Deprecated unittests

(C) 2008-2011 by the GRASS Development Team
This program is free software under the GNU General Public
License (>=v2). Read the file COPYING that comes with GRASS
for details.

:authors: Soeren Gebbert
"""

import copy
from ctypes import byref
from datetime import datetime

from grass.lib import gis, rtree, vector
from grass.script import core

from .abstract_dataset import (
    AbstractDatasetComparisonKeyEndTime,
    AbstractDatasetComparisonKeyStartTime,
)
from .core import init
from .datetime_math import increment_datetime_by_string
from .space_time_datasets import RasterDataset
from .spatial_extent import SpatialExtent
from .spatio_temporal_relationships import SpatioTemporalTopologyBuilder
from .temporal_granularity import (
    adjust_datetime_to_granularity,
    compute_absolute_time_granularity,
)

# Uncomment this to detect the error
core.set_raise_on_error(True)

###############################################################################


def test_increment_datetime_by_string() -> None:
    # First test
    print("# Test 1")
    dt = datetime(2001, 9, 1, 0, 0, 0)
    string = "60 seconds, 4 minutes, 12 hours, 10 days, 1 weeks, 5 months, 1 years"

    dt1 = datetime(2003, 2, 18, 12, 5, 0)
    dt2 = increment_datetime_by_string(dt, string)

    print(dt)
    print(dt2)

    delta = dt1 - dt2

    if delta.days != 0 or delta.seconds != 0:
        core.fatal("increment computation is wrong %s" % (delta))

    # Second test
    print("# Test 2")
    dt = datetime(2001, 11, 1, 0, 0, 0)
    string = "1 months"

    dt1 = datetime(2001, 12, 1)
    dt2 = increment_datetime_by_string(dt, string)

    print(dt)
    print(dt2)

    delta = dt1 - dt2

    if delta.days != 0 or delta.seconds != 0:
        core.fatal("increment computation is wrong %s" % (delta))

    # Third test
    print("# Test 3")
    dt = datetime(2001, 11, 1, 0, 0, 0)
    string = "13 months"

    dt1 = datetime(2002, 12, 1)
    dt2 = increment_datetime_by_string(dt, string)

    print(dt)
    print(dt2)

    delta = dt1 - dt2

    if delta.days != 0 or delta.seconds != 0:
        core.fatal("increment computation is wrong %s" % (delta))

    # 4. test
    print("# Test 4")
    dt = datetime(2001, 1, 1, 0, 0, 0)
    string = "72 months"

    dt1 = datetime(2007, 1, 1)
    dt2 = increment_datetime_by_string(dt, string)

    print(dt)
    print(dt2)

    delta = dt1 - dt2

    if delta.days != 0 or delta.seconds != 0:
        core.fatal("increment computation is wrong %s" % (delta))


###############################################################################


def test_adjust_datetime_to_granularity() -> None:
    # First test
    print("Test 1")
    dt = datetime(2001, 8, 8, 12, 30, 30)
    result = adjust_datetime_to_granularity(dt, "5 seconds")
    correct = datetime(2001, 8, 8, 12, 30, 30)

    delta = correct - result

    if delta.days != 0 or delta.seconds != 0:
        core.fatal("Granularity adjustment computation is wrong %s" % (delta))

    # Second test
    print("Test 2")
    result = adjust_datetime_to_granularity(dt, "20 minutes")
    correct = datetime(2001, 8, 8, 12, 30, 0)

    delta = correct - result

    if delta.days != 0 or delta.seconds != 0:
        core.fatal("Granularity adjustment computation is wrong %s" % (delta))

    # Third test
    print("Test 2")
    result = adjust_datetime_to_granularity(dt, "20 minutes")
    correct = datetime(2001, 8, 8, 12, 30, 0)

    delta = correct - result

    if delta.days != 0 or delta.seconds != 0:
        core.fatal("Granularity adjustment computation is wrong %s" % (delta))

    # 4. test
    print("Test 4")
    result = adjust_datetime_to_granularity(dt, "3 hours")
    correct = datetime(2001, 8, 8, 12, 0, 0)

    delta = correct - result

    if delta.days != 0 or delta.seconds != 0:
        core.fatal("Granularity adjustment computation is wrong %s" % (delta))

    # 5. test
    print("Test 5")
    result = adjust_datetime_to_granularity(dt, "5 days")
    correct = datetime(2001, 8, 8, 0, 0, 0)

    delta = correct - result

    if delta.days != 0 or delta.seconds != 0:
        core.fatal("Granularity adjustment computation is wrong %s" % (delta))

    # 6. test
    print("Test 6")
    result = adjust_datetime_to_granularity(dt, "2 weeks")
    correct = datetime(2001, 8, 6, 0, 0, 0)

    delta = correct - result

    if delta.days != 0 or delta.seconds != 0:
        core.fatal("Granularity adjustment computation is wrong %s" % (delta))

    # 7. test
    print("Test 7")
    result = adjust_datetime_to_granularity(dt, "6 months")
    correct = datetime(2001, 8, 1, 0, 0, 0)

    delta = correct - result

    if delta.days != 0 or delta.seconds != 0:
        core.fatal("Granularity adjustment computation is wrong %s" % (delta))

    # 8. test
    print("Test 8")
    result = adjust_datetime_to_granularity(dt, "2 years")
    correct = datetime(2001, 1, 1, 0, 0, 0)

    delta = correct - result

    if delta.days != 0 or delta.seconds != 0:
        core.fatal("Granularity adjustment computation is wrong %s" % (delta))

    # 9. test
    print("Test 9")
    result = adjust_datetime_to_granularity(
        dt, "2 years, 3 months, 5 days, 3 hours, 3 minutes, 2 seconds"
    )
    correct = datetime(2001, 8, 8, 12, 30, 30)

    delta = correct - result

    if delta.days != 0 or delta.seconds != 0:
        core.fatal("Granularity adjustment computation is wrong %s" % (delta))

    # 10. test
    print("Test 10")
    result = adjust_datetime_to_granularity(dt, "3 months, 5 days, 3 minutes")
    correct = datetime(2001, 8, 8, 12, 30, 0)

    delta = correct - result

    if delta.days != 0 or delta.seconds != 0:
        core.fatal("Granularity adjustment computation is wrong %s" % (delta))

    # 11. test
    print("Test 11")
    result = adjust_datetime_to_granularity(dt, "3 weeks, 5 days")
    correct = datetime(2001, 8, 8, 0, 0, 0)

    delta = correct - result

    if delta.days != 0 or delta.seconds != 0:
        core.fatal("Granularity adjustment computation is wrong %s" % (delta))


###############################################################################


def test_compute_absolute_time_granularity() -> None:
    # First we test intervals
    print("Test 1")
    maps = []
    a = datetime(2001, 1, 1)
    increment = "1 year"
    for i in range(10):
        start = increment_datetime_by_string(a, increment, i)
        end = increment_datetime_by_string(a, increment, i + 1)
        map = RasterDataset(None)
        map.set_absolute_time(start, end)
        maps.append(map)

    gran = compute_absolute_time_granularity(maps)
    if increment != gran:
        core.fatal("Wrong granularity reference %s != gran %s" % (increment, gran))

    print("Test 2")
    maps = []
    a = datetime(2001, 1, 1)
    increment = "3 years"
    for i in range(10):
        start = increment_datetime_by_string(a, increment, i)
        end = increment_datetime_by_string(a, increment, i + 1)
        map = RasterDataset(None)
        map.set_absolute_time(start, end)
        maps.append(map)

    gran = compute_absolute_time_granularity(maps)
    if increment != gran:
        core.fatal("Wrong granularity reference %s != gran %s" % (increment, gran))

    print("Test 3")
    maps = []
    a = datetime(2001, 5, 1)
    increment = "1 month"
    for i in range(20):
        start = increment_datetime_by_string(a, increment, i)
        end = increment_datetime_by_string(a, increment, i + 1)
        map = RasterDataset(None)
        map.set_absolute_time(start, end)
        maps.append(map)

    gran = compute_absolute_time_granularity(maps)
    if increment != gran:
        core.fatal("Wrong granularity reference %s != gran %s" % (increment, gran))

    print("Test 4")
    maps = []
    a = datetime(2001, 1, 1)
    increment = "3 months"
    for i in range(20):
        start = increment_datetime_by_string(a, increment, i)
        end = increment_datetime_by_string(a, increment, i + 1)
        map = RasterDataset(None)
        map.set_absolute_time(start, end)
        maps.append(map)

    gran = compute_absolute_time_granularity(maps)
    if increment != gran:
        core.fatal("Wrong granularity reference %s != gran %s" % (increment, gran))

    print("Test 3")
    maps = []
    a = datetime(2001, 1, 1)
    increment = "1 day"
    for i in range(6):
        start = increment_datetime_by_string(a, increment, i)
        end = increment_datetime_by_string(a, increment, i + 1)
        map = RasterDataset(None)
        map.set_absolute_time(start, end)
        maps.append(map)

    gran = compute_absolute_time_granularity(maps)
    if increment != gran:
        core.fatal("Wrong granularity reference %s != gran %s" % (increment, gran))

    print("Test 4")
    maps = []
    a = datetime(2001, 1, 14)
    increment = "14 days"
    for i in range(6):
        start = increment_datetime_by_string(a, increment, i)
        end = increment_datetime_by_string(a, increment, i + 1)
        map = RasterDataset(None)
        map.set_absolute_time(start, end)
        maps.append(map)

    gran = compute_absolute_time_granularity(maps)
    if increment != gran:
        core.fatal("Wrong granularity reference %s != gran %s" % (increment, gran))

    print("Test 5")
    maps = []
    a = datetime(2001, 3, 1)
    increment = "1 month, 4 days"
    for i in range(20):
        start = increment_datetime_by_string(a, increment, i)
        end = increment_datetime_by_string(a, increment, i + 1)
        map = RasterDataset(None)
        map.set_absolute_time(start, end)
        maps.append(map)

    increment = "1 day"
    gran = compute_absolute_time_granularity(maps)
    if increment != gran:
        core.fatal("Wrong granularity reference %s != gran %s" % (increment, gran))

    print("Test 6")
    maps = []
    a = datetime(2001, 2, 11)
    increment = "1 days, 1 hours"
    for i in range(20):
        start = increment_datetime_by_string(a, increment, i)
        end = increment_datetime_by_string(a, increment, i + 1)
        map = RasterDataset(None)
        map.set_absolute_time(start, end)
        maps.append(map)

    increment = "25 hours"
    gran = compute_absolute_time_granularity(maps)
    if increment != gran:
        core.fatal("Wrong granularity reference %s != gran %s" % (increment, gran))

    print("Test 7")
    maps = []
    a = datetime(2001, 6, 12)
    increment = "6 hours"
    for i in range(20):
        start = increment_datetime_by_string(a, increment, i)
        end = increment_datetime_by_string(a, increment, i + 1)
        map = RasterDataset(None)
        map.set_absolute_time(start, end)
        maps.append(map)

    gran = compute_absolute_time_granularity(maps)
    if increment != gran:
        core.fatal("Wrong granularity reference %s != gran %s" % (increment, gran))

    print("Test 8")
    maps = []
    a = datetime(2001, 1, 1)
    increment = "20 minutes"
    for i in range(20):
        start = increment_datetime_by_string(a, increment, i)
        end = increment_datetime_by_string(a, increment, i + 1)
        map = RasterDataset(None)
        map.set_absolute_time(start, end)
        maps.append(map)

    gran = compute_absolute_time_granularity(maps)
    if increment != gran:
        core.fatal("Wrong granularity reference %s != gran %s" % (increment, gran))

    print("Test 9")
    maps = []
    a = datetime(2001, 1, 1)
    increment = "5 hours, 25 minutes"
    for i in range(20):
        start = increment_datetime_by_string(a, increment, i)
        end = increment_datetime_by_string(a, increment, i + 1)
        map = RasterDataset(None)
        map.set_absolute_time(start, end)
        maps.append(map)

    increment = "325 minutes"
    gran = compute_absolute_time_granularity(maps)
    if increment != gran:
        core.fatal("Wrong granularity reference %s != gran %s" % (increment, gran))

    print("Test 10")
    maps = []
    a = datetime(2001, 1, 1)
    increment = "5 minutes, 30 seconds"
    for i in range(20):
        start = increment_datetime_by_string(a, increment, i)
        end = increment_datetime_by_string(a, increment, i + 1)
        map = RasterDataset(None)
        map.set_absolute_time(start, end)
        maps.append(map)

    increment = "330 seconds"
    gran = compute_absolute_time_granularity(maps)
    if increment != gran:
        core.fatal("Wrong granularity reference %s != gran %s" % (increment, gran))

    print("Test 11")
    maps = []
    a = datetime(2001, 12, 31)
    increment = "60 minutes, 30 seconds"
    for i in range(24):
        start = increment_datetime_by_string(a, increment, i)
        end = increment_datetime_by_string(a, increment, i + 1)
        map = RasterDataset(None)
        map.set_absolute_time(start, end)
        maps.append(map)

    increment = "3630 seconds"
    gran = compute_absolute_time_granularity(maps)
    if increment != gran:
        core.fatal("Wrong granularity reference %s != gran %s" % (increment, gran))

    print("Test 12")
    maps = []
    a = datetime(2001, 12, 31, 12, 30, 30)
    increment = "3600 seconds"
    for i in range(24):
        start = increment_datetime_by_string(a, increment, i)
        end = increment_datetime_by_string(a, increment, i + 1)
        print(start)
        print(end)
        map = RasterDataset(None)
        map.set_absolute_time(start, end)
        maps.append(map)

    gran = compute_absolute_time_granularity(maps)
    if increment != gran:
        core.fatal("Wrong granularity reference %s != gran %s" % (increment, gran))

    # Test absolute time points

    print("Test 13")
    maps = []
    a = datetime(2001, 12, 31, 12, 30, 30)
    increment = "3600 seconds"
    for i in range(24):
        start = increment_datetime_by_string(a, increment, i)
        end = None
        map = RasterDataset(None)
        map.set_absolute_time(start, end)
        maps.append(map)

    gran = compute_absolute_time_granularity(maps)
    if increment != gran:
        core.fatal("Wrong granularity reference %s != gran %s" % (increment, gran))

    print("Test 14")
    maps = []
    a = datetime(2001, 12, 31, 0, 0, 0)
    increment = "20 days"
    for i in range(24):
        start = increment_datetime_by_string(a, increment, i)
        end = None
        map = RasterDataset(None)
        map.set_absolute_time(start, end)
        maps.append(map)

    gran = compute_absolute_time_granularity(maps)
    if increment != gran:
        core.fatal("Wrong granularity reference %s != gran %s" % (increment, gran))

    print("Test 15")
    maps = []
    a = datetime(2001, 12, 1, 0, 0, 0)
    increment = "5 months"
    for i in range(24):
        start = increment_datetime_by_string(a, increment, i)
        end = None
        map = RasterDataset(None)
        map.set_absolute_time(start, end)
        maps.append(map)

    gran = compute_absolute_time_granularity(maps)
    if increment != gran:
        core.fatal("Wrong granularity reference %s != gran %s" % (increment, gran))

    # Test absolute time interval and points

    print("Test 16")
    maps = []
    a = datetime(2001, 12, 31, 12, 30, 30)
    increment = "3600 seconds"

    for i in range(24):
        start = increment_datetime_by_string(a, increment, i)
        end = increment_datetime_by_string(a, increment, i + 1)
        map = RasterDataset(None)
        map.set_absolute_time(start, end)
        maps.append(map)

    a = datetime(2002, 2, 1, 12, 30, 30)
    for i in range(24):
        start = increment_datetime_by_string(a, increment, i)
        end = None
        map = RasterDataset(None)
        map.set_absolute_time(start, end)
        maps.append(map)

    gran = compute_absolute_time_granularity(maps)
    if increment != gran:
        core.fatal("Wrong granularity reference %s != gran %s" % (increment, gran))

    print("Test 17")
    maps = []
    a = datetime(2001, 1, 1)
    increment = "2 days"

    for i in range(8):
        start = increment_datetime_by_string(a, increment, i)
        end = increment_datetime_by_string(a, increment, i + 1)
        map = RasterDataset(None)
        map.set_absolute_time(start, end)
        maps.append(map)

    a = datetime(2001, 2, 2)
    for i in range(8):
        start = increment_datetime_by_string(a, increment, i)
        end = None
        map = RasterDataset(None)
        map.set_absolute_time(start, end)
        maps.append(map)

    gran = compute_absolute_time_granularity(maps)
    if increment != gran:
        core.fatal("Wrong granularity reference %s != gran %s" % (increment, gran))


###############################################################################


def test_spatial_extent_intersection() -> None:
    # Generate the extents

    A = SpatialExtent(north=80, south=20, east=60, west=10, bottom=-50, top=50)
    A.print_info()
    B = SpatialExtent(north=80, south=20, east=60, west=10, bottom=-50, top=50)
    B.print_info()
    C = A.intersect(B)
    C.print_info()

    if (
        C.get_north() != B.get_north()
        or C.get_south() != B.get_south()
        or C.get_west() != B.get_west()
        or C.get_east() != B.get_east()
        or C.get_bottom() != B.get_bottom()
        or C.get_top() != B.get_top()
    ):
        core.fatal("Wrong intersection computation")

    B = SpatialExtent(north=40, south=30, east=60, west=10, bottom=-50, top=50)
    B.print_info()
    C = A.intersect(B)
    C.print_info()

    if (
        C.get_north() != B.get_north()
        or C.get_south() != B.get_south()
        or C.get_west() != B.get_west()
        or C.get_east() != B.get_east()
        or C.get_bottom() != B.get_bottom()
        or C.get_top() != B.get_top()
    ):
        core.fatal("Wrong intersection computation")

    B = SpatialExtent(north=40, south=30, east=60, west=30, bottom=-50, top=50)
    B.print_info()
    C = A.intersect(B)
    C.print_info()

    if (
        C.get_north() != B.get_north()
        or C.get_south() != B.get_south()
        or C.get_west() != B.get_west()
        or C.get_east() != B.get_east()
        or C.get_bottom() != B.get_bottom()
        or C.get_top() != B.get_top()
    ):
        core.fatal("Wrong intersection computation")

    B = SpatialExtent(north=40, south=30, east=60, west=30, bottom=-30, top=50)
    B.print_info()
    C = A.intersect(B)
    C.print_info()

    if (
        C.get_north() != B.get_north()
        or C.get_south() != B.get_south()
        or C.get_west() != B.get_west()
        or C.get_east() != B.get_east()
        or C.get_bottom() != B.get_bottom()
        or C.get_top() != B.get_top()
    ):
        core.fatal("Wrong intersection computation")

    B = SpatialExtent(north=40, south=30, east=60, west=30, bottom=-30, top=30)
    B.print_info()
    C = A.intersect(B)
    C.print_info()

    if (
        C.get_north() != B.get_north()
        or C.get_south() != B.get_south()
        or C.get_west() != B.get_west()
        or C.get_east() != B.get_east()
        or C.get_bottom() != B.get_bottom()
        or C.get_top() != B.get_top()
    ):
        core.fatal("Wrong intersection computation")


###############################################################################


def test_spatial_relations() -> None:
    # Generate the extents

    A = SpatialExtent(north=80, south=20, east=60, west=10, bottom=-50, top=50)
    A.print_info()
    B = SpatialExtent(north=80, south=20, east=60, west=10, bottom=-50, top=50)
    B.print_info()

    relation = A.spatial_relation(B)
    print(relation)
    if relation != "equivalent":
        core.fatal("Wrong spatial relation: %s" % (relation))

    B = SpatialExtent(north=70, south=20, east=60, west=10, bottom=-50, top=50)
    B.print_info()

    relation = A.spatial_relation_2d(B)
    print(relation)
    if relation != "cover":
        core.fatal("Wrong spatial relation: %s" % (relation))

    relation = A.spatial_relation(B)
    print(relation)
    if relation != "cover":
        core.fatal("Wrong spatial relation: %s" % (relation))

    B = SpatialExtent(north=70, south=30, east=60, west=10, bottom=-50, top=50)
    B.print_info()

    relation = A.spatial_relation_2d(B)
    print(relation)
    if relation != "cover":
        core.fatal("Wrong spatial relation: %s" % (relation))

    relation = A.spatial_relation(B)
    print(relation)
    if relation != "cover":
        core.fatal("Wrong spatial relation: %s" % (relation))

    relation = B.spatial_relation_2d(A)
    print(relation)
    if relation != "covered":
        core.fatal("Wrong spatial relation: %s" % (relation))

    relation = B.spatial_relation(A)
    print(relation)
    if relation != "covered":
        core.fatal("Wrong spatial relation: %s" % (relation))

    B = SpatialExtent(north=70, south=30, east=50, west=10, bottom=-50, top=50)
    B.print_info()

    relation = A.spatial_relation_2d(B)
    print(relation)
    if relation != "cover":
        core.fatal("Wrong spatial relation: %s" % (relation))

    relation = B.spatial_relation_2d(A)
    print(relation)
    if relation != "covered":
        core.fatal("Wrong spatial relation: %s" % (relation))

    relation = A.spatial_relation(B)
    print(relation)
    if relation != "cover":
        core.fatal("Wrong spatial relation: %s" % (relation))

    B = SpatialExtent(north=70, south=30, east=50, west=20, bottom=-50, top=50)

    relation = B.spatial_relation(A)
    print(relation)
    if relation != "covered":
        core.fatal("Wrong spatial relation: %s" % (relation))

    B = SpatialExtent(north=70, south=30, east=50, west=20, bottom=-50, top=50)
    B.print_info()

    relation = A.spatial_relation_2d(B)
    print(relation)
    if relation != "contain":
        core.fatal("Wrong spatial relation: %s" % (relation))

    relation = A.spatial_relation(B)
    print(relation)
    if relation != "cover":
        core.fatal("Wrong spatial relation: %s" % (relation))

    B = SpatialExtent(north=70, south=30, east=50, west=20, bottom=-40, top=50)
    B.print_info()

    relation = A.spatial_relation(B)
    print(relation)
    if relation != "cover":
        core.fatal("Wrong spatial relation: %s" % (relation))

    B = SpatialExtent(north=70, south=30, east=50, west=20, bottom=-40, top=40)
    B.print_info()

    relation = A.spatial_relation(B)
    print(relation)
    if relation != "contain":
        core.fatal("Wrong spatial relation: %s" % (relation))

    relation = B.spatial_relation(A)
    print(relation)
    if relation != "in":
        core.fatal("Wrong spatial relation: %s" % (relation))

    B = SpatialExtent(north=90, south=30, east=50, west=20, bottom=-40, top=40)
    B.print_info()

    relation = A.spatial_relation_2d(B)
    print(relation)
    if relation != "overlap":
        core.fatal("Wrong spatial relation: %s" % (relation))

    relation = A.spatial_relation(B)
    print(relation)
    if relation != "overlap":
        core.fatal("Wrong spatial relation: %s" % (relation))

    B = SpatialExtent(north=90, south=5, east=70, west=5, bottom=-40, top=40)
    A.print_info()
    B.print_info()

    relation = A.spatial_relation_2d(B)
    print(relation)
    if relation != "in":
        core.fatal("Wrong spatial relation: %s" % (relation))

    relation = A.spatial_relation(B)
    print(relation)
    if relation != "overlap":
        core.fatal("Wrong spatial relation: %s" % (relation))

    B = SpatialExtent(north=90, south=5, east=70, west=5, bottom=-40, top=60)
    A.print_info()
    B.print_info()

    relation = A.spatial_relation(B)
    print(relation)
    if relation != "overlap":
        core.fatal("Wrong spatial relation: %s" % (relation))

    B = SpatialExtent(north=90, south=5, east=70, west=5, bottom=-60, top=60)
    A.print_info()
    B.print_info()

    relation = A.spatial_relation(B)
    print(relation)
    if relation != "in":
        core.fatal("Wrong spatial relation: %s" % (relation))

    A = SpatialExtent(north=80, south=60, east=60, west=10, bottom=-50, top=50)
    A.print_info()
    B = SpatialExtent(north=60, south=20, east=60, west=10, bottom=-50, top=50)
    B.print_info()

    relation = A.spatial_relation_2d(B)
    print(relation)
    if relation != "meet":
        core.fatal("Wrong spatial relation: %s" % (relation))

    relation = A.spatial_relation(B)
    print(relation)
    if relation != "meet":
        core.fatal("Wrong spatial relation: %s" % (relation))

    A = SpatialExtent(north=60, south=40, east=60, west=10, bottom=-50, top=50)
    A.print_info()
    B = SpatialExtent(north=80, south=60, east=60, west=10, bottom=-50, top=50)
    B.print_info()

    relation = A.spatial_relation_2d(B)
    print(relation)
    if relation != "meet":
        core.fatal("Wrong spatial relation: %s" % (relation))

    relation = A.spatial_relation(B)
    print(relation)
    if relation != "meet":
        core.fatal("Wrong spatial relation: %s" % (relation))

    A = SpatialExtent(north=80, south=40, east=60, west=40, bottom=-50, top=50)
    A.print_info()
    B = SpatialExtent(north=80, south=40, east=40, west=20, bottom=-50, top=50)
    B.print_info()

    relation = A.spatial_relation_2d(B)
    print(relation)
    if relation != "meet":
        core.fatal("Wrong spatial relation: %s" % (relation))

    relation = A.spatial_relation(B)
    print(relation)
    if relation != "meet":
        core.fatal("Wrong spatial relation: %s" % (relation))

    A = SpatialExtent(north=80, south=40, east=40, west=20, bottom=-50, top=50)
    A.print_info()
    B = SpatialExtent(north=90, south=30, east=60, west=40, bottom=-50, top=50)
    B.print_info()

    relation = A.spatial_relation_2d(B)
    print(relation)
    if relation != "meet":
        core.fatal("Wrong spatial relation: %s" % (relation))

    relation = A.spatial_relation(B)
    print(relation)
    if relation != "meet":
        core.fatal("Wrong spatial relation: %s" % (relation))

    A = SpatialExtent(north=80, south=40, east=40, west=20, bottom=-50, top=50)
    A.print_info()
    B = SpatialExtent(north=70, south=50, east=60, west=40, bottom=-50, top=50)
    B.print_info()

    relation = A.spatial_relation_2d(B)
    print(relation)
    if relation != "meet":
        core.fatal("Wrong spatial relation: %s" % (relation))

    relation = A.spatial_relation(B)
    print(relation)
    if relation != "meet":
        core.fatal("Wrong spatial relation: %s" % (relation))

    A = SpatialExtent(north=80, south=40, east=40, west=20, bottom=-50, top=50)
    A.print_info()
    B = SpatialExtent(north=60, south=20, east=60, west=40, bottom=-50, top=50)
    B.print_info()

    relation = A.spatial_relation_2d(B)
    print(relation)
    if relation != "meet":
        core.fatal("Wrong spatial relation: %s" % (relation))

    relation = A.spatial_relation(B)
    print(relation)
    if relation != "meet":
        core.fatal("Wrong spatial relation: %s" % (relation))

    A = SpatialExtent(north=80, south=40, east=40, west=20, bottom=-50, top=50)
    A.print_info()
    B = SpatialExtent(north=40, south=20, east=60, west=40, bottom=-50, top=50)
    B.print_info()

    relation = A.spatial_relation_2d(B)
    print(relation)
    if relation != "disjoint":
        core.fatal("Wrong spatial relation: %s" % (relation))

    relation = A.spatial_relation(B)
    print(relation)
    if relation != "disjoint":
        core.fatal("Wrong spatial relation: %s" % (relation))

    A = SpatialExtent(north=80, south=40, east=40, west=20, bottom=-50, top=50)
    A.print_info()
    B = SpatialExtent(north=60, south=20, east=60, west=40, bottom=-60, top=60)
    B.print_info()

    relation = A.spatial_relation(B)
    print(relation)
    if relation != "meet":
        core.fatal("Wrong spatial relation: %s" % (relation))

    A = SpatialExtent(north=80, south=40, east=40, west=20, bottom=-50, top=50)
    A.print_info()
    B = SpatialExtent(north=90, south=30, east=60, west=40, bottom=-40, top=40)
    B.print_info()

    relation = A.spatial_relation(B)
    print(relation)
    if relation != "meet":
        core.fatal("Wrong spatial relation: %s" % (relation))

    A = SpatialExtent(north=80, south=40, east=60, west=20, bottom=0, top=50)
    A.print_info()
    B = SpatialExtent(north=80, south=40, east=60, west=20, bottom=-50, top=0)
    B.print_info()

    relation = A.spatial_relation(B)
    print(relation)
    if relation != "meet":
        core.fatal("Wrong spatial relation: %s" % (relation))

    A = SpatialExtent(north=80, south=40, east=60, west=20, bottom=0, top=50)
    A.print_info()
    B = SpatialExtent(north=80, south=50, east=60, west=30, bottom=-50, top=0)
    B.print_info()

    relation = A.spatial_relation(B)
    print(relation)
    if relation != "meet":
        core.fatal("Wrong spatial relation: %s" % (relation))

    A = SpatialExtent(north=80, south=40, east=60, west=20, bottom=0, top=50)
    A.print_info()
    B = SpatialExtent(north=70, south=50, east=50, west=30, bottom=-50, top=0)
    B.print_info()

    relation = A.spatial_relation(B)
    print(relation)
    if relation != "meet":
        core.fatal("Wrong spatial relation: %s" % (relation))

    A = SpatialExtent(north=80, south=40, east=60, west=20, bottom=0, top=50)
    A.print_info()
    B = SpatialExtent(north=90, south=30, east=70, west=10, bottom=-50, top=0)
    B.print_info()

    relation = A.spatial_relation(B)
    print(relation)
    if relation != "meet":
        core.fatal("Wrong spatial relation: %s" % (relation))

    A = SpatialExtent(north=80, south=40, east=60, west=20, bottom=0, top=50)
    A.print_info()
    B = SpatialExtent(north=70, south=30, east=50, west=10, bottom=-50, top=0)
    B.print_info()

    relation = A.spatial_relation(B)
    print(relation)
    if relation != "meet":
        core.fatal("Wrong spatial relation: %s" % (relation))

    A = SpatialExtent(north=80, south=40, east=60, west=20, bottom=-50, top=0)
    A.print_info()
    B = SpatialExtent(north=80, south=40, east=60, west=20, bottom=0, top=50)
    B.print_info()

    relation = A.spatial_relation(B)
    print(relation)
    if relation != "meet":
        core.fatal("Wrong spatial relation: %s" % (relation))

    A = SpatialExtent(north=80, south=40, east=60, west=20, bottom=-50, top=0)
    A.print_info()
    B = SpatialExtent(north=80, south=50, east=60, west=30, bottom=0, top=50)
    B.print_info()

    relation = A.spatial_relation(B)
    print(relation)
    if relation != "meet":
        core.fatal("Wrong spatial relation: %s" % (relation))

    A = SpatialExtent(north=80, south=40, east=60, west=20, bottom=-50, top=0)
    A.print_info()
    B = SpatialExtent(north=70, south=50, east=50, west=30, bottom=0, top=50)
    B.print_info()

    relation = A.spatial_relation(B)
    print(relation)
    if relation != "meet":
        core.fatal("Wrong spatial relation: %s" % (relation))

    A = SpatialExtent(north=80, south=40, east=60, west=20, bottom=-50, top=0)
    A.print_info()
    B = SpatialExtent(north=90, south=30, east=70, west=10, bottom=0, top=50)
    B.print_info()

    relation = A.spatial_relation(B)
    print(relation)
    if relation != "meet":
        core.fatal("Wrong spatial relation: %s" % (relation))

    A = SpatialExtent(north=80, south=40, east=60, west=20, bottom=-50, top=0)
    A.print_info()
    B = SpatialExtent(north=70, south=30, east=50, west=10, bottom=0, top=50)
    B.print_info()

    relation = A.spatial_relation(B)
    print(relation)
    if relation != "meet":
        core.fatal("Wrong spatial relation: %s" % (relation))


###############################################################################


def test_temporal_topology_builder() -> None:
    map_listA = []

    map_ = RasterDataset(ident="1@a")
    map_.set_absolute_time(datetime(2001, 1, 1), datetime(2001, 2, 1))
    map_listA.append(copy.copy(map_))
    map_ = RasterDataset(ident="2@a")
    map_.set_absolute_time(datetime(2001, 2, 1), datetime(2001, 3, 1))
    map_listA.append(copy.copy(map_))
    map_ = RasterDataset(ident="3@a")
    map_.set_absolute_time(datetime(2001, 3, 1), datetime(2001, 4, 1))
    map_listA.append(copy.copy(map_))
    map_ = RasterDataset(ident="4@a")
    map_.set_absolute_time(datetime(2001, 4, 1), datetime(2001, 5, 1))
    map_listA.append(copy.copy(map_))
    map_ = RasterDataset(ident="5@a")
    map_.set_absolute_time(datetime(2001, 5, 1), datetime(2001, 6, 1))
    map_listA.append(copy.copy(map_))

    tb = SpatioTemporalTopologyBuilder()
    tb.build(map_listA)

    count = 0
    for map_ in tb:
        print("[%s]" % (map_.get_name()))
        map_.print_topology_info()
        if map_.get_id() != map_listA[count].get_id():
            core.fatal(
                "Error building temporal topology <%s> != <%s>"
                % (map_.get_id(), map_listA[count].get_id())
            )
        count += 1

    map_listB = []

    map_ = RasterDataset(ident="1@b")
    map_.set_absolute_time(datetime(2001, 1, 14), datetime(2001, 3, 14))
    map_listB.append(copy.copy(map_))
    map_ = RasterDataset(ident="2@b")
    map_.set_absolute_time(datetime(2001, 2, 1), datetime(2001, 4, 1))
    map_listB.append(copy.copy(map_))
    map_ = RasterDataset(ident="3@b")
    map_.set_absolute_time(datetime(2001, 2, 14), datetime(2001, 4, 30))
    map_listB.append(copy.copy(map_))
    map_ = RasterDataset(ident="4@b")
    map_.set_absolute_time(datetime(2001, 4, 2), datetime(2001, 4, 30))
    map_listB.append(copy.copy(map_))
    map_ = RasterDataset(ident="5@b")
    map_.set_absolute_time(datetime(2001, 5, 1), datetime(2001, 5, 14))
    map_listB.append(copy.copy(map_))

    tb = SpatioTemporalTopologyBuilder()
    tb.build(map_listB)

    # Probing some relations
    if map_listB[0].get_overlapped()[0] != map_listB[1]:
        core.fatal("Error building temporal topology")
    if map_listB[0].get_overlapped()[1] != map_listB[2]:
        core.fatal("Error building temporal topology")
    if map_listB[2].get_contains()[0] != map_listB[3]:
        core.fatal("Error building temporal topology")
    if map_listB[3].get_during()[0] != map_listB[2]:
        core.fatal("Error building temporal topology")

    count = 0
    for map_ in tb:
        print("[%s]" % (map_.get_map_id()))
        map_.print_topology_shell_info()
        if map_.get_id() != map_listB[count].get_id():
            core.fatal(
                "Error building temporal topology <%s> != <%s>"
                % (map_.get_id(), map_listB[count].get_id())
            )
        count += 1

    tb = SpatioTemporalTopologyBuilder()
    tb.build(map_listA, map_listB)

    count = 0
    for map_ in tb:
        print("[%s]" % (map_.get_map_id()))
        map_.print_topology_shell_info()
        if map_.get_id() != map_listA[count].get_id():
            core.fatal(
                "Error building temporal topology <%s> != <%s>"
                % (map_.get_id(), map_listA[count].get_id())
            )
        count += 1

    count = 0
    for map_ in map_listB:
        print("[%s]" % (map_.get_map_id()))
        map_.print_topology_shell_info()

    # Probing some relations
    if map_listA[3].get_follows()[0] != map_listB[1]:
        core.fatal("Error building temporal topology")
    if map_listA[3].get_precedes()[0] != map_listB[4]:
        core.fatal("Error building temporal topology")
    if map_listA[3].get_overlaps()[0] != map_listB[2]:
        core.fatal("Error building temporal topology")
    if map_listA[3].get_contains()[0] != map_listB[3]:
        core.fatal("Error building temporal topology")

    if map_listA[2].get_during()[0] != map_listB[1]:
        core.fatal("Error building temporal topology")
    if map_listA[2].get_during()[1] != map_listB[2]:
        core.fatal("Error building temporal topology")


###############################################################################


def test_map_list_sorting() -> None:
    map_list = []

    map_ = RasterDataset(ident="1@a")
    map_.set_absolute_time(datetime(2001, 2, 1), datetime(2001, 3, 1))
    map_list.append(copy.copy(map_))
    map_ = RasterDataset(ident="2@a")
    map_.set_absolute_time(datetime(2001, 1, 1), datetime(2001, 2, 1))
    map_list.append(copy.copy(map_))
    map_ = RasterDataset(ident="3@a")
    map_.set_absolute_time(datetime(2001, 3, 1), datetime(2001, 4, 1))
    map_list.append(copy.copy(map_))

    print("Original")
    for map_ in map_list:
        print(
            map_.get_temporal_extent_as_tuple()[0],
            map_.get_temporal_extent_as_tuple()[1],
        )
    print("Sorted by start time")
    new_list = sorted(map_list, key=AbstractDatasetComparisonKeyStartTime)
    for map_ in new_list:
        print(
            map_.get_temporal_extent_as_tuple()[0],
            map_.get_temporal_extent_as_tuple()[1],
        )

    if new_list[0] != map_list[1]:
        core.fatal("Sorting by start time failed")
    if new_list[1] != map_list[0]:
        core.fatal("Sorting by start time failed")
    if new_list[2] != map_list[2]:
        core.fatal("Sorting by start time failed")

    print("Sorted by end time")
    new_list = sorted(map_list, key=AbstractDatasetComparisonKeyEndTime)
    for map_ in new_list:
        print(
            map_.get_temporal_extent_as_tuple()[0],
            map_.get_temporal_extent_as_tuple()[1],
        )

    if new_list[0] != map_list[1]:
        core.fatal("Sorting by end time failed")
    if new_list[1] != map_list[0]:
        core.fatal("Sorting by end time failed")
    if new_list[2] != map_list[2]:
        core.fatal("Sorting by end time failed")


###############################################################################


def test_1d_rtree() -> None:
    """Testing the rtree ctypes wrapper"""

    tree = rtree.RTreeCreateTree(-1, 0, 1)

    for i in range(10):
        rect = rtree.RTreeAllocRect(tree)
        rtree.RTreeSetRect1D(rect, tree, float(i - 2), float(i + 2))
        rtree.RTreeInsertRect(rect, i + 1, tree)

    rect = rtree.RTreeAllocRect(tree)
    rtree.RTreeSetRect1D(rect, tree, 2.0, 7.0)

    list_ = gis.ilist()

    num = vector.RTreeSearch2(tree, rect, byref(list_))

    rtree.RTreeFreeRect(rect)

    # print rectangle ids
    print("Number of overlapping rectangles", num)
    for i in range(list_.n_values):
        print("id", list_.value[i])

    rtree.RTreeDestroyTree(tree)


###############################################################################


def test_2d_rtree() -> None:
    """Testing the rtree ctypes wrapper"""

    tree = rtree.RTreeCreateTree(-1, 0, 2)

    for i in range(10):
        rect = rtree.RTreeAllocRect(tree)

        rtree.RTreeSetRect2D(
            rect, tree, float(i - 2), float(i + 2), float(i - 2), float(i + 2)
        )
        rtree.RTreeInsertRect(rect, i + 1, tree)

    rect = rtree.RTreeAllocRect(tree)
    rtree.RTreeSetRect2D(rect, tree, 2.0, 7.0, 2.0, 7.0)

    list_ = gis.ilist()

    num = vector.RTreeSearch2(tree, rect, byref(list_))
    rtree.RTreeFreeRect(rect)

    # print rectangle ids
    print("Number of overlapping rectangles", num)
    for i in range(list_.n_values):
        print("id", list_.value[i])

    rtree.RTreeDestroyTree(tree)


###############################################################################


def test_3d_rtree() -> None:
    """Testing the rtree ctypes wrapper"""

    tree = rtree.RTreeCreateTree(-1, 0, 3)

    for i in range(10):
        rect = rtree.RTreeAllocRect(tree)
        rtree.RTreeSetRect3D(
            rect,
            tree,
            float(i - 2),
            float(i + 2),
            float(i - 2),
            float(i + 2),
            float(i - 2),
            float(i + 2),
        )
        rtree.RTreeInsertRect(rect, i + 1, tree)
        print(i + 1)
        rtree.RTreePrintRect(rect, 1, tree)

    rect = rtree.RTreeAllocRect(tree)
    rtree.RTreeSetRect3D(rect, tree, 2.0, 7.0, 2.0, 7.0, 2.0, 7.0)
    print("Select")
    rtree.RTreePrintRect(rect, 1, tree)

    list_ = gis.ilist()

    num = vector.RTreeSearch2(tree, rect, byref(list_))
    rtree.RTreeFreeRect(rect)

    # print rectangle ids
    print("Number of overlapping rectangles", num)
    for i in range(list_.n_values):
        print("id", list_.value[i])

    rtree.RTreeDestroyTree(tree)


###############################################################################


def test_4d_rtree() -> None:
    """Testing the rtree ctypes wrapper"""

    tree = rtree.RTreeCreateTree(-1, 0, 4)

    for i in range(10):
        # Allocate the boundary
        rect = rtree.RTreeAllocRect(tree)
        rtree.RTreeSetRect4D(
            rect,
            tree,
            float(i - 2),
            float(i + 2),
            float(i - 2),
            float(i + 2),
            float(i - 2),
            float(i + 2),
            float(i - 2),
            float(i + 2),
        )
        rtree.RTreeInsertRect(rect, i + 1, tree)

    rect = rtree.RTreeAllocRect(tree)
    rtree.RTreeSetRect4D(rect, tree, 2.0, 7.0, 2.0, 7.0, 2.0, 7.0, 2.0, 7.0)

    list_ = gis.ilist()

    num = vector.RTreeSearch2(tree, rect, byref(list_))

    rtree.RTreeFreeRect(rect)

    # print rectangle ids
    print("Number of overlapping rectangles", num)
    for i in range(list_.n_values):
        print("id", list_.value[i])

    rtree.RTreeDestroyTree(tree)


###############################################################################

if __name__ == "__main__":
    init()
    test_increment_datetime_by_string()
    test_adjust_datetime_to_granularity()
    test_spatial_extent_intersection()
    test_compute_absolute_time_granularity()
    test_spatial_extent_intersection()
    test_spatial_relations()
    test_temporal_topology_builder()
    test_map_list_sorting()
    test_1d_rtree()
    test_2d_rtree()
    test_3d_rtree()
    test_4d_rtree()
