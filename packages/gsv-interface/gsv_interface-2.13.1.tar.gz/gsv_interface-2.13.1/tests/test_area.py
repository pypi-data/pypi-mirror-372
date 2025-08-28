import pytest

from gsv.requests.checker import check_area
from gsv.area import RectangularAreaSelector
from gsv.exceptions import InvalidAreaError


def test_rectangular_area_selector_coordinates():
    area = RectangularAreaSelector([90.0, 10.0, -90.0, 40.0])
    assert area.north == 90.0
    assert area.south == -90.0
    assert area.west == 10.0
    assert area.east == 40.0


def test_rectangular_area_selector_equality_true():
    area_1 = RectangularAreaSelector([90.0, 10.0, -90.0, 40.0])
    area_2 = RectangularAreaSelector([90.0, 10.0, -90.0, 40.0])
    assert area_1 == area_2


def test_rectangular_area_selector_equality_false():
    area_1 = RectangularAreaSelector([90.0, 10.0, -90.0, 40.0])
    area_2 = RectangularAreaSelector([90.0, 10.0, -90.0, 30.0])
    assert not area_1 == area_2
    assert not area_1 == 40


def test_select_area_east(ds_r180x91):
    area = RectangularAreaSelector([90.0, 10.0, -90.0, 40.0])
    ds = area.select_area(ds_r180x91)
    assert ds.coords["lon"].values[0] == 10.0
    assert ds.coords["lon"].values[-1] == 40.0
    assert ds.coords["lat"].values[0] == 90.0
    assert ds.coords["lat"].values[-1] == -90.0

def test_select_area_east_limits(ds_r180x91):
    area = RectangularAreaSelector([90.0, 0.0, -90.0, 180.0])
    ds = area.select_area(ds_r180x91)
    assert ds.coords["lon"].values[0] == 0.0
    assert ds.coords["lon"].values[-1] == 180.0
    assert ds.coords["lat"].values[0] == 90.0
    assert ds.coords["lat"].values[-1] == -90.0

def test_select_area_west_360(ds_r180x91):
    area = RectangularAreaSelector([90.0, 270.0, -90.0, 330.0])
    ds = area.select_area(ds_r180x91)
    assert ds.coords["lon"].values[0] == 270.0
    assert ds.coords["lon"].values[-1] == 330.0
    assert ds.coords["lat"].values[0] == 90.0
    assert ds.coords["lat"].values[-1] == -90.0

def test_select_area_west_360_limits(ds_r180x91):
    # WARNING 360.0 longitude does not exist on original dataset
    area = RectangularAreaSelector([90.0, 180.0, -90.0, 360.0])
    ds = area.select_area(ds_r180x91)
    assert ds.coords["lon"].values[0] == 180.0
    assert ds.coords["lon"].values[-1] == 358.0
    assert ds.coords["lat"].values[0] == 90.0
    assert ds.coords["lat"].values[-1] == -90.0

def test_select_area_west_180(ds_r180x91):
    area = RectangularAreaSelector([90.0, -90.0, -90.0, -30.0])
    ds = area.select_area(ds_r180x91)
    assert ds.coords["lon"].values[0] == -90.0
    assert ds.coords["lon"].values[-1] == -30.0
    assert ds.coords["lat"].values[0] == 90.0
    assert ds.coords["lat"].values[-1] == -90.0

def test_select_area_west_180_limits(ds_r180x91):
    area = RectangularAreaSelector([90.0, -180.0, -90.0, 0.0])
    ds = area.select_area(ds_r180x91)
    assert ds.coords["lon"].values[0] == -180.0
    assert ds.coords["lon"].values[-1] == 0.0
    assert ds.coords["lat"].values[0] == 90.0
    assert ds.coords["lat"].values[-1] == -90.0

def test_select_area_west_to_east(ds_r180x91):
    area = RectangularAreaSelector([90.0, -90.0, -90.0, 90.0])
    ds = area.select_area(ds_r180x91)
    assert ds.coords["lon"].values[0] == -90.0
    assert ds.coords["lon"].values[-1] == 90.0
    assert ds.coords["lat"].values[0] == 90.0
    assert ds.coords["lat"].values[-1] == -90.0

def test_select_area_west_to_east_limits(ds_r180x91):
    area = RectangularAreaSelector([90.0, -180.0, -90.0, 180.0])
    ds = area.select_area(ds_r180x91)
    assert ds.coords["lon"].values[0] == -180.0
    assert ds.coords["lon"].values[-1] == 178.0
    assert ds.coords["lat"].values[0] == 90.0
    assert ds.coords["lat"].values[-1] == -90.0

