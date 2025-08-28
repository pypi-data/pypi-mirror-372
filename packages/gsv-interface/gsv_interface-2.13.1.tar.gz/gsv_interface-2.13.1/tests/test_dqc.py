import os
from pathlib import Path
from unittest import mock

import eccodes as ecc
import numpy as np
import pytest
import yaml

from gsv.dqc import dqc_wrapper
from gsv.dqc.spatial_completeness_checker import SpatialCompletenessChecker
from gsv.dqc.spatial_consistency_checker import SpatialConsistencyChecker
from gsv.dqc.standard_compliance_checker import StandardComplianceChecker
from gsv.dqc.physical_plausibility_checker import PhysicalPlausibilityChecker
from gsv.iterator import MessageIterator

from gsv.exceptions import (
    DQCInvalidHaltModeError,
    DQCMissingProfilesError,
    UnknownLevtypeError,
    DQCMissingStartDateError,
    DQCStandardComplianceError,
    DQCSpatialCompletenessError,
    DQCSpatialConsistencyError,
    DQCPhysicalPlausibilityError,
    DQCFailedError,
    DQCInconsistentDateUpdateRequestedError,
    DateNotConvertableToMonthlyError
)

HOSTNAME = os.environ.get("HOSTNAME", "dummy")

@pytest.mark.skipif("uan" not in HOSTNAME, reason="Databridge connection can only be tested in Lumi")
@mock.patch.dict(os.environ, {"FDB_HOME": "/appl/local/climatedt/databridge", "FDB5_CONFIG_FILE": "/appl/local/climatedt/databridge/etc/fdb/config.yaml"})
def test_dqc_pass_full(dqc_hl_full):
    dqc = dqc_hl_full
    dqc.run_dqc()

    assert dqc.n_messages == 48
    assert dqc.sample_length is None
    assert dqc.current_sample_length is None
    assert dqc.n_checked_messages == 48
    assert not dqc.any_failed

@pytest.mark.skipif("uan" not in HOSTNAME, reason="Databridge connection can only be tested in Lumi")
@mock.patch.dict(os.environ, {"FDB_HOME": "/appl/local/climatedt/databridge", "FDB5_CONFIG_FILE": "/appl/local/climatedt/databridge/etc/fdb/config.yaml"})
def test_dqc_pass_subsampled(dqc_hl_subsampled):
    dqc = dqc_hl_subsampled
    dqc.run_dqc()

    assert dqc.n_messages == 48
    assert dqc.sample_length == 10
    assert dqc.current_sample_length == 10
    assert dqc.n_checked_messages == 10
    assert not dqc.any_failed

@pytest.mark.skipif("uan" not in HOSTNAME, reason="Databridge connection can only be tested in Lumi")
@mock.patch.dict(os.environ, {"FDB_HOME": "/appl/local/climatedt/databridge", "FDB5_CONFIG_FILE": "/appl/local/climatedt/databridge/etc/fdb/config.yaml"})
def test_dqc_pass_oversampled(dqc_hl_oversampled):
    dqc = dqc_hl_oversampled
    dqc.run_dqc()

    assert dqc.n_messages == 48
    assert dqc.sample_length == 50
    assert dqc.current_sample_length is None
    assert dqc.n_checked_messages == 48
    assert not dqc.any_failed

@pytest.mark.xfail(reason="DQC check on tables Version is currently disabled")
def test_dqc_fail_standard_compliance(dqc_dac_passed, grib_tempfile_wrong_tables_version):
    iterator = MessageIterator(grib_tempfile_wrong_tables_version)
    dqc = dqc_dac_passed
    dqc.run_message_checker(
        request=dqc.request,
        iterator=iterator
    )
    assert dqc.profile_status == 2

@pytest.mark.xfail(reason="DQC check parameter defining GRIB keys is disabled since v2.9.3")
def test_dqc_fail_standard_compliance_second_surface(dqc_dac_passed, grib_tempfile_wrong_second_surface_ocean):
    iterator = MessageIterator(grib_tempfile_wrong_second_surface_ocean)
    dqc = dqc_dac_passed
    dqc._check_spatial_consistency = False  # To avoid DQC complaining about grid
    dqc.run_message_checker(
        request=dqc.request,
        iterator=iterator
    )
    assert dqc.profile_status == 2

def test_dqc_fail_spatial_consistency(dqc_dac_passed, grib_tempfile_h128_ring):
    iterator = MessageIterator(grib_tempfile_h128_ring)
    dqc = dqc_dac_passed
    dqc.run_message_checker(
        request=dqc.request,
        iterator=iterator
    )
    assert dqc.profile_status == 4

