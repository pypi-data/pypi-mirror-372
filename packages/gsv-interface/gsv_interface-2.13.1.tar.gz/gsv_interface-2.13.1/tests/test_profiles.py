from pathlib import Path
from tempfile import TemporaryDirectory

import yaml

from gsv.dqc.profiles.scripts.generate_profiles import main as generate_profiles


ARGUMENTS_v_1_1_0 = [
    "--repo-path", str(Path(__file__).parent / "testing_portfolios/v1.1.0"),
    "--tag", "v1.1.0",
    "--portfolio", "production",
    "--configuration", "production",
    "--output-dir", TemporaryDirectory().name
]


ARGUMENTS_v_1_2_0 = [
    "--repo-path", str(Path(__file__).parent / "testing_portfolios/v1.2.0"),
    "--tag", "v1.2.0",
    "--portfolio", "production",
    "--configuration", "production",
    "--output-dir", TemporaryDirectory().name
]


ARGUMENTS_v_1_3_0_FULL = [
    "--repo-path", str(Path(__file__).parent / "testing_portfolios/v1.3.0"),
    "--tag", "v1.3.0",
    "--portfolio", "full",
    "--configuration", "production",
    "--output-dir", TemporaryDirectory().name
]


ARGUMENTS_v_1_3_0_REDUCED = [
    "--repo-path", str(Path(__file__).parent / "testing_portfolios/v1.3.0"),
    "--tag", "v1.3.0",
    "--portfolio", "reduced",
    "--configuration", "production",
    "--output-dir", TemporaryDirectory().name
]


ARGUMENTS_v_2_0_0_FULL = [
    "--repo-path", str(Path(__file__).parent / "testing_portfolios/v2.0.0"),
    "--tag", "v2.0.0",
    "--portfolio", "full",
    "--configuration", "production",
    "--output-dir", TemporaryDirectory().name
]

def get_generated_profiles_list(profile_path):
    profiles = [f.stem for f in profile_path.iterdir() if f.is_file()]
    return sorted(profiles)

def validate_profile(profile, model, content):
    # General keys validation
    assert content["mars-keys"]["model"] == model
    assert content["mars-keys"]["levtype"] == profile.split("_")[0]
    assert content["mars-keys"]["resolution"] == profile.split("_")[-1]

    # Assert variable list is not empty
    assert content["mars-keys"]["param"]

    # Validate grid is correctly decoded (only for production configuration)
    if profile.split("_")[-1] == "high":
        assert content["grid"] == "H1024"
    
    elif profile.split("_")[-1] == "standard":
        assert content["grid"] == "H128"

    # Validate date-format and time keys
    if profile.split("_")[1] == "hourly":
        assert content["date-format"] == "date"
        assert content["mars-keys"]["time"] == "0000/to/2300/by/0100"
        assert content["mars-keys"]["stream"] == "clte"

    elif profile.split("_")[1] == "daily":
        assert content["date-format"] == "date"
        assert content["mars-keys"]["time"] == "0000"
        assert content["mars-keys"]["stream"] == "clte"

    elif profile.split("_")[1] == "monthly":
        assert content["date-format"] == "month"
        assert content["mars-keys"]["stream"] == "clmn"

def validate_header(file, dp_version, portfolio, configuration):
    file.seek(0)
    lines = file.readlines()
    assert lines[0] == f"# Profile automatically generated with profile_generator.py based on Data Portfolio version: {dp_version}, portfolio: {portfolio}, configuration: {configuration}.\n"