def test_select_area_east_to_west(ds_r180x91):
    area = RectangularAreaSelector([90, 90.0, -90, 270.0])
    ds = area.select_area(ds_r180x91)
    assert ds.coords["lon"].values[0] == 90.0
    assert ds.coords["lon"].values[-1] == 270.0
    assert ds.coords["lat"].values[0] == 90.0
    assert ds.coords["lat"].values[-1] == -90.0

def test_select_area_east_to_west_limits(ds_r180x91):
    area = RectangularAreaSelector([90.0, 0.0, -90.0, 360.0])
    ds = area.select_area(ds_r180x91)
    assert ds.coords["lon"].values[0] == 0.0
    assert ds.coords["lon"].values[-1] == 358.0
    assert ds.coords["lat"].values[0] == 90.0
    assert ds.coords["lat"].values[-1] == -90.0

def test_select_area_west_to_east_wrap(ds_r180x91):
    area = RectangularAreaSelector([90.0, 90.0, -90.0, -90.0])
    ds = area.select_area(ds_r180x91)
    assert ds.coords["lon"].values[0] == 90.0
    assert ds.coords["lon"].values[-1] == 270.0
    assert ds.coords["lat"].values[0] == 90.0
    assert ds.coords["lat"].values[-1] == -90.0

def test_select_area_west_to_east_wrap_limits(ds_r180x91):
    pass
    # WARNING what about (0.0, -180.0) or (180.0, 0.0)??
    # WARNING what about (360.0, 0.0) or (180.0, -180.0)

def test_select_area_east_to_west_wrap(ds_r180x91):
    area = RectangularAreaSelector([90.0, 270.0, -90.0, 90.0])
    ds = area.select_area(ds_r180x91)
    assert ds.coords["lon"].values[0] == -90.0
    assert ds.coords["lon"].values[-1] == 90.0
    assert ds.coords["lat"].values[0] == 90.0
    assert ds.coords["lat"].values[-1] == -90.0

def test_select_area_invalid_south_larger_than_north(ds_r180x91):  #A1
    area = [60, 0.0, 80.0, 360.0]
    with pytest.raises(InvalidAreaError):
        check_area(area)

def test_select_area_invalid_north_over_90(ds_r180x91):  # A4
    area = [91.0, 0.0, -90.0, 360.0]
    with pytest.raises(InvalidAreaError):
        check_area(area)

def test_select_area_invalid_south_under_neg_90(ds_r180x91):  # A5
    area = [90.0, 0.0, -91.0, 360.0]
    with pytest.raises(InvalidAreaError):
        check_area(area)

def test_select_area_invalid_west_under_neg_180(ds_r180x91):  # A6
    area = [90.0, -190.0, -90.0 ,360.0]
    with pytest.raises(InvalidAreaError):
        check_area(area)

def test_select_area_invalid_west_over_360(ds_r180x91):  # A6
    area = [90.0, 361.0, -90.0 ,360.0]
    with pytest.raises(InvalidAreaError):
        check_area(area)

def test_select_area_invalid_east_under_neg_180(ds_r180x91):  # A7
    area = [90.0, 0.0, -90.0 ,-190.0]
    with pytest.raises(InvalidAreaError):
        check_area(area)

def test_select_area_invalid_east_over_360(ds_r180x91):  # A7
    area = [90.0, 0.0, -90.0 ,361.0]
    with pytest.raises(InvalidAreaError):
        check_area(area)

def test_select_area_overlapping(ds_r180x91):
    area = [90.0, -180.0, -90.0, 360.0]
    check_area(area)
    area = RectangularAreaSelector(area)
    ds = area.select_area(ds_r180x91)

    assert ds.coords["lon"].values[0] == 0.0
    assert ds.coords["lon"].values[-1] == 358.0
    assert ds.coords["lat"].values[0] == 90.0
    assert ds.coords["lat"].values[-1] == -90.0

def test_select_area_invalid_big_area(ds_r180x91):
    area = [90.0, -160.0, -90.0, 190.0]
    check_area(area)

    with pytest.raises(InvalidAreaError):
        area = RectangularAreaSelector(area)

def test_select_area_invalid_big_wrapping(ds_r180x91):
    area = [90.0, 90.0, -90.0, 40.0]
    check_area(area)

    with pytest.raises(InvalidAreaError):
        area = RectangularAreaSelector(area)
