from yaml import safe_load

from bizon.engine.engine import RunnerFactory

config_yaml = """
source:
  name: dummy
  stream: creatures
  authentication:
    type: api_key
    params:
      token: dummy_key

destination:
  name: logger
  config:
    dummy: dummy

engine:
  queue:
    type: kafka
    config:
      queue:
        bootstrap_server: localhost:9092
"""
config = safe_load(config_yaml)
runner = RunnerFactory.create_from_config_dict(config=config)
runner.run()
