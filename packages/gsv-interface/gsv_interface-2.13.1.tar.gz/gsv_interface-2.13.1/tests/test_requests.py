import re

from pathlib import Path
import pytest

from gsv.retriever import GSVRetriever
from gsv.requests import checker, parser, processor
from gsv.requests.utils import (
    split_request, filter_request, count_combinations, load_yaml,
    convert_to_step_format, convert_to_datetime_format,
    convert_date_to_monthly, convert_monthly_to_date
)
from gsv.exceptions import (
    InvalidRequestError, InvalidTargetGridError,
    InvalidInterpolationMethodError, MissingKeyError, InvalidKeyError,
    UnexpectedKeyError, InvalidTimeError, InvalidDateError,
    UnknownVariableError, InvalidLevelError, InvalidStepError,
    InvalidAreaError, InvalidMonthError, InvalidYearError,
    InvalidShortNameDefinitionPath, DateNotConvertableToMonthlyError
)

def test_split_request(basic_request):
    ordered_keys = ["step", "param", "date", "time", "levtype", "levelist"]
    splitted_request = split_request(basic_request, ordered_keys)
    assert len(splitted_request) == 12
    for i, req in enumerate(splitted_request):
        assert req["step"] == "0"
        assert req["date"] == "20050401"
        assert req["levtype"] == "sfc"

        if i < 4:
            assert req["param"] == "165"
        elif i < 8:
            assert req["param"] == "166"
        else:
            assert req["param"] == "167"

        if i%4 == 0:
            assert req["time"] == "0000"
        elif i%4 == 1:
            assert req["time"] == "0600"
        elif i%4 == 2:
            assert req["time"] == "1200"
        else:
            assert req["time"] == "1800"

def test_filter_request(basic_request, request_interp_nn, mars_keys):
    filtered_request = filter_request(request_interp_nn, mars_keys)
    assert filtered_request == basic_request


def test_count_combinations(basic_request, mars_keys):
    combinations = count_combinations(basic_request, mars_keys)
    assert combinations == 12


def test_check_missing_key():
    with pytest.raises(MissingKeyError):
        checker.check_request({"param": "165"})


def test_check_invalid_param():
    incorrect_params = ["dummy", ["dummy", "dummy"], ["167", "dummy"]]
    for param in incorrect_params:
        with pytest.raises(UnknownVariableError):
            checker.check_params(param)


def test_check_invalid_explicit_date():
    incorrect_dates = ["dummy", "2015022", 2015022, "20150431",
                       20150431, ["20050101", "dummy"]]
    for date in incorrect_dates:
        with pytest.raises(InvalidDateError):
            checker.check_dates(date)

def test_check_invalid_implicit_date():
    dates = ["20050101/to/20050105/by/4a", "20050101/by/2",
             "20050101/to/2005011", "20050105/to/20050101",
             "20050431/to/20050501", "20050430/to/20050431",
             "20050101/to/20050105/by/0"
             ]
    for date in dates:
        with pytest.raises(InvalidDateError):
            checker.check_dates(date)

def test_check_invalid_type_date():
    incorrect_dates = [None, 6.0, False]
    for date in incorrect_dates:
        with pytest.raises(InvalidDateError):
            checker.check_dates(date)

def test_check_invalid_explicit_time():
    incorrect_times = ["dummy", "600", 600, ["0600", 600]]
    for time in incorrect_times:
        with pytest.raises(InvalidTimeError):
            checker.check_times(time)

def test_check_invalid_implicit_time():
    incorrect_times = [
        "0000/to/0600/by/4a", "0000/by/400",
        "0000/to/123", "0600/to/0000",
        "0061/to/0600", "0000/to/2300/by/0000"
    ]
    for time in incorrect_times:
        with pytest.raises(InvalidTimeError):
            checker.check_times(time)


def test_check_invalid_type_time():
    incorrect_times = [
        None, 60.0, False
    ]
    for time in incorrect_times:
        with pytest.raises(InvalidTimeError):
            checker.check_times(time)

def test_check_invalid_step():
    incorrect_steps = [
        "2a", "2.5", 2.0, [100, 3.5], False, None, -100,
        "0/by/6", "10/to/0", "-100"
    ]
    for step in incorrect_steps:
        with pytest.raises(InvalidStepError):
            checker.check_steps(step)