def test_dqc_fail_spatial_completeness(dqc_dac_passed, grib_tempfile_wrong_bitmap):
    iterator = MessageIterator(grib_tempfile_wrong_bitmap)
    dqc = dqc_dac_passed
    dqc.run_message_checker(
        request=dqc.request,
        iterator=iterator
    )
    assert dqc.profile_status == 8

def test_dqc_fail_physical_plausibility(dqc_dac_passed, grib_tempfile_wrong_values):
    iterator = MessageIterator(grib_tempfile_wrong_values)
    dqc = dqc_dac_passed
    dqc.run_message_checker(
        request=dqc.request,
        iterator=iterator
    )
    assert dqc.profile_status == 16

def test_dqc_pp_max_temperature(eccodes_msgid_h128_nest, debug_logger):
    msgid = eccodes_msgid_h128_nest
    variable_db = dqc_wrapper.DQCWrapper.read_variable_database()
    values = ecc.codes_get_array(msgid, 'values')
    values[10] = 1001.0
    ecc.codes_set_array(msgid, 'values', values)
    checker = PhysicalPlausibilityChecker(msgid, logger=debug_logger, variable_db=variable_db)
    checker.run()

    assert checker.status == 1

def test_dqc_pp_min_temperature(eccodes_msgid_h128_nest, debug_logger):
    msgid = eccodes_msgid_h128_nest
    variable_db = dqc_wrapper.DQCWrapper.read_variable_database()
    values = ecc.codes_get_array(msgid, 'values')
    values[10] = -1.0
    ecc.codes_set_array(msgid, 'values', values)
    checker = PhysicalPlausibilityChecker(msgid, logger=debug_logger, variable_db=variable_db)
    checker.run()

    assert checker.status == 1

def test_dqc_pp_unknown_variable(eccodes_msgid_h128_nest, debug_logger):
    msgid = eccodes_msgid_h128_nest
    variable_db = dqc_wrapper.DQCWrapper.read_variable_database()
    ecc.codes_set(msgid, 'parameterCategory', 1)
    ecc.codes_set(msgid, 'parameterNumber', 93)  # 228037 (2rhw)
    checker = PhysicalPlausibilityChecker(msgid, logger=debug_logger, variable_db=variable_db)
    checker.run()

    assert checker.status == 1

def test_dqc_spatcon_wrong_ordering(eccodes_msgid_h128_nest, debug_logger):
    msgid = eccodes_msgid_h128_nest
    ecc.codes_set(msgid, 'ordering', 0)
    grid_config = Path(dqc_wrapper.__file__).parent / "profiles/grids/healpix_128_nest.yaml"
    keys = dqc_wrapper.DQCWrapper.load_yaml_file(grid_config)
    checker = SpatialConsistencyChecker(msgid=msgid, keys=keys, logger=debug_logger)
    checker.run()

    assert checker.status == 1

def test_dqc_spatcon_wrong_nside(eccodes_msgid_h128_nest, debug_logger):
    msgid = eccodes_msgid_h128_nest
    ecc.codes_set(msgid, 'Nside', 32)
    grid_config = Path(dqc_wrapper.__file__).parent / "profiles/grids/healpix_128_nest.yaml"
    keys = dqc_wrapper.DQCWrapper.load_yaml_file(grid_config)
    checker = SpatialConsistencyChecker(msgid=msgid, keys=keys, logger=debug_logger)
    checker.run()

    assert checker.status == 1

def test_dqc_spatcom_wrong_bitmap_atmos(eccodes_msgid_h128_nest, debug_logger):
    msgid = eccodes_msgid_h128_nest
    ecc.codes_set(msgid, 'bitMapIndicator', 0)
    checker = SpatialCompletenessChecker(msgid=msgid, logger=debug_logger)
    checker.run()

    assert checker.status == 1

def test_dqc_spatcom_wrong_bitmap_ocean(eccodes_msgid_h128_nest, debug_logger):
    msgid = eccodes_msgid_h128_nest
    # Set paramId to 262101 (tos)
    ecc.codes_set(msgid, 'discipline', 10)
    ecc.codes_set(msgid, 'parameterCategory', 3)
    ecc.codes_set(msgid, 'parameterNumber', 3)
    ecc.codes_set(msgid, 'typeOfFirstFixedSurface', 160)
    ecc.codes_set(msgid, 'typeOfSecondFixedSurface', 255)
    ecc.codes_set(msgid, 'scaledValueOfFirstFixedSurface', 0)
    ecc.codes_set(msgid, 'scaleFactorOfFirstFixedSurface', 0)
    checker = SpatialCompletenessChecker(msgid=msgid, logger=debug_logger)
    checker.run()

    assert checker.status == 1