def test_profile_generation_portfolio_v1_1_0_ifs_nemo():
    argv = ARGUMENTS_v_1_1_0
    dp_version = argv[3]
    portfolio = argv[5]
    configuration = argv[7]
    profile_path = argv[9]
    generate_profiles(argv)

    # Check IFS-NEMO v1.1.0, portfolio: production, configuration: production
    profiles_ifs_nemo = get_generated_profiles_list(Path(profile_path) / "ifs-nemo")
    expected_profiles_ifs_nemo = [
        "hl_hourly_healpix_high",
        "hl_hourly_healpix_standard",
        "hl_monthly_healpix_high",
        "hl_monthly_healpix_standard",
        "o2d_daily_healpix_high",
        "o2d_daily_healpix_standard",
        "o2d_monthly_healpix_high",
        "o2d_monthly_healpix_standard",
        "o3d_daily_healpix_high",
        "o3d_daily_healpix_standard",
        "o3d_monthly_healpix_high",
        "o3d_monthly_healpix_standard",
        "pl_hourly_healpix_high",
        "pl_hourly_healpix_standard",
        "pl_monthly_healpix_high",
        "pl_monthly_healpix_standard",
        "sfc_daily_healpix_high",
        "sfc_daily_healpix_standard",
        "sfc_hourly_healpix_high",
        "sfc_hourly_healpix_standard",
        "sfc_monthly_healpix_high",
        "sfc_monthly_healpix_standard",
        "sol_2_hourly_healpix_high",
        "sol_2_hourly_healpix_standard",
        "sol_2_monthly_healpix_high",
        "sol_2_monthly_healpix_standard",
        "sol_hourly_healpix_high",
        "sol_hourly_healpix_standard",
        "sol_monthly_healpix_high",
        "sol_monthly_healpix_standard",
    ]
    assert len(profiles_ifs_nemo) == 30
    assert profiles_ifs_nemo == expected_profiles_ifs_nemo

    for profile in profiles_ifs_nemo:
        with open(Path(profile_path) / "ifs-nemo" / f"{profile}.yaml") as f:
            content = yaml.safe_load(f)
            validate_profile(profile, "ifs-nemo", content)
            validate_header(f, dp_version, portfolio, configuration)


def test_profile_generation_portfolio_v1_1_0_ifs_fesom():
    argv = ARGUMENTS_v_1_1_0
    dp_version = argv[3]
    portfolio = argv[5]
    configuration = argv[7]
    profile_path = argv[9]
    generate_profiles(argv)

    # Check IFS-FESOM v1.1.0, portfolio: production, configuration: production
    profiles_ifs_fesom = get_generated_profiles_list(Path(profile_path) / "ifs-fesom")
    expected_profiles_ifs_fesom = [
        "hl_hourly_healpix_high",
        "hl_hourly_healpix_standard",
        "hl_monthly_healpix_high",
        "hl_monthly_healpix_standard",
        "o2d_daily_healpix_high",
        "o2d_daily_healpix_standard",
        "o2d_monthly_healpix_high",
        "o2d_monthly_healpix_standard",
        "o3d_2_daily_healpix_high",
        "o3d_2_daily_healpix_standard",
        "o3d_2_monthly_healpix_high",
        "o3d_2_monthly_healpix_standard",
        "o3d_daily_healpix_high",
        "o3d_daily_healpix_standard",
        "o3d_monthly_healpix_high",
        "o3d_monthly_healpix_standard",
        "pl_hourly_healpix_high",
        "pl_hourly_healpix_standard",
        "pl_monthly_healpix_high",
        "pl_monthly_healpix_standard",
        "sfc_daily_healpix_high",
        "sfc_daily_healpix_standard",
        "sfc_hourly_healpix_high",
        "sfc_hourly_healpix_standard",
        "sfc_monthly_healpix_high",
        "sfc_monthly_healpix_standard",
        "sol_2_hourly_healpix_high",
        "sol_2_hourly_healpix_standard",
        "sol_2_monthly_healpix_high",
        "sol_2_monthly_healpix_standard",
        "sol_hourly_healpix_high",
        "sol_hourly_healpix_standard",
        "sol_monthly_healpix_high",
        "sol_monthly_healpix_standard",
    ]
    assert len(profiles_ifs_fesom) == 34
    assert profiles_ifs_fesom == expected_profiles_ifs_fesom

    for profile in profiles_ifs_fesom:
        with open(Path(profile_path) / "ifs-fesom" / f"{profile}.yaml") as f:
            content = yaml.safe_load(f)
            validate_profile(profile, "ifs-fesom", content)
            validate_header(f, dp_version, portfolio, configuration)


def test_profile_generation_portfolio_v1_1_0_icon():
    argv = ARGUMENTS_v_1_1_0
    dp_version = argv[3]
    portfolio = argv[5]
    configuration = argv[7]
    profile_path = argv[9]
    generate_profiles(argv)

    # Check ICON v1.1.0, portfolio: production, configuration: production
    profiles_icon = get_generated_profiles_list(Path(profile_path) / "icon")
    expected_profiles_icon = [
        "hl_hourly_healpix_high",
        "hl_monthly_healpix_high",
        "o2d_daily_healpix_high",
        "o2d_monthly_healpix_high",
        "o3d_2_daily_healpix_high",
        "o3d_2_monthly_healpix_high",
        "o3d_daily_healpix_high",
        "o3d_monthly_healpix_high",
        "pl_hourly_healpix_high",
        "pl_monthly_healpix_high",
        "sfc_daily_healpix_high",
        "sfc_hourly_healpix_high",
        "sfc_monthly_healpix_high",
        "sol_2_hourly_healpix_high",
        "sol_2_monthly_healpix_high",
        "sol_hourly_healpix_high",
        "sol_monthly_healpix_high",
    ]
    assert len(profiles_icon) == 17
    assert profiles_icon == expected_profiles_icon

    for profile in profiles_icon:
        with open(Path(profile_path) / "icon" / f"{profile}.yaml") as f:
            content = yaml.safe_load(f)
            validate_profile(profile, "icon", content)
            validate_header(f, dp_version, portfolio, configuration)