# Test disabled as feature is disabled since version 0.4.3
# def test_check_invalid_levtype(basic_request):
#     basic_request["levtype"] = "dummy"
#     with pytest.raises(InvalidKeyError):
#         checker.check_request(basic_request)


def test_check_invalid_explicit_months():
    incorrect_months = [
        "0", "-1", "2.5", True, None, "dummy",
        [1, 2.3], 13, "13", ["1", 13]
    ]
    for month in incorrect_months:
        with pytest.raises(InvalidMonthError):
            checker.check_months(month)

def test_check_invalid_implicit_months():
    incorrect_months = [
        "1/to/12/by/4a", "1/to/12/by/0", "1/to/12/by/-3",
        "1/12", "1/by/2", "1/to/13", "12/to/10/by/2"
    ]

    for month in incorrect_months:
        with pytest.raises(InvalidMonthError):
            checker.check_months(month)

def test_check_invalid_explicit_years():
    incorrect_years = [
        "0", "-1990", "2.5", True, None, "dummy",
        [1990, '1991.5'], 10000, "10000", ["1990", 10000]
    ]
    for year in incorrect_years:
        with pytest.raises(InvalidYearError):
            checker.check_years(year)

def test_check_invalid_implicit_years():
    incorrect_years = [
        "1990/to/2000/by/4a", "1990/to/2000/by/0", "1990/to/2000/by/-3",
        "1990/2000", "1900/by/2", "1990/to/10000", "2000/to/1900/by/2"
    ]

    for year in incorrect_years:
        with pytest.raises(InvalidYearError):
            checker.check_years(year)

def test_check_request_missing_step(basic_request):
    del(basic_request["step"])
    checker.check_request(basic_request)

def test_check_invalid_request_mixed_date_format(basic_request):
    # Request with date, time, step and year
    basic_request["year"] = "1990"
    with pytest.raises(InvalidKeyError):
        checker.check_requested_dates(basic_request)

    # Request with year, month, date
    basic_request["month"] = "3"
    del(basic_request["time"])
    del(basic_request["step"])
    with pytest.raises(InvalidKeyError):
        checker.check_requested_dates(basic_request)

    # Request with year, month and step
    basic_request["step"] = "0"
    del(basic_request["date"])
    with pytest.raises(InvalidKeyError):
        checker.check_requested_dates(basic_request)


def test_check_invalid_request_no_dates(basic_request):
    del(basic_request["date"])
    del(basic_request["time"])
    with pytest.raises(MissingKeyError):
        checker.check_requested_dates(basic_request)

def test_check_multiple_levtypes(basic_request):
    basic_request["levtype"] = ["sfc", "pl"]
    with pytest.raises(NotImplementedError):
        checker.check_request(basic_request)


def test_check_levtype_aslist(basic_request):
    basic_request["levtype"] = ["sfc"]
    checker.check_request(basic_request)

def test_check_request_new_schema_hourly(fdb_new_hourly_request):
    checker.check_request(fdb_new_hourly_request)


def test_check_request_new_schema_monthly(fdb_new_monthly_request):
    checker.check_request(fdb_new_monthly_request)


def test_check_request_new_schema_wave(fdb_new_wave_request):
    checker.check_request(fdb_new_wave_request)


def test_check_unexpected_levelist(basic_request):
    basic_request["levelist"] = ["0"]
    with pytest.raises(UnexpectedKeyError):
        checker.check_request(basic_request)


def test_check_missing_levelist(basic_request):
    basic_request["levtype"] = "pl"
    with pytest.raises(MissingKeyError):
        checker.check_request(basic_request)


def test_check_invalid_levelist(basic_request):
    basic_request["levtype"] = "pl"
    incorrect_levelists = [
        "2a", "2.5", 2.0, [100, 3.5], False, None, "-100"
    ]
    for levelist in incorrect_levelists:
        basic_request["levelist"] = levelist
        with pytest.raises(InvalidLevelError):
            checker.check_request(basic_request)


def test_check_correct_levelsits(basic_request):
    basic_request["levtype"] = "pl"
    correct_levelists = [
        100, "100", [100, 300], ("100", "300"), (100, "300")
    ]
    for levelist in correct_levelists:
        basic_request["levelist"] = levelist
        checker.check_request(basic_request)


