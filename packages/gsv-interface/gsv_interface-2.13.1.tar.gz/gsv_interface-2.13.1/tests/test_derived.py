from gsv.derived.derived import norm, get_action_fn, get_derived_variables_components, _get_new_da, compute_derived_variables
from gsv.requests.parser import parse_request

import numpy as np
from pathlib import Path
import pytest
import xarray as xr


def test_norm_values():
    array_1 = np.array([3.0, 5.0, -7.0])
    array_2 = np.array([-4.0, -12.0, -24.0])
    norm_ref = np.array([5.0, 13.0, 25.0])
    norm_test = norm(array_1, array_2)
    assert np.allclose(norm_ref, norm_test, rtol=1e-5)

def test_norm_xarray():
    array_1 = xr.DataArray(np.array([3.0, 5.0, -7.0]), dims=["ncells"])
    array_2 = xr.DataArray(np.array([-4.0, -12.0, -24.0]), dims=["ncells"])
    norm_ref = xr.DataArray(np.array([5.0, 13.0, 25.0]), dims=["ncells"])
    norm_test = norm(array_1, array_2)
    assert np.allclose(norm_ref, norm_test, rtol=1e-5)

def test_norm_xarray_masked():
    array_1 = xr.DataArray(np.array([3.0, np.nan, -7.0]), dims=["ncells"])
    array_2 = xr.DataArray(np.array([-4.0, np.nan, -24.0]), dims=["ncells"])
    norm_ref = xr.DataArray(np.array([5.0, np.nan, 25.0]), dims=["ncells"])
    norm_test = norm(array_1, array_2)
    assert np.allclose(norm_ref, norm_test, rtol=1e-5, equal_nan=True)

def test_norm_xarray_latlon():
    array_1 = xr.DataArray(np.array([[3.0, 5.0, -7.0], [3.0, 5.0, -7.0], [3.0, 5.0, -7.0]]), dims=["lat", "lon"])
    array_2 = xr.DataArray(np.array([[-4.0, -12.0, -24.0], [-4.0, -12.0, -24.0], [-4.0, -12.0, -24.0]]), dims=["lat", "lon"])
    norm_ref = xr.DataArray(np.array([[5.0, 13.0, 25.0], [5.0, 13.0, 25.0], [5.0, 13.0, 25.0]]), dims=["lat", "lon"])
    norm_test = norm(array_1, array_2)
    assert np.allclose(norm_ref, norm_test, rtol=1e-5)

def test_get_action_fn_norm():
    action_fn = get_action_fn("norm")
    assert action_fn == norm

def test_get_action_fn_error():
    with pytest.raises(ValueError):
        get_action_fn("not_norm")

def test_get_derived_variables_components(fdb_new_hourly_request):
    request = fdb_new_hourly_request
    test_cases = [
        ["131", "167", "10"],
        ["168", "228249"],

    ]
    expected_results = [
        ["131", "132", "167"],
        ["168", "228246", "228247"]
    ]
    for test_case, expected_result in zip(test_cases, expected_results):
        request["param"] = test_case
        processed_request = get_derived_variables_components(request)
        assert set(processed_request["param"]) == set(expected_result)

def test_get_derived_variables_components_custom_defs(fdb_new_hourly_request):
    request = fdb_new_hourly_request
    test_cases = [
        ["165", "167"],
        ["167"],

    ]
    expected_results = [
        ["165", "166"],
        ["165", "166"]
    ]

    derived_variables_defs = Path(__file__).parent / "testing_misc_files/alternative_derived_variables.yaml"

    for test_case, expected_result in zip(test_cases, expected_results):
        request["param"] = test_case
        processed_request = get_derived_variables_components(request, derived_variables_definitions=derived_variables_defs)
        assert set(processed_request["param"]) == set(expected_result)

