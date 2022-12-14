import yaml

from mmuxer.models.rule import Rule


def test_parse_rule(data):
    rules_yaml = data("models/rules.yaml")
    rules_dicts = yaml.safe_load(rules_yaml)
    for f in rules_dicts:
        r = Rule.parse_obj(f)
        r._actions()