def test_check_incorrect_target_grid(basic_request):
    incorrect_grids = [
        ("dummy", "dummy"), (1.0, 1.0, 1.0),
        (1.0, -1.0), ("dummy", 1.0), ["dummy"],
        "0.1/0.1/0.1", "-0.1/0.1", "0.1b/0.1",
        10, None, False
    ]

    for grid in incorrect_grids:
        basic_request["grid"] = grid
        with pytest.raises(InvalidTargetGridError):
            checker.check_request(basic_request)


def test_check_method_without_grid(basic_request):
    basic_request["method"] = "nn"
    with pytest.raises(UnexpectedKeyError):
        checker.check_request(basic_request)


def test_check_incorrect_interpolation_method(request_interp_nn):
    request_interp_nn["method"] = "dummy"

    with pytest.raises(InvalidInterpolationMethodError):
        checker.check_request(request_interp_nn)

def test_check_area_correct(request_interp_nn):
    correct_areas = [
        [90.0, 10.0, -90.0, 40.0],
        [90.0, "10.0", -90.0, 40.0],
        "90.0/0.0/-90.0/360.0"
    ]

    for area in correct_areas:
        request_interp_nn["area"] = area
        checker.check_request(request_interp_nn)


def test_check_area_invalid(request_interp_nn):
    invalid_areas = [
        [90.0, -90.0, 0.0],
        ["dummy", 0.0, 0.0, 360.0],
        [91.0, 0.0, -90.0, 360.0],
        ["91.0", 0.0, -90.0, 360.0],
        "90.0/-90.0/360.0",
        "dummy/0.0/0.0/360.0"
        "91.0/0.0/-90.0/360.0",
        True,
        None,
        "Dummy"
    ]

    for area in invalid_areas:
        request_interp_nn["area"] = area
        with pytest.raises(InvalidAreaError):
            checker.check_request(request_interp_nn)

def test_check_area_witohut_interpolation(basic_request):
    basic_request["area"] = [90.0, 0.0, -90.0 ,360.0]
    with pytest.raises(UnexpectedKeyError):
        checker.check_request(basic_request)

def test_render_param():
    short_names = ["10u", "10v", "2t"]
    params = ["165", "166", "167"]
    assert processor._render_params(short_names) == params

    # Check one element creates list
    assert processor._render_params('2d') == ["168"]

def test_render_param_as_grib():
    "Check params passed as GRIB codes with either integer or string "
    "data types are always parsed as strings."
    params = ["165", 166, "167"]
    assert processor._render_params(params) == ["165", "166", "167"]

def test_render_param_cusom_def(user_definitions):
    short_names = ["2t", "dummy"]
    params = ["2", "1"]
    assert processor._render_params(short_names, user_definitions) == params


def test_parse_param_cusom_def(basic_request, user_definitions):
    basic_request["param"] = ["2t", "dummy"]
    params = ["2", "1"]
    request = parser.parse_request(
        basic_request,
        check_and_process=True,
        definitions=user_definitions
    )
    assert request["param"] == params


def test_render_param_custom_def_missing_file():
    short_names = ["10u"]
    with pytest.raises(InvalidShortNameDefinitionPath):
        processor._render_params(short_names, "dummy.yaml")


def test_render_implicit_dates():
    implicit_dates = "20050401/to/20050405/by/2"
    explicit_dates = ["20050401", "20050403", "20050405"]
    assert processor._render_dates(implicit_dates) == explicit_dates


def test_render_explicit_dates():
    explicit_dates = ["20050401", "20050403", 20050405]
    expected_dates = ["20050401", "20050403", "20050405"]
    assert processor._render_dates(explicit_dates) == expected_dates
    assert processor._render_dates(20050401) == ["20050401"]


def test_render_implicit_times():
    implicit_times = "0000/to/1800/by/600"
    explicit_times = ["0000", "0600", "1200", "1800"]
    assert processor._render_times(implicit_times) == explicit_times


def test_render_explicit_times():
    explicit_times = ["0600", "1200", 1800]
    expected_times = ["0600", "1200", "1800"]
    assert processor._render_times(explicit_times) == expected_times
    assert processor._render_times(1200) == ["1200"]