def test_dqc_spatcom_get_checking_fn_atmos():
    checker = SpatialCompletenessChecker(msgid=0, logger=None)
    assert checker.get_checking_fn("sfc") == checker.check_atmos_variable
    assert checker.get_checking_fn("pl") == checker.check_atmos_variable
    assert checker.get_checking_fn("hl") == checker.check_atmos_variable
    assert checker.get_checking_fn("sol") == checker.check_atmos_variable

def test_dqc_spatcom_get_checking_fn_ocean():
    checker = SpatialCompletenessChecker(msgid=0, logger=None)
    assert checker.get_checking_fn("o2d") == checker.check_ocean_variable
    assert checker.get_checking_fn("o3d") == checker.check_ocean_variable

def test_dqc_spatcom_get_checking_fn_unknown_levtype():
    checker = SpatialCompletenessChecker(msgid=0, logger=None)
    with pytest.raises(UnknownLevtypeError):
        checker.get_checking_fn("dummy")

@pytest.mark.xfail(reason="DQC check on tables Version is currently disabled")
def test_dqc_stdcom_wrong_table_version(eccodes_msgid_h128_nest, debug_logger):
    msgid = eccodes_msgid_h128_nest
    ecc.codes_set(msgid, 'tablesVersion', 32)
    checker = StandardComplianceChecker(msgid=msgid, logger=debug_logger)
    checker.run()

    assert checker.status == 1

def test_dqc_stdcom_wrong_centre(eccodes_msgid_h128_nest, debug_logger):
    msgid = eccodes_msgid_h128_nest
    ecc.codes_set(msgid, 'centre', 0)
    checker = StandardComplianceChecker(msgid=msgid, logger=debug_logger)
    checker.run()

    assert checker.status == 1

def test_dqc_stdcom_wrong_prodtype(eccodes_msgid_h128_nest, debug_logger):
    msgid = eccodes_msgid_h128_nest
    ecc.codes_set(msgid, 'productionStatusOfProcessedData', 13)
    checker = StandardComplianceChecker(msgid=msgid, logger=debug_logger)
    checker.run()

    assert checker.status == 1

def test_invalid_halt_mode():
    with pytest.raises(DQCInvalidHaltModeError):
        dqc_wrapper.DQCWrapper(
            profile_path=Path(dqc_wrapper.__file__).parent / "profiles/production/ifs-nemo",
            halt_mode = "dummy"
        )

def test_invalid_profile_file():
    with pytest.raises(DQCMissingProfilesError):
        dqc_wrapper.DQCWrapper(
            profile_path=Path(dqc_wrapper.__file__).parent / "profiles/production/ifs-nemo",
            profiles=["dummy.yaml"]
            )


# def test_invalid_profile_file_missing_ok():
#     dqc = dqc_wrapper.DQCWrapper(
#         profile_path=Path(dqc_wrapper.__file__).parent / "profiles/production/ifs-nemo",
#         missing_profiles_ok=True,
#         profiles=["dummy.yaml"]
#         )

#     assert not dqc.profiles

def test_update_variables_db(user_variables_database):
    dqc = dqc_wrapper.DQCWrapper(
        profile_path=Path(__file__).parent / "testing_profiles",
        variables_config=user_variables_database
    )
    assert dqc.variable_db[167]["min"] == 0.0

def test_default_variables_all_enabled():
    conf_path = Path(dqc_wrapper.__file__).parent / "profiles/config/variables.yaml"
    with open(conf_path, 'r') as f:
        variable_db = yaml.safe_load(f)

    for variable in variable_db.values():
        assert variable["check_enabled"]

def test_dqc_pass_disabled_variable(dqc_dac_passed_2t_disabeld, grib_tempfile_wrong_values):
    iterator = MessageIterator(grib_tempfile_wrong_values)
    dqc = dqc_dac_passed_2t_disabeld
    dqc.run_message_checker(
        request=dqc.request,
        iterator=iterator
    )
    assert dqc.profile_status == 0

def test_dqc_missing_profiles():
    with pytest.raises(DQCMissingProfilesError):
        dqc_wrapper.DQCWrapper(profile_path="dummy")

