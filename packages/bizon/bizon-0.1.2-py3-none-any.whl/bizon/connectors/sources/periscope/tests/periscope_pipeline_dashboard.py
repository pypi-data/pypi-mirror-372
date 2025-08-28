import os

from bizon.cli.utils import parse_from_yaml
from bizon.engine.engine import RunnerFactory

config = parse_from_yaml(os.path.abspath("bizon/connectors/sources/periscope/config/periscope_dashboards.yml"))

runner = RunnerFactory.create_from_config_dict(config=config)
runner.run()