def test_get_new_da(derived_variables_db):
    ds = xr.Dataset(
        {
            "100u": xr.DataArray(np.array([3.0, 5.0, -7.0]), dims=["x"], attrs={"GRIB_paramId": 228246}),
            "100v": xr.DataArray(np.array([-4.0, -12.0, -24.0]), dims=["x"], attrs={"GRIB_paramId": 228247}),
        }
    )
    var_data = derived_variables_db.get("228249")
    new_da = _get_new_da(ds, var_data)
    assert new_da.name == "100si"
    assert new_da.attrs["short_name"] == "100si"
    assert new_da.attrs["long_name"] == "100 meter wind speed"
    assert new_da.attrs["units"] == "m s**-1"

    ref_values = np.array([5.0, 13.0, 25.0])
    assert np.allclose(new_da.values, ref_values, rtol=1e-5)

def test_compute_derived_variables_only_derived(fdb_new_hourly_request):
    request = fdb_new_hourly_request
    ds = xr.Dataset(
        {
            "100u": xr.DataArray(np.array([1.0, 2.0, 3.0]), dims=["x"], attrs={"GRIB_paramId": 228246}),
            "100v": xr.DataArray(np.array([4.0, 5.0, 6.0]), dims=["x"], attrs={"GRIB_paramId": 228247}),
        }
    )
    request["param"] = ["228249"]
    ds_res = compute_derived_variables(request, ds)
    expected_vars = {"100si"}
    assert set(ds_res.data_vars) == expected_vars

def test_compute_derived_variables_only_derived_int(fdb_new_hourly_request):
    request = fdb_new_hourly_request
    ds = xr.Dataset(
        {
            "100u": xr.DataArray(np.array([1.0, 2.0, 3.0]), dims=["x"], attrs={"GRIB_paramId": 228246}),
            "100v": xr.DataArray(np.array([4.0, 5.0, 6.0]), dims=["x"], attrs={"GRIB_paramId": 228247}),
        }
    )
    request["param"] = [228249]
    request = parse_request(request)
    ds_res = compute_derived_variables(request, ds)
    expected_vars = {"100si"}
    assert set(ds_res.data_vars) == expected_vars

def test_compute_derived_variables_derived_plus_components(fdb_new_hourly_request):
    request = fdb_new_hourly_request
    ds = xr.Dataset(
        {
            "100u": xr.DataArray(np.array([1.0, 2.0, 3.0]), dims=["x"], attrs={"GRIB_paramId": 228246}),
            "100v": xr.DataArray(np.array([4.0, 5.0, 6.0]), dims=["x"], attrs={"GRIB_paramId": 228247}),
        }
    )
    request["param"] = ["228246", "228247", "228249"]
    ds_res = compute_derived_variables(request, ds)
    expected_vars = {"100u", "100v", "100si"}
    assert set(ds_res.data_vars) == expected_vars

def test_compute_derived_variables_mixed_request_string(fdb_new_hourly_request):
    """Request including variables that do not play any role in the
    derived variables computation. Params parsed as strings.
    """
    request = fdb_new_hourly_request
    ds = xr.Dataset(
        {
            "100u": xr.DataArray(np.array([1.0, 2.0, 3.0]), dims=["x"], attrs={"GRIB_paramId": 228246}),
            "100v": xr.DataArray(np.array([4.0, 5.0, 6.0]), dims=["x"], attrs={"GRIB_paramId": 228247}),
            "2t": xr.DataArray(np.array([10.0, 11.0, 12.0]), dims=["x"], attrs={"GRIB_paramId": 167}),
        }
    )
    request["param"] = ["228246", "228247", "167", "228249"]
    request = parse_request(request)
    ds_res = compute_derived_variables(request, ds)
    expected_vars = {"100u", "100v", "2t", "100si"}
    assert set(ds_res.data_vars) == expected_vars