def test_exclude_profiles():
    dqc = dqc_wrapper.DQCWrapper(
        profile_path=Path(dqc_wrapper.__file__).parent / "profiles/production/ifs-nemo",
        exclude_profiles = ["sfc_daily_healpix_standard.yaml", "sfc_daily_healpix_high.yaml"]
        )
    assert dqc.profiles
    assert "sfc_daily_healpix_standard.yaml" not in dqc.profiles
    assert "sfc_daily_healpix_high.yaml" not in dqc.profiles

def test_convert_to_steps_no_start_date(fdb_new_hourly_request):
    dqc = dqc_wrapper.DQCWrapper(
        profile_path=Path(dqc_wrapper.__file__).parent / "profiles/production/ifs-nemo",
        )
    with pytest.raises(DQCMissingStartDateError):
        dqc.convert_to_steps(fdb_new_hourly_request)

@pytest.mark.xfail(reason="DQC check on tables Version is currently disabled")
def test_dqc_stdcom_halt_always(dqc_dac_passed_halt_always, grib_tempfile_wrong_tables_version):
    iterator = MessageIterator(grib_tempfile_wrong_tables_version)
    dqc = dqc_dac_passed_halt_always
    dqc.check_spatial_completeness = False
    dqc.check_spatial_consistency = False
    dqc.check_physical_plausibility = False
    with pytest.raises(DQCStandardComplianceError):
        dqc.run_message_checker(
            request=dqc.request,
            iterator=iterator
        )

def test_dqc_spatcom_halt_always(dqc_dac_passed_halt_always, grib_tempfile_wrong_bitmap):
    iterator = MessageIterator(grib_tempfile_wrong_bitmap)
    dqc = dqc_dac_passed_halt_always
    dqc.check_standard_compliance = False
    dqc.check_spatial_consistency = False
    dqc.check_physical_plausibility = False
    with pytest.raises(DQCSpatialCompletenessError):
        dqc.run_message_checker(
            request=dqc.request,
            iterator=iterator
        )

def test_dqc_spatcon_halt_always(dqc_dac_passed_halt_always, grib_tempfile_h128_ring):
    iterator = MessageIterator(grib_tempfile_h128_ring)
    dqc = dqc_dac_passed_halt_always
    dqc.check_standard_compliance = False
    dqc.check_spatial_completeness = False
    dqc.check_physical_plausibility = False
    with pytest.raises(DQCSpatialConsistencyError):
        dqc.run_message_checker(
            request=dqc.request,
            iterator=iterator
        )

def test_dqc_pp_halt_always(dqc_dac_passed_halt_always, grib_tempfile_wrong_values):
    iterator = MessageIterator(grib_tempfile_wrong_values)
    dqc = dqc_dac_passed_halt_always
    dqc.check_standard_compliance = False
    dqc.check_spatial_completeness = False
    dqc.check_physical_plausibility = False
    with pytest.raises(DQCPhysicalPlausibilityError):
        dqc.run_message_checker(
            request=dqc.request,
            iterator=iterator
        )

@pytest.mark.xfail(reason="DQC check on tables Version is currently disabled")
def test_dqc_stdcom_end_error(dqc_dac_passed_halt_always, grib_tempfile_wrong_tables_version):
    dqc_dac_passed_halt_always.halt_mode = "end"
    iterator = MessageIterator(grib_tempfile_wrong_tables_version)
    dqc = dqc_dac_passed_halt_always
    dqc.check_spatial_completeness = False
    dqc.check_spatial_consistency = False
    dqc.check_physical_plausibility = False
    dqc.run_message_checker(
            request=dqc.request,
            iterator=iterator
    )
    with pytest.raises(DQCFailedError):
        dqc.report_general_result()

def test_dqc_spatcom_end_error(dqc_dac_passed_halt_always, grib_tempfile_wrong_bitmap):
    dqc_dac_passed_halt_always.halt_mode = "end"
    iterator = MessageIterator(grib_tempfile_wrong_bitmap)
    dqc = dqc_dac_passed_halt_always
    dqc.check_standard_compliance = False
    dqc.check_spatial_consistency = False
    dqc.check_physical_plausibility = False
    dqc.run_message_checker(
            request=dqc.request,
            iterator=iterator
    )
    with pytest.raises(DQCFailedError):
        dqc.report_general_result()