def test_render_implicit_months():
    implicit_months = ["1/to/12/by/2", "1/to/12", "1"]
    explicit_months = [
        ["1", "3", "5", "7", "9", "11"],
        ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
        ["1"]
    ]
    for imp_month, exp_month in zip(implicit_months, explicit_months):
        assert processor._render_steps(imp_month) == exp_month

def test_render_explicit_months():
    explicit_months = [1, 2, "3"]
    expected_months = ["1", "2", "3"]
    assert processor._render_steps(explicit_months) == expected_months
    assert processor._render_steps("1") == ["1"]

def test_render_implicit_years():
    implicit_years = ["1990/to/2000/by/2", "1990/to/2000", "1990"]
    explicit_years = [
        ["1990", "1992", "1994", "1996", "1998", "2000"],
        ["1990", "1991", "1992", "1993", "1994", "1995", "1996", "1997",
         "1998", "1999", "2000"],
        ["1990"]
    ]
    for imp_year, exp_year in zip(implicit_years, explicit_years):
        assert processor._render_steps(imp_year) == exp_year

def test_render_explicit_years():
    explicit_years = [1990, 2000, "2020"]
    expected_years = ["1990", "2000", "2020"]
    assert processor._render_steps(explicit_years) == expected_years
    assert processor._render_steps("1990") == ["1990"]

def test_render_implicit_steps():
    implicit_steps = "0/to/9/by/2"
    explicit_steps = ["0", "2", "4", "6", "8"]

    assert processor._render_steps(implicit_steps) == explicit_steps

def test_render_explicit_steps():
    explicit_steps = [0, 1, "2"]
    expected_steps = ["0", "1", "2"]
    assert processor._render_steps(explicit_steps) == expected_steps
    assert processor._render_steps(5) == ["5"]


def test_render_grid_str():
    user_grid  = "72.0/36.0"
    grid = processor._render_grid(user_grid)
    assert grid == [72.0, 36.0]


def test_render_grid_tuple():
    user_grid = (72.0, 36.0)
    grid = processor._render_grid(user_grid)
    assert grid == [72.0, 36.0]

    user_grid = ("72.0", "36.0")
    grid = processor._render_grid(user_grid)
    assert grid == [72.0, 36.0]


def test_render_grid_list():
    user_grid = [72.0, 36.0]
    grid = processor._render_grid(user_grid)
    assert grid == [72.0, 36.0]

    user_grid = ["72.0", "36.0"]
    grid = processor._render_grid(user_grid)
    assert grid == [72.0, 36.0]

def test_render_area_string():
    user_area = "90.0/0.0/-90.0/360.0"
    area = processor._render_area(user_area)
    assert area == [90.0, 0.0, -90.0 ,360.0]

    user_area = "90/0/-90/360"
    area = processor._render_area(user_area)
    assert area == [90.0, 0.0, -90.0 ,360.0]

def test_render_area_list():
    user_area = [90.0 ,0.0, -90.0, 360.0]
    area = processor._render_area(user_area)
    assert area == [90.0, 0.0, -90.0 ,360.0]

    user_area = ["90.0", "0.0", "-90.0", 360.0]
    area = processor._render_area(user_area)
    assert area == [90.0, 0.0, -90.0, 360.0]

def test_render_area_tuple():
    user_area = (90.0 ,0.0, -90.0, 360.0)
    area = processor._render_area(user_area)
    assert area == [90.0, 0.0, -90.0 ,360.0]

    user_area = ("90.0", "0.0", "-90.0", 360.0)
    area = processor._render_area(user_area)
    assert area == [90.0, 0.0, -90.0, 360.0]


def test_load_yaml(basic_request):
    yaml_path = Path(__file__).parent / "request_testing.yaml"
    loaded_request = load_yaml(yaml_path)
    assert loaded_request == basic_request


def test_process_request(basic_request, shortname_request):
    request = processor.process_request(shortname_request)
    assert request == basic_request

def test_process_request_missing_step(basic_request, shortname_request):
    del(shortname_request["step"])
    del(basic_request["step"])
    request = processor.process_request(shortname_request)
    assert request == basic_request


def test_process_request_area(request_interp_nn):
    request_interp_nn["area"] = [90.0, 0.0, -90.0, 360.0]
    request = processor.process_request(request_interp_nn)
    assert request["area"] == [90.0, 0.0, -90.0, 360.0]