def test_profile_generation_portfolio_v1_2_0_ifs_nemo():
    argv = ARGUMENTS_v_1_2_0
    dp_version = argv[3]
    portfolio = argv[5]
    configuration = argv[7]
    profile_path = argv[9]
    generate_profiles(argv)

    # Check IFS-NEMO v1.2.0, portfolio: production, configuration: production
    profiles_ifs_nemo = get_generated_profiles_list(Path(profile_path) / "ifs-nemo")
    expected_profiles_ifs_nemo = [
        "hl_hourly_healpix_high",
        "hl_hourly_healpix_standard",
        "hl_monthly_healpix_standard",
        "o2d_daily_healpix_high",
        "o2d_daily_healpix_standard",
        "o2d_monthly_healpix_high",
        "o2d_monthly_healpix_standard",
        "o3d_2_monthly_healpix_standard",
        "o3d_daily_healpix_high",
        "o3d_daily_healpix_standard",
        "o3d_monthly_healpix_high",
        "o3d_monthly_healpix_standard",
        "pl_hourly_healpix_high",
        "pl_hourly_healpix_standard",
        "pl_monthly_healpix_standard",
        "sfc_daily_healpix_high",
        "sfc_daily_healpix_standard",
        "sfc_hourly_healpix_high",
        "sfc_hourly_healpix_standard",
        "sfc_monthly_healpix_high",
        "sfc_monthly_healpix_standard",
        "sol_2_hourly_healpix_high",
        "sol_2_hourly_healpix_standard",
        "sol_2_monthly_healpix_high",
        "sol_2_monthly_healpix_standard",
        "sol_hourly_healpix_high",
        "sol_hourly_healpix_standard",
        "sol_monthly_healpix_high",
        "sol_monthly_healpix_standard",
    ]
    assert len(profiles_ifs_nemo) == 29
    assert profiles_ifs_nemo == expected_profiles_ifs_nemo

    for profile in profiles_ifs_nemo:
        with open(Path(profile_path) / "ifs-nemo" / f"{profile}.yaml") as f:
            content = yaml.safe_load(f)
            validate_profile(profile, "ifs-nemo", content)
            validate_header(f, dp_version, portfolio, configuration)


def test_profile_generation_portfolio_v1_2_0_ifs_fesom():
    argv = ARGUMENTS_v_1_2_0
    dp_version = argv[3]
    portfolio = argv[5]
    configuration = argv[7]
    profile_path = argv[9]
    generate_profiles(argv)

    # Check IFS-FESOM v1.2.0, portfolio: production, configuration: production
    profiles_ifs_fesom = get_generated_profiles_list(Path(profile_path) / "ifs-fesom")
    expected_profiles_ifs_fesom = [
        "hl_hourly_healpix_high",
        "hl_hourly_healpix_standard",
        "hl_monthly_healpix_standard",
        "o2d_daily_healpix_high",
        "o2d_daily_healpix_standard",
        "o2d_monthly_healpix_high",
        "o2d_monthly_healpix_standard",
        "o3d_2_daily_healpix_high",
        "o3d_2_daily_healpix_standard",
        "o3d_2_monthly_healpix_standard",
        "o3d_3_monthly_healpix_standard",
        "o3d_daily_healpix_high",
        "o3d_daily_healpix_standard",
        "o3d_monthly_healpix_high",
        "o3d_monthly_healpix_standard",
        "pl_hourly_healpix_high",
        "pl_hourly_healpix_standard",
        "pl_monthly_healpix_standard",
        "sfc_daily_healpix_high",
        "sfc_daily_healpix_standard",
        "sfc_hourly_healpix_high",
        "sfc_hourly_healpix_standard",
        "sfc_monthly_healpix_high",
        "sfc_monthly_healpix_standard",
        "sol_2_hourly_healpix_high",
        "sol_2_hourly_healpix_standard",
        "sol_2_monthly_healpix_high",
        "sol_2_monthly_healpix_standard",
        "sol_hourly_healpix_high",
        "sol_hourly_healpix_standard",
        "sol_monthly_healpix_high",
        "sol_monthly_healpix_standard",
    ]
    assert len(profiles_ifs_fesom) == 32
    assert profiles_ifs_fesom == expected_profiles_ifs_fesom

    for profile in profiles_ifs_fesom:
        with open(Path(profile_path) / "ifs-fesom" / f"{profile}.yaml") as f:
            content = yaml.safe_load(f)
            validate_profile(profile, "ifs-fesom", content)
            validate_header(f, dp_version, portfolio, configuration)