def test_dqc_spatcon_end_error(dqc_dac_passed_halt_always, grib_tempfile_h128_ring):
    dqc_dac_passed_halt_always.halt_mode = "end"
    iterator = MessageIterator(grib_tempfile_h128_ring)
    dqc = dqc_dac_passed_halt_always
    dqc.check_standard_compliance = False
    dqc.check_spatial_completeness = False
    dqc.check_physical_plausibility = False
    dqc.run_message_checker(
            request=dqc.request,
            iterator=iterator
    )
    with pytest.raises(DQCFailedError):
        dqc.report_general_result()

def test_dqc_pp_end_error(dqc_dac_passed_halt_always, grib_tempfile_wrong_values):
    dqc_dac_passed_halt_always.halt_mode = "end"
    iterator = MessageIterator(grib_tempfile_wrong_values)
    dqc = dqc_dac_passed_halt_always
    dqc.check_standard_compliance = False
    dqc.check_spatial_completeness = False
    dqc.check_physical_plausibility = False
    dqc.run_message_checker(
            request=dqc.request,
            iterator=iterator
    )
    with pytest.raises(DQCFailedError):
        dqc.report_general_result()

def test_dqc_not_update_request_clte():
    """
    DQC date update case 1: date-time request, no update.

    Expected behaviour: request is parsed as it is with no updates.
    """
    dqc = dqc_wrapper.DQCWrapper(
        profile_path=Path(__file__).parent / "testing_profiles",
        profiles=["sfc_hourly_healpix_high.yaml"],
        )
    request = dqc.get_updated_request(dqc.profiles[0])
    assert request["date"] == ["19900101"]
    assert request["time"] == [f"{i:02}00" for i in range(24)]
    assert "month" not in request
    assert "year" not in request

def test_dqc_not_update_request_clmn():
    """
    DQC date update case 2: month-year request, no update.

    Expected behaviour: reuqest is parsed as it is with no updates.
    """
    dqc = dqc_wrapper.DQCWrapper(
        profile_path=Path(__file__).parent / "testing_profiles",
        profiles=["sfc_monthly_healpix_high.yaml"],
        )
    request = dqc.get_updated_request(dqc.profiles[0])
    assert request["month"] == [str(i) for i in range(1, 13)]
    assert request["year"] == ["1990"]
    assert "date" not in request
    assert "time" not in request

def test_dqc_update_request_date_clte():
    """
    DQC date update case 3: date-time request, only date updated.

    Expected behaviour: date is updated in request and time is parsed
    as it is in the profile.
    """
    dqc = dqc_wrapper.DQCWrapper(
        profile_path=Path(__file__).parent / "testing_profiles",
        profiles=["sfc_hourly_healpix_high.yaml"],
        date="20200101"
        )
    request = dqc.get_updated_request(dqc.profiles[0])
    assert request["date"] == ["20200101"]
    assert request["time"] == [f"{i:02}00" for i in range(24)]
    assert "month" not in request
    assert "year" not in request

def test_dqc_update_request_time_clte():
    """
    DQC date update case 4: date-time request, only time updated.

    Expected behaviour: time is updated in request and date is parsed
    as it is in the profile.
    """
    dqc = dqc_wrapper.DQCWrapper(
        profile_path=Path(__file__).parent / "testing_profiles",
        profiles=["sfc_hourly_healpix_high.yaml"],
        time="0000/to/2300/by/0600"
        )
    request = dqc.get_updated_request(dqc.profiles[0])
    assert request["date"] == ["19900101"]
    assert request["time"] == [f"{6*i:02}00" for i in range(4)]
    assert "month" not in request
    assert "year" not in request

def test_dqc_update_request_date_time_clte():
    """
    DQC date update case 5: date-time request, date and time udpated.

    Expected behaviour: date and time are updated in the requst.
    """
    dqc = dqc_wrapper.DQCWrapper(
        profile_path=Path(__file__).parent / "testing_profiles",
        profiles=["sfc_hourly_healpix_high.yaml"],
        date="20200101",
        time="0000/to/2300/by/0600"
        )
    request = dqc.get_updated_request(dqc.profiles[0])
    assert request["date"] == ["20200101"]
    assert request["time"] == [f"{6*i:02}00" for i in range(4)]
    assert "month" not in request
    assert "year" not in request