def test_parse_request_dict(basic_request):
    assert parser.parse_request(basic_request, check_and_process=False) == basic_request


def test_parse_request_yaml(basic_request):
    yaml_path = Path(__file__).parent / "request_testing.yaml"
    assert parser.parse_request(yaml_path, check_and_process=False) == basic_request


def test_parse_request_incorrect():
    request = 5
    with pytest.raises(InvalidRequestError):
        parser.parse_request(request)

def test_convert_to_steps(basic_request):
    start_date = "20050101"
    start_time = "0000"
    expected_steps = ["2160", "2166", "2172", "2178"]
    step_request = convert_to_step_format(
        basic_request, start_date=start_date, start_time=start_time
    )
    assert expected_steps == step_request["step"]

def test_convert_to_datetime(fdb_request):
    fdb_request["step"] = "12"
    datetime_request = convert_to_datetime_format(fdb_request)
    assert datetime_request["step"] == "0"
    assert datetime_request["date"] == "20200120"
    assert datetime_request["time"] == "1200"

def test_convert_to_datetime_list(fdb_request):
    fdb_request["step"] = ["12"]
    fdb_request["date"] = ["20200120"]
    fdb_request["time"] = ["0000"]

    datetime_request = convert_to_datetime_format(fdb_request)
    assert datetime_request["step"] == "0"
    assert datetime_request["date"] == "20200120"
    assert datetime_request["time"] == "1200"

def test_convert_to_datetime_step_list_invalid(fdb_request):
    fdb_request["step"] = ["0", "12"]
    with pytest.raises(Exception):
        convert_to_datetime_format(fdb_request)

def test_convert_to_datetime_date_list_invalid(fdb_request):
    fdb_request["step"] = "12"
    fdb_request["date"] = ["20200120", "20200121"]
    with pytest.raises(Exception):
        convert_to_datetime_format(fdb_request)

def test_convert_to_datetime_time_list_invalid(fdb_request):
    fdb_request["step"] = "12"
    fdb_request["time"] = ["0000", "1200"]
    with pytest.raises(Exception):
        convert_to_datetime_format(fdb_request)

def test_parse_request_new_schema_hourly(fdb_new_hourly_request):
    fdb_request = parser.parse_request(fdb_new_hourly_request)
    fdb_request = filter_request(fdb_request, GSVRetriever.MARS_KEYS)
    assert fdb_request == fdb_new_hourly_request

def test_parse_request_new_schema_monthly(fdb_new_monthly_request):
    fdb_request = parser.parse_request(fdb_new_monthly_request)
    fdb_request = filter_request(fdb_request, GSVRetriever.MARS_KEYS)
    assert fdb_request == fdb_new_monthly_request

def test_parse_request_new_schema_wave(fdb_new_wave_request):
    fdb_request = parser.parse_request(fdb_new_wave_request)
    fdb_request = filter_request(fdb_request, GSVRetriever.MARS_KEYS)
    assert fdb_request == fdb_new_wave_request

def test_default_shortnames_no_duplicates(default_shortname_filepath):
    SHORT_NAME_PATTERN = r'"(\w+)":\s+"(\w+)"'
    with open(default_shortname_filepath, 'r') as f:
        lines = f.readlines()

    short_names = []
    paramids = []

    for line in lines:

        if line.startswith("#"):
            continue

        search = re.search(SHORT_NAME_PATTERN, line)
        short_names.append(search.group(1))
        paramids.append(search.group(2))

    assert len(short_names) == len(set(short_names))
    assert len(paramids) == len(set(paramids))

def test_convert_month_to_date(fdb_new_monthly_request):
    request = parser.parse_request(fdb_new_monthly_request)
    reference_dates = processor._render_dates("20200201/to/20200229")
    date_request = convert_monthly_to_date(request)
    assert set(date_request["date"]) == set(reference_dates)
    assert "month" not in date_request
    assert "year" not in date_request

def test_convert_month_to_date_multiple_months(fdb_new_monthly_request):
    fdb_new_monthly_request["month"] = ["1", "02", 3, 4]
    request = parser.parse_request(fdb_new_monthly_request)
    reference_dates = processor._render_dates("20200101/to/20200430")
    date_request = convert_monthly_to_date(request)
    assert set(date_request["date"]) == set(reference_dates)
    assert "month" not in date_request
    assert "year" not in date_request