def test_profile_generation_portfolio_v1_2_0_icon():
    argv = ARGUMENTS_v_1_2_0
    dp_version = argv[3]
    portfolio = argv[5]
    configuration = argv[7]
    profile_path = argv[9]
    generate_profiles(argv)

    # Check ICON v1.2.0, portfolio: production, configuration: production
    profiles_icon = get_generated_profiles_list(Path(profile_path) / "icon")
    expected_profiles_icon = [
        "hl_hourly_healpix_high",
        "hl_hourly_healpix_standard",
        "hl_monthly_healpix_standard",
        "o2d_daily_healpix_high",
        "o2d_daily_healpix_standard",
        "o2d_monthly_healpix_high",
        "o2d_monthly_healpix_standard",
        "o3d_2_daily_healpix_high",
        "o3d_2_daily_healpix_standard",
        "o3d_2_monthly_healpix_standard",
        "o3d_3_monthly_healpix_standard",
        "o3d_daily_healpix_high",
        "o3d_daily_healpix_standard",
        "o3d_monthly_healpix_high",
        "o3d_monthly_healpix_standard",
        "pl_hourly_healpix_high",
        "pl_hourly_healpix_standard",
        "pl_monthly_healpix_standard",
        "sfc_daily_healpix_high",
        "sfc_daily_healpix_standard",
        "sfc_hourly_healpix_high",
        "sfc_hourly_healpix_standard",
        "sfc_monthly_healpix_high",
        "sfc_monthly_healpix_standard",
        "sol_2_hourly_healpix_high",
        "sol_2_hourly_healpix_standard",
        "sol_2_monthly_healpix_high",
        "sol_2_monthly_healpix_standard",
        "sol_hourly_healpix_high",
        "sol_hourly_healpix_standard",
        "sol_monthly_healpix_high",
        "sol_monthly_healpix_standard",
    ]
    assert len(profiles_icon) == 32
    assert profiles_icon == expected_profiles_icon

    for profile in profiles_icon:
        with open(Path(profile_path) / "icon" / f"{profile}.yaml") as f:
            content = yaml.safe_load(f)
            validate_profile(profile, "icon", content)
            validate_header(f, dp_version, portfolio, configuration)


def test_profile_generation_portfolio_v1_3_0_reduced_ifs_nemo():
    argv = ARGUMENTS_v_1_3_0_REDUCED
    dp_version = argv[3]
    portfolio = argv[5]
    configuration = argv[7]
    profile_path = argv[9]
    generate_profiles(argv)

    # Check IFS-NEMO v1.3.0, portfolio: reduced, configuration: production
    profiles_ifs_nemo = get_generated_profiles_list(Path(profile_path) / "ifs-nemo")
    expected_profiles_ifs_fesom = [
        "hl_hourly_healpix_high",
        "hl_hourly_healpix_standard",
        "o2d_daily_healpix_high",
        "o2d_daily_healpix_standard",
        "o2d_monthly_healpix_high",
        "o2d_monthly_healpix_standard",
        "o3d_monthly_healpix_high",
        "o3d_monthly_healpix_standard",
        "pl_6-hourly_healpix_high",
        "pl_6-hourly_healpix_standard",
        "pl_monthly_healpix_high",
        "pl_monthly_healpix_standard",
        "sfc_daily_healpix_high",
        "sfc_daily_healpix_standard",
        "sfc_hourly_healpix_high",
        "sfc_hourly_healpix_standard",
        "sfc_monthly_healpix_high",
        "sfc_monthly_healpix_standard",
    ]
    assert len(profiles_ifs_nemo) == 18
    assert profiles_ifs_nemo == expected_profiles_ifs_fesom

    for profile in profiles_ifs_nemo:
        with open(Path(profile_path) / "ifs-nemo" / f"{profile}.yaml") as f:
            content = yaml.safe_load(f)
            validate_profile(profile, "ifs-nemo", content)
            validate_header(f, dp_version, portfolio, configuration)



