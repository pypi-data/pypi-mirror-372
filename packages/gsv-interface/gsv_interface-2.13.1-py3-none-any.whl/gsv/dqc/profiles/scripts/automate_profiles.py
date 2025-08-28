import argparse
from pathlib import Path
import shutil

from git import Repo
import yaml

from generate_profiles import generate_profiles


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
            "-c", "--config",
            help="Configuration file for profile generation",
            required=False,
            default=Path(__file__).parent / "config.yaml"
    )
    return parser.parse_args()


def main():
    args = parse_args()
    config = args.config
    with open(config, 'r') as f:
        config = yaml.safe_load(f)
    
    git_tag = config["git-tag"]
    profile_path = Path(config["profile-path"])

    # Download REPO
    LOCAL_REPO_PATH=Path("/tmp/dprepo")

    if LOCAL_REPO_PATH.exists():
        shutil.rmtree(LOCAL_REPO_PATH)

    Repo.clone_from(
        "https://earth.bsc.es/gitlab/digital-twins/de_340-2/data-portfolio.git",
        LOCAL_REPO_PATH,
        branch=git_tag
    )

    for portfolio in config["portfolios"]:
        portfolio_name = portfolio["name"]
        for configuration in portfolio["configurations"]:
            conf_name = configuration["name"]
            profile_target = profile_path / configuration["profile-target"]
            print(f"Updating profiles for portfolio: <{portfolio_name}> and configuration: <{conf_name}>")
            print(f"Generating profiles in: {profile_target}")
            generate_profiles(LOCAL_REPO_PATH, git_tag, portfolio_name, conf_name, profile_target)
    
    # Clean repo
    shutil.rmtree(LOCAL_REPO_PATH)


if __name__ == '__main__':
    main()