def test_dqc_update_request_month_clte():
    """
    DQC date update case 6: date-time request, month updated.

    Expected behaviour: a DQCInconsistentDateUpdateRequestedError
    is raised since user is not supposed to updated a date-time request
    with month-year values.
    """
    dqc = dqc_wrapper.DQCWrapper(
        profile_path=Path(__file__).parent / "testing_profiles",
        profiles=["sfc_hourly_healpix_high.yaml"],
        month="1",
        )
    with pytest.raises(DQCInconsistentDateUpdateRequestedError):
        dqc.get_updated_request(dqc.profiles[0])

def test_dqc_update_request_year_clte():
    """
    DQC date update case 7: date-time request, year updated.

    Expected behaviour: a DQCInconsistentDateUpdateRequestedError
    is raised since user is not supposed to updated a date-time request
    with month-year values.
    """
    dqc = dqc_wrapper.DQCWrapper(
        profile_path=Path(__file__).parent / "testing_profiles",
        profiles=["sfc_hourly_healpix_high.yaml"],
        year="2020",
        )
    with pytest.raises(DQCInconsistentDateUpdateRequestedError):
        dqc.get_updated_request(dqc.profiles[0])

def test_dqc_update_request_month_year_clte():
    """
    DQC date update case 8: date-time request, month and  year updated.

    Expected behaviour: a DQCInconsistentDateUpdateRequestedError
    is raised since user is not supposed to updated a date-time request
    with month-year values.
    """
    dqc = dqc_wrapper.DQCWrapper(
        profile_path=Path(__file__).parent / "testing_profiles",
        profiles=["sfc_hourly_healpix_high.yaml"],
        month="1",
        year="2020",
        )
    with pytest.raises(DQCInconsistentDateUpdateRequestedError):
        dqc.get_updated_request(dqc.profiles[0])

def test_dqc_update_request_mixed_clte():
    """
    DQC date update case 9: date-time request, month and date updated.

    Expected behaviour a DQCInconsistentDateUpdateRequestedError
    is raised since user is not supposed to updated a dates with a
    mixture of date-time and month-year values.
    """
    dqc = dqc_wrapper.DQCWrapper(
        profile_path=Path(__file__).parent / "testing_profiles",
        profiles=["sfc_hourly_healpix_high.yaml"],
        date="20200101",
        month="1",
        )
    with pytest.raises(DQCInconsistentDateUpdateRequestedError):
        dqc.get_updated_request(dqc.profiles[0])

def test_dqc_update_request_mixed_clmn():
    """
    DQC date update case 10: month-year request, year and time updated.

    Expected behaviour a DQCInconsistentDateUpdateRequestedError
    is raised since user is not supposed to updated a dates with a
    mixture of date-time and month-year values.
    """
    dqc = dqc_wrapper.DQCWrapper(
        profile_path=Path(__file__).parent / "testing_profiles",
        profiles=["sfc_monthly_healpix_high.yaml"],
        time="0000",
        year="2020",
        )
    with pytest.raises(DQCInconsistentDateUpdateRequestedError):
        dqc.get_updated_request(dqc.profiles[0])

def test_dqc_update_request_month_clmn():
    """
    DQC date update case 11: month-year request, month updated.

    Expected behaviour: month is updated in the request and year
    is parsed as it is in the profile.
    """
    dqc = dqc_wrapper.DQCWrapper(
        profile_path=Path(__file__).parent / "testing_profiles",
        profiles=["sfc_monthly_healpix_high.yaml"],
        month="1/to/12/by/2",
        )
    request = dqc.get_updated_request(dqc.profiles[0])
    assert request["month"] == ["1", "3", "5", "7", "9", "11"]
    assert request["year"] == ["1990"]
    assert "date" not in request
    assert "time" not in request

def test_dqc_update_request_year_clmn():
    """
    DQC date update case 12: month-year request, year updated.

    Expected behaviour: year is updated in the request and month
    is parsed as it is in the profile.
    """
    dqc = dqc_wrapper.DQCWrapper(
        profile_path=Path(__file__).parent / "testing_profiles",
        profiles=["sfc_monthly_healpix_high.yaml"],
        year="2020/to/2022",
        )
    request = dqc.get_updated_request(dqc.profiles[0])
    assert request["month"] == [str(i) for i in range(1, 13)]
    assert request["year"] == ["2020", "2021", "2022"]
    assert "date" not in request
    assert "time" not in request

def test_dqc_update_request_month_year_clmn():
    """
    DQC date update case 13: month-year request, month and year updated.

    Expected behaviour: month and year are updated in the request.
    """
    dqc = dqc_wrapper.DQCWrapper(
        profile_path=Path(__file__).parent / "testing_profiles",
        profiles=["sfc_monthly_healpix_high.yaml"],
        month="1/to/12/by/2",
        year="2020/to/2022",
        )
    request = dqc.get_updated_request(dqc.profiles[0])
    assert request["month"] == ["1", "3", "5", "7", "9", "11"]
    assert request["year"] == ["2020", "2021", "2022"]
    assert "date" not in request
    assert "time" not in request