def test_convert_month_to_date_multiple_years(fdb_new_monthly_request):
    fdb_new_monthly_request["month"] = ["1", "02", 3, 4]
    fdb_new_monthly_request["year"] = [2020, 2022, 2025]
    request = parser.parse_request(fdb_new_monthly_request)
    reference_dates = processor._render_dates("20200101/to/20200430")
    reference_dates.extend(processor._render_dates("20220101/to/20220430"))
    reference_dates.extend(processor._render_dates("20250101/to/20250430"))
    date_request = convert_monthly_to_date(request)
    assert set(date_request["date"]) == set(reference_dates)
    assert "month" not in date_request
    assert "year" not in date_request

def test_convert_date_to_month(fdb_new_hourly_request):
    request = parser.parse_request(fdb_new_hourly_request)
    monthly_request = convert_date_to_monthly(request)
    assert set(monthly_request["month"]) == {"2"}
    assert set(monthly_request["year"]) == {"2020"}
    assert "date" not in monthly_request
    assert "time" not in monthly_request

def test_convert_date_to_month_multiple_dates(fdb_new_hourly_request):
    """
    Test heteregoneous dates with partial months and mixed months in
    different years. This should work as convert_date_to_monthly will
    be called with strict=False by default.
    """
    fdb_new_hourly_request["date"] = ["20200101", 20200102, "20200201", "20200401", "20210301"]
    request = parser.parse_request(fdb_new_hourly_request)
    monthly_request = convert_date_to_monthly(request)
    assert set(monthly_request["month"]) == {"1", "2", "3", "4"}
    assert set(monthly_request["year"]) == {"2020", "2021"}
    assert "date" not in monthly_request
    assert "time" not in monthly_request

def test_convert_date_to_month_multiple_dates_strict_false(fdb_new_hourly_request):
    """
    Test heteregoneous dates with partial months and mixed months in
    different years. This should work as convert_date_to_monthly is being
    called with strict=False explictly.
    """
    fdb_new_hourly_request["date"] = ["20200101", 20200102, "20200201", "20200401", "20210301"]
    request = parser.parse_request(fdb_new_hourly_request)
    monthly_request = convert_date_to_monthly(request, strict=False)
    assert set(monthly_request["month"]) == {"1", "2", "3", "4"}
    assert set(monthly_request["year"]) == {"2020", "2021"}
    assert "date" not in monthly_request
    assert "time" not in monthly_request

def test_convert_date_to_monthly_strcit_true_fails(fdb_new_hourly_request):
    """
    Test heteregoneous dates with partial months and mixed months in
    different years. This should fail as convert_date_to_monthly is being
    called with strict=True explictly.
    """
    fdb_new_hourly_request["date"] = ["20200101", 20200102, "20200201", "20200401", "20210301"]
    request = parser.parse_request(fdb_new_hourly_request)
    with pytest.raises(DateNotConvertableToMonthlyError):
        convert_date_to_monthly(request, strict=True)

def test_convert_date_to_monthly_strict_true(fdb_new_hourly_request):
    """
    """
    fdb_new_hourly_request["date"] = "20200101/to/20200430"
    request = parser.parse_request(fdb_new_hourly_request)
    monthly_request = convert_date_to_monthly(request, strict=True)
    assert set(monthly_request["month"]) == {"1", "2", "3", "4"}
    assert set(monthly_request["year"]) == {"2020"}
    assert "date" not in monthly_request
    assert "time" not in monthly_request

def test_convert_date_to_monthly_multiple_years_strict_true(fdb_new_hourly_request):
    fdb_new_hourly_request["date"] = "20200101/to/20200430"
    request = parser.parse_request(fdb_new_hourly_request)
    request["date"].extend(processor._render_dates("20210101/to/20210430"))
    monthly_request = convert_date_to_monthly(request, strict=True)
    assert set(monthly_request["month"]) == {"1", "2", "3", "4"}
    assert set(monthly_request["year"]) == {"2020", "2021"}
    assert "date" not in monthly_request
    assert "time" not in monthly_request