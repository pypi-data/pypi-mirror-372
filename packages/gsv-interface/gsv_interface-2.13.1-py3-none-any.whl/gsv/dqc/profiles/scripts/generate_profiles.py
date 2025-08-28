import argparse
from pathlib import Path
import re

from jinja2 import Environment, FileSystemLoader
import yaml


def get_args(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--repo-path", help="Path to the Data Portfolio repository")
    parser.add_argument("-p", "--portfolio", help="Type of Data Portofio utilized (production/reduced)")
    parser.add_argument("-c", "--configuration", help="Experiment configuration (production/develop/lowres)")
    parser.add_argument("-t", "--tag", help="Tag of Data Portfolio repository")
    parser.add_argument("-o", "--output-dir", help="Output directory on profiles will be generated. Also named profile_path throughout the code.", required=False, default=None)
    return parser.parse_args(argv)

def validate_profile_path(profile_path):
    if profile_path is not None:
        # Check it is not empty string
        assert profile_path

def get_default_profile_path(run_resolution):
    GSVROOT = Path(__file__).parents[4]
    profile_path = GSVROOT / "gsv/dqc/profiles"
    if run_resolution.lower() in {"production", "develop", "lowres", "intermediate"}:
        return profile_path /  run_resolution.lower()
    else:
        raise ValueError(f"Invalid output type {run_resolution}")  # TOFIX: Exception not checked

def get_local_grids(run_resolution, grids):
    local_grids = grids["common"]
    local_grids.update(grids[run_resolution])
    return local_grids

def load_template(frequency):
    frequency_to_template = {
        "hourly": "date_time",
        "daily": "date_time",
        "6-hourly": "date_time",
        "monthly": "month_year"
    }
    templates_path = Path(__file__).parents[1] / "templates"
    env = Environment(loader=FileSystemLoader(templates_path), trim_blocks=True, lstrip_blocks=True)
    template = env.get_template(f"{frequency_to_template[frequency]}.jinja")
    return template

def get_time(frequency):
    freq2time = {
        "hourly": '"0000/to/2300/by/0100"',
        "daily": '"0000"',
        "6-hourly": '"0000/to/1800/by/0600"',
        "monthly": None
    }
    return freq2time[frequency]

def get_levelist(profile, local_grids, levels):
    vertical = profile.get("vertical")
    if vertical is None:
        return "None"
    
    return levels[local_grids[f"vertical-{vertical}"]]["levelist"]

def get_profile_content(template, profile, resolution, model, dp_version, local_grids, levels, portfolio, run_resolution):
    grid = local_grids[f"horizontal-{model.upper()}-{resolution}"]
    levelist = get_levelist(profile, local_grids, levels)
    kwargs = {
        "dp_version": dp_version,
        "model": model,
        "resolution": resolution,
        "levtype":  profile["levtype"],
        "levelist": levelist,
        "param": profile["variables"],
        "time": get_time(profile["frequency"]),
        "grid": grid,
        "portfolio": portfolio,
        "run_resolution": run_resolution,
    }
    return template.render(kwargs)

def get_available_resolutions(local_grids, model, omit_resolutions):
    re_pattern = f"horizontal-{model.upper()}-(\w+)"
    resolutions = []

    for key in local_grids:
        match = re.match(re_pattern, key)
        if match and match.group(1) not in omit_resolutions:
            resolutions.append(match.group(1))
    return resolutions

def get_profile_grid_type(content):
    grid_name = re.search(r'grid:\s(\w+)', content).group(1)
    if re.match(r'r\d+x\d+', grid_name):
        return "regular"
    elif re.match(r'H\d+', grid_name):
        return "healpix"
    else:
        raise ValueError(f"Cannot determine grid type for {grid_name}")

def get_profile_filename(model_path, levtype, frequency, grid_type, resolution):
    MAX_SIMILAR_PROFILES = 10

    profile_filename = model_path / f"{levtype}_{frequency}_{grid_type}_{resolution}.yaml"

    if profile_filename.exists():
        for i in range(2, MAX_SIMILAR_PROFILES + 1):
            profile_filename = model_path / f"{levtype}_{i}_{frequency}_{grid_type}_{resolution}.yaml"
            if not profile_filename.exists():
                break
        else:
            raise Exception(
                f"Number of profiles with same levtype, frequency "
                f"and resolution exceeds "
                f"MAX_SIMILAR_PROFILES={MAX_SIMILAR_PROFILES}."
                )

    return profile_filename

def check_and_delete_path(root_path):
    # Check if root_path is empty
    root_path = Path(root_path).resolve()
    files = list(filter(lambda p: p.is_file(), root_path.rglob('*')))

    if not files:
        return True

    extensions = list(map(lambda p: p.suffix, files))
    depths = list(map(lambda p: len(str(p.relative_to(root_path)).split('/')), files))

    # Security checks, to avoid deleting unwanted files
    # Assert almost all files are YAML files
    assert (extensions.count('.yaml') / len(files)) >= 0.8
    # Assert almost all files have depth 2 (relative to root_path)
    assert (depths.count(2) / len(files)) >= 0.95
    # Assert there is no file with depth greater than 2
    assert max(depths) <= 2

    # If all assertions pass, procceed to delete only YAML files.
    profiles = filter(lambda p: p.suffix == '.yaml', files)
    for profile in profiles:
        profile.unlink()

def get_data_portfolio_file(repo_path: Path, portfolio: str) -> Path:
    """
    Return the path for the Data Portfolio file.

    If a `portfolios` directory exists in the root of the repository,
    a 2.0.0 or later version of the Data Portfolio is assumed,
    and the path is constructed accordingly.

    Otherwise, it assumes an older version and returns the path accordingly.

    Args:
        repo_path (Path): Path to the Data Portfolio repository.
        portfolio (str): The type of Data Portfolio (e.g., 'production',
        'reduced' or 'minimal').
    
    Returns:
        Path: Path to the Data Portfolio file.
    """
    if repo_path / "portfolios" in repo_path.iterdir():
        # Assuming Data Portfolio version 2.0.0 or later
        return repo_path / f"portfolios/{portfolio}/portfolio.yaml"
    else:
        # Assuming older version of Data Portfolio
        return repo_path / f"{portfolio}/portfolio.yaml"

def get_grids_file(repo_path: Path, portfolio: str) -> Path:
    """
    Return the path for the grids file.

    If a `portfolios` directory exists in the root of the repository,
    a 2.0.0 or later version of the Data Portfolio is assumed,
    and the path is constructed accordingly.

    Otherwise, it assumes an older version and returns the path accordingly.

    Args:
        repo_path (Path): Path to the Data Portfolio repository.
        portfolio (str): The type of Data Portfolio (e.g., 'production',
        'reduced' or 'minimal').
    
    Returns:
        Path: Path to the grids file.
    """
    if repo_path / "portfolios" in repo_path.iterdir():
        # Assuming Data Portfolio version 2.0.0 or later
        return repo_path / f"portfolios/{portfolio}/grids.yaml"
    else:
        # Assuming older version of Data Portfolio
        return repo_path / f"{portfolio}/grids.yaml"

def generate_profiles(
        dp_repo_path,
        dp_version,
        portfolio,
        run_resolution,
        profile_path=None
    ):
    LOCAL_REPO_PATH = Path(dp_repo_path)

    validate_profile_path(profile_path)

    if profile_path is None:
        profile_path = get_default_profile_path(run_resolution)

    dpfile = get_data_portfolio_file(LOCAL_REPO_PATH, portfolio)
    with open(dpfile, 'r') as f:
        dp = yaml.safe_load(f)

    gridfile = get_grids_file(LOCAL_REPO_PATH, portfolio)
    with open(gridfile, 'r') as f:
        grids = yaml.safe_load(f)
        local_grids = get_local_grids(run_resolution, grids)

    levelsfile = LOCAL_REPO_PATH / "definitions/levels.yaml"
    with open(levelsfile, 'r') as f:
        levels = yaml.safe_load(f)

    # Clean profiles directory
    root_path = Path(profile_path)

    if root_path.exists():
        check_and_delete_path(root_path)

    root_path.mkdir(parents=True, exist_ok=True)

    for model in dp:
        model_path = root_path / model.lower()
        model_path.mkdir(parents=True, exist_ok=True)

        for profile in dp[model]:
            levtype = profile["levtype"]
            frequency = profile["frequency"]
            omit_resolutions = profile.get("omit-resolutions", [])

            # Load template. Frequency dependent
            template = load_template(frequency)

            resolutions = get_available_resolutions(local_grids, model, omit_resolutions)
            for resolution in resolutions:

                content = get_profile_content(
                    template, profile, resolution, model.lower(), dp_version,
                    local_grids, levels, portfolio, run_resolution
                )

                grid_type = get_profile_grid_type(content)

                profile_filename = get_profile_filename(model_path, levtype, frequency, grid_type, resolution)
                
                with open(profile_filename,'w') as output:
                    output.write(content)


def main(argv=None):
    args = get_args(argv)
    dp_repo_path = args.repo_path
    dp_version = args.tag
    portfolio = args.portfolio
    run_resolution = args.configuration
    profile_path = args.output_dir  # Output-dir is renamed profile_path in the code
    generate_profiles(
           dp_repo_path=dp_repo_path,
           dp_version=dp_version,
           portfolio=portfolio,
           run_resolution=run_resolution,
           profile_path=profile_path
           )


if __name__ == '__main__':
    main()