def test_dqc_update_request_date_clmn():
    """
    DQC date update case 14: month-year request, date updated.

    Expected behaviour: date is updated and the request is converted
    back to month-year format, with the new dates.

    This works because the requested dates fill a full month.
    """
    dqc = dqc_wrapper.DQCWrapper(
        profile_path=Path(__file__).parent / "testing_profiles",
        profiles=["sfc_monthly_healpix_high.yaml"],
        date="20200101/to/20200131",
        )
    request = dqc.get_updated_request(dqc.profiles[0])
    assert request["month"] == ["1"]
    assert request["year"] == ["2020"]
    assert "date" not in request
    assert "time" not in request

def test_dqc_update_request_date_time_clmn():
    """
    DQC date update case 15: month-year request, date and time updated.

    Expected behaviour: date and time are updated and the requets is
    converted back to month-year format, with the new dates. As time
    is not used in the calculation of months and years, it does not
    play any significant role.

    This works because the requested dates fill a full month.
    """
    dqc = dqc_wrapper.DQCWrapper(
        profile_path=Path(__file__).parent / "testing_profiles",
        profiles=["sfc_monthly_healpix_high.yaml"],
        date="20200101/to/20200131",
        time="0000/to/2300/by/0600"
        )
    request = dqc.get_updated_request(dqc.profiles[0])
    assert request["month"] == ["1"]
    assert request["year"] == ["2020"]
    assert "date" not in request
    assert "time" not in request

def test_dqc_update_request_date_multiple_years_clmn():
    """
    DQC date update (special) case 16: month-year requets, date updated

    Same as case 14 but with multiple years in the date range.

    Expected behaviour: date is updated and the request is converted
    back to month-year format, with the new dates.

    This no months are left incomplete and all the years have the
    same set of months.
    """
    dqc = dqc_wrapper.DQCWrapper(
        profile_path=Path(__file__).parent / "testing_profiles",
        profiles=["sfc_monthly_healpix_high.yaml"],
        date="20200101/to/20221231",
        )
    request = dqc.get_updated_request(dqc.profiles[0])
    assert request["month"] == [str(i) for i in range(1, 13)]
    assert request["year"] == ["2020", "2021", "2022"]
    assert "date" not in request
    assert "time" not in request

def test_dqc_update_request_fail_date_clmn_incomplete_month():
    """
    DQC date update (edge) case 17: month-year request, date updated.

    Edge case: the requested dates do not fill a full month.

    Expected behaviour: a DateNotConvertableToMonthlyError is raised
    as the requested dates list contains an incomplete month.
    """
    dqc = dqc_wrapper.DQCWrapper(
        profile_path=Path(__file__).parent / "testing_profiles",
        profiles=["sfc_monthly_healpix_high.yaml"],
        date="20200101/to/20200115",
        )
    with pytest.raises(DateNotConvertableToMonthlyError):
        dqc.get_updated_request(dqc.profiles[0])

def test_dqc_update_request_fail_date_clmn_offset_month():
    """
    DQC date update (edge) case 18: month-year request, date updated.

    Edge case: the requested dates span for a month but not starting
    at first day of month.

    Expected behaviour: a DateNotConvertableToMonthlyError is raised
    as the requested dates list contains incomplete months.
    """
    dqc = dqc_wrapper.DQCWrapper(
        profile_path=Path(__file__).parent / "testing_profiles",
        profiles=["sfc_monthly_healpix_high.yaml"],
        date="20200120/to/20200219",
        )
    with pytest.raises(DateNotConvertableToMonthlyError):
        dqc.get_updated_request(dqc.profiles[0])

def test_dqc_update_request_fail_date_clmn_incomplete_year():
    """
    DQC date update (edge) case 19: month-year request, date updated.

    Edge case: the requested dates contain different months
    for each year.

    Expected behaviour: a DateNotConvertableToMonthlyError is raised
    since even with full months the list of dates cannot consistently
    be converted into a list of months and years, as different years
    contain different months.
    """
    dqc = dqc_wrapper.DQCWrapper(
        profile_path=Path(__file__).parent / "testing_profiles",
        profiles=["sfc_monthly_healpix_high.yaml"],
        date="20201231/to/20210131",
        )
    with pytest.raises(DateNotConvertableToMonthlyError):
        dqc.get_updated_request(dqc.profiles[0])

