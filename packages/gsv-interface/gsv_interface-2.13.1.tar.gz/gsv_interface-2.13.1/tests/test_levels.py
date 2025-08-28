from gsv.levels import PressureLevelReader, SurfaceLevelReader, OceanLevelReader


def test_read_level_sfc(eccodes_msgid):
    levels = SurfaceLevelReader()
    level = levels.read_level(eccodes_msgid)
    assert level == 0

def test_read_level_pl(eccodes_msgid_pl):
    levels = PressureLevelReader()
    level = levels.read_level(eccodes_msgid_pl)
    assert level == 700

def test_read_level_o3d(eccodes_msgid_o3d):
    levels = OceanLevelReader()
    level = levels.read_level(eccodes_msgid_o3d)
    assert abs(level - 6.54303) < 1.0e-5

def test_read_level_03d_file_not_founf(eccodes_msgid_o3d):
    levels = OceanLevelReader()
    levels.DEFINITION_FILE = "missing.nc"
    levels.__post_init__()
    level = levels.read_level(eccodes_msgid_o3d)
    assert level == 6

def test_read_vertical_cood_sfc(eccodes_msgid):
    levels = SurfaceLevelReader()
    coord = levels.read_vertical_coordinate(eccodes_msgid)
    assert coord.name == "level"
    assert coord.data == [0]
    assert coord.dims == ("level", )
    assert coord.attrs["standard_name"] == "level"
    assert coord.attrs["units"] == "m"

def test_read_vertical_coord_pl(eccodes_msgid_pl):
    levels = PressureLevelReader()
    coord = levels.read_vertical_coordinate(eccodes_msgid_pl)
    assert coord.name == "level"
    assert coord.data == [700]
    assert coord.attrs["standard_name"] == "level"
    assert coord.attrs["units"] == "hPa"

def test_read_vertical_coord_o3d(eccodes_msgid_o3d):
    levels = OceanLevelReader()
    coord = levels.read_vertical_coordinate(eccodes_msgid_o3d)
    assert coord.name == "level"
    assert (coord.data[0] - 6.54303) < 1.0e-5
    assert coord.attrs["standard_name"] == "level"
    assert coord.attrs["units"] == "m"

def test_read_vertical_coord_03d_file_not_found(eccodes_msgid_o3d):
    levels = OceanLevelReader()
    levels.DEFINITION_FILE = "missing.nc"
    levels.__post_init__()
    coord = levels.read_vertical_coordinate(eccodes_msgid_o3d)
    assert levels.level_meters is None
    assert coord.name == "level"
    assert coord.data == [6]
    assert coord.attrs["standard_name"] == "level"
    assert coord.attrs["units"] == "NEMO model layers"