def test_profile_generation_portfolio_v1_3_0_full_ifs_nemo():
    argv = ARGUMENTS_v_1_3_0_FULL
    dp_version = argv[3]
    portfolio = argv[5]
    configuration = argv[7]
    profile_path = argv[9]
    generate_profiles(argv)

    # Check IFS-NEMO v1.2.0, portfolio: production, configuration: production
    profiles_ifs_nemo = get_generated_profiles_list(Path(profile_path) / "ifs-nemo")
    expected_profiles_ifs_nemo = [
        "hl_hourly_healpix_high",
        "hl_hourly_healpix_standard",
        "hl_monthly_healpix_standard",
        "o2d_daily_healpix_high",
        "o2d_daily_healpix_standard",
        "o2d_monthly_healpix_high",
        "o2d_monthly_healpix_standard",
        "o3d_2_monthly_healpix_standard",
        "o3d_daily_healpix_high",
        "o3d_daily_healpix_standard",
        "o3d_monthly_healpix_high",
        "o3d_monthly_healpix_standard",
        "pl_hourly_healpix_high",
        "pl_hourly_healpix_standard",
        "pl_monthly_healpix_standard",
        "sfc_daily_healpix_high",
        "sfc_daily_healpix_standard",
        "sfc_hourly_healpix_high",
        "sfc_hourly_healpix_standard",
        "sfc_monthly_healpix_high",
        "sfc_monthly_healpix_standard",
        "sol_2_hourly_healpix_high",
        "sol_2_hourly_healpix_standard",
        "sol_2_monthly_healpix_high",
        "sol_2_monthly_healpix_standard",
        "sol_hourly_healpix_high",
        "sol_hourly_healpix_standard",
        "sol_monthly_healpix_high",
        "sol_monthly_healpix_standard",
    ]
    assert len(profiles_ifs_nemo) == 29
    assert profiles_ifs_nemo == expected_profiles_ifs_nemo

    for profile in profiles_ifs_nemo:
        with open(Path(profile_path) / "ifs-nemo" / f"{profile}.yaml") as f:
            content = yaml.safe_load(f)
            validate_profile(profile, "ifs-nemo", content)
            validate_header(f, dp_version, portfolio, configuration)


def test_profile_generation_portfolio_v2_0_0_full_ifs_nemo():
    argv = ARGUMENTS_v_2_0_0_FULL
    dp_version = argv[3]
    portfolio = argv[5]
    configuration = argv[7]
    profile_path = argv[9]
    generate_profiles(argv)

    # Check IFS-NEMO v1.2.0, portfolio: production, configuration: production
    profiles_ifs_nemo = get_generated_profiles_list(Path(profile_path) / "ifs-nemo")
    expected_profiles_ifs_nemo = [
        "hl_hourly_healpix_high",
        "hl_hourly_healpix_standard",
        "hl_monthly_healpix_standard",
        "o2d_daily_healpix_high",
        "o2d_daily_healpix_standard",
        "o2d_monthly_healpix_high",
        "o2d_monthly_healpix_standard",
        "o3d_2_monthly_healpix_standard",
        "o3d_daily_healpix_high",
        "o3d_daily_healpix_standard",
        "o3d_monthly_healpix_high",
        "o3d_monthly_healpix_standard",
        "pl_hourly_healpix_high",
        "pl_hourly_healpix_standard",
        "pl_monthly_healpix_standard",
        "sfc_daily_healpix_high",
        "sfc_daily_healpix_standard",
        "sfc_hourly_healpix_high",
        "sfc_hourly_healpix_standard",
        "sfc_monthly_healpix_high",
        "sfc_monthly_healpix_standard",
        "sol_2_hourly_healpix_high",
        "sol_2_hourly_healpix_standard",
        "sol_2_monthly_healpix_high",
        "sol_2_monthly_healpix_standard",
        "sol_hourly_healpix_high",
        "sol_hourly_healpix_standard",
        "sol_monthly_healpix_high",
        "sol_monthly_healpix_standard",
    ]
    assert len(profiles_ifs_nemo) == 29
    assert profiles_ifs_nemo == expected_profiles_ifs_nemo

    for profile in profiles_ifs_nemo:
        with open(Path(profile_path) / "ifs-nemo" / f"{profile}.yaml") as f:
            content = yaml.safe_load(f)
            validate_profile(profile, "ifs-nemo", content)
            validate_header(f, dp_version, portfolio, configuration)