def test_dqc_update_request_date_clte_and_clmn():
    """
    DQC date update (special) case 20: updating same date in both profiles.

    Integration test to check how the DQC would behave when profiles
    of both time formats are used in the same DQC API call.

    Expected behaviour: both requests are updated with the provided
    date and times, but the month-year request is converted back to
    month-year format, with the new dates.
    """
    dqc = dqc_wrapper.DQCWrapper(
        profile_path=Path(__file__).parent / "testing_profiles",
        profiles=["sfc_hourly_healpix_high.yaml", "sfc_monthly_healpix_high.yaml"],
        date="20200101/to/20200131",
        )
    # Request 1: clte expected full month in hourly timesteps
    request = dqc.get_updated_request(dqc.profiles[0])
    print(request)
    assert request["date"] == [f"202001{i:02}" for i in range(1, 32)]
    assert request["time"] == [f"{i:02}00" for i in range(24)]
    assert "month" not in request
    assert "year" not in request

    # Request 2: clmn expected single month
    request = dqc.get_updated_request(dqc.profiles[1])
    print(request)
    assert request["month"] == ["1"]
    assert request["year"] == ["2020"]
    assert "date" not in request
    assert "time" not in request

def test_dqc_generation_updated():
    dqc = dqc_wrapper.DQCWrapper(
        profile_path=Path(__file__).parent / "testing_profiles",
        profiles=["sfc_hourly_healpix_high.yaml"],
        generation=2
        )
    request = dqc.get_updated_request(dqc.profiles[0])
    assert request["generation"] == 2

def test_dqc_generation_not_updated():
    dqc = dqc_wrapper.DQCWrapper(
        profile_path=Path(__file__).parent / "testing_profiles",
        profiles=["sfc_hourly_healpix_high.yaml"],
        )
    request = dqc.get_updated_request(dqc.profiles[0])
    assert request["generation"] == 1

def test_dqc_monthly_submonthly_allowed():
    """
    Check the feature that skips monthly profiles when date is updated
    with the `date` key and a submonthly chunk.

    The example only uses a monthly profile, so the dqc.run() should
    just skip that profile and rin successfully (even in an
    environment with no data).
    """
    dqc = dqc_wrapper.DQCWrapper(
        profile_path=Path(__file__).parent / "testing_profiles",
        profiles=["sfc_monthly_healpix_high.yaml"],
        date="20200101",
        allow_submonthly_chunks=True,
        )
    dqc.run_dqc()

def test_dqc_monthly_submonthly_not_allowed():
    """
    Check that default option still prevents submonthly dates
    to be used to update monthly profiles.

    The example only uses a monthly profile, so the dqc.run() should
    raise an error before trying to read any data.
    """
    dqc = dqc_wrapper.DQCWrapper(
        profile_path=Path(__file__).parent / "testing_profiles",
        profiles=["sfc_monthly_healpix_high.yaml"],
        date="20200101",
        )
    with pytest.raises(DateNotConvertableToMonthlyError):
        dqc.run_dqc()

def test_dqc_pp_tcc_passes(eccodes_msgid_tcc, debug_logger):
    """
    Docstrings
    """
    msgid = eccodes_msgid_tcc
    variable_db = dqc_wrapper.DQCWrapper.read_variable_database()
    #values = ecc.codes_get_array(msgid, 'values')
    #values[10] = 1001.0
    #ecc.codes_set_array(msgid, 'values', values)
    checker = PhysicalPlausibilityChecker(msgid, logger=debug_logger, variable_db=variable_db)
    checker.run()

    assert checker.status == 0

def test_dqc_pp_tcc_lower_treshold_error(eccodes_msgid_tcc, debug_logger):
    """
    Docstrings
    """
    # Get tcc msgid with random values from 0-100
    msgid = eccodes_msgid_tcc
    variable_db = dqc_wrapper.DQCWrapper.read_variable_database()

    # Set random values from 0-1 to mock tcc writing in 0-1 units.
    values = ecc.codes_get_array(msgid, 'values')
    n_values = len(values)
    values = np.random.rand(n_values)
    ecc.codes_set_array(msgid, 'values', values)

    # Run checker
    checker = PhysicalPlausibilityChecker(msgid, logger=debug_logger, variable_db=variable_db)
    checker.run()

    assert checker.status == 1