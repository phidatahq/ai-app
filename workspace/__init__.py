from pathlib import Path
from phidata.utils.env_file import load_env_from_file

load_env_from_file(Path(__file__).parent.joinpath("secrets/api_secrets.yml").resolve())