def test_compute_derived_variables_mixed_request_int(fdb_new_hourly_request):
    """Request including variables that do not play any role in the
    derived variables computation. Params parsed as integers.
    """
    request = fdb_new_hourly_request
    ds = xr.Dataset(
        {
            "100u": xr.DataArray(np.array([1.0, 2.0, 3.0]), dims=["x"], attrs={"GRIB_paramId": 228246}),
            "100v": xr.DataArray(np.array([4.0, 5.0, 6.0]), dims=["x"], attrs={"GRIB_paramId": 228247}),
            "2t": xr.DataArray(np.array([10.0, 11.0, 12.0]), dims=["x"], attrs={"GRIB_paramId": 167}),
        }
    )
    request["param"] = [228246, 228247, 167, 228249]
    request = parse_request(request)
    ds_res = compute_derived_variables(request, ds)
    expected_vars = {"100u", "100v", "2t", "100si"}
    assert set(ds_res.data_vars) == expected_vars

def test_compute_derived_variables_custom_database(fdb_new_hourly_request):
    """Request including variables that do not play any role in the
    derived variables computation. Params parsed as integers.
    """
    request = fdb_new_hourly_request
    ds = xr.Dataset(
        {
            "10u": xr.DataArray(np.array([1.0, 2.0, 3.0]), dims=["x"], attrs={"GRIB_paramId": 165}),
            "10v": xr.DataArray(np.array([4.0, 5.0, 6.0]), dims=["x"], attrs={"GRIB_paramId": 166}),
        }
    )
    request["param"] = ["167"]
    request = parse_request(request)
    derived_variables_defs = Path(__file__).parent / "testing_misc_files/alternative_derived_variables.yaml"
    ds_res = compute_derived_variables(request, ds, derived_variables_definitions=derived_variables_defs)
    expected_vars = {"2t"}
    assert set(ds_res.data_vars) == expected_vars

def test_derived_da_attrs_mars(derived_variables_db):
    common_attrs = {
        "class": "d1",
        "dataset": "climate-dt",
        "experiment": "hist",
        "activity": "baseline",
        "model": "ifs-nemo",
        "realization": 1,
        "generation": 2,
        "type": "fc",
        "stream": "clte",
        "resolution": "high",
        "expver": "0001",
        "levtype": "hl",
    }
    ds = xr.Dataset(
        {
            "u": xr.DataArray(np.array([3.0, 5.0, -7.0]), dims=["x"], attrs={"GRIB_paramId": 131, **common_attrs}),
            "v": xr.DataArray(np.array([-4.0, -12.0, -24.0]), dims=["x"], attrs={"GRIB_paramId": 132, **common_attrs}),
        }
    )
    var_data = derived_variables_db.get("10")
    new_da = _get_new_da(ds, var_data)
    
    for key, value in common_attrs.items():
        assert new_da.attrs[key] == value

def test_derived_da_attrs_hardcoded(derived_variables_db):
    common_attrs = {
        "class": "d1",
        "dataset": "climate-dt",
        "experiment": "hist",
        "activity": "baseline",
        "model": "ifs-nemo",
        "realization": 1,
        "generation": 2,
        "type": "fc",
        "stream": "clte",
        "resolution": "high",
        "expver": "0001",
        "levtype": "hl",
    }
    ds = xr.Dataset(
        {
            "u": xr.DataArray(np.array([3.0, 5.0, -7.0]), dims=["x"], attrs={"GRIB_paramId": 131, **common_attrs}),
            "v": xr.DataArray(np.array([-4.0, -12.0, -24.0]), dims=["x"], attrs={"GRIB_paramId": 132, **common_attrs}),
        }
    )
    var_data = derived_variables_db.get("10")
    new_da = _get_new_da(ds, var_data)
    assert new_da.name == "ws"
    assert new_da.attrs["short_name"] == "ws"
    assert new_da.attrs["standard_name"] == "unknown"
    assert new_da.attrs["long_name"] == "Wind speed"
    assert new_da.attrs["units"] == "m s**-1"
    assert new_da.attrs["GRIB_paramId"] == "10"
    assert new_da.attrs["GRIB_shortName"] == "ws"
    assert new_da.attrs["GRIB_units"] == "m s**-1"
    assert new_da.attrs["GRIB_name"] == "Wind speed"
    assert new_da.attrs["GRIB_cfName"] == "unknown"
    assert new_da.attrs["GRIB_cfVarName"] == "si100"