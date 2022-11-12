import yaml

from mail_juicer.models.filter import parse_filter


def test_parse_filter(data):
    filters_yaml = data("models/filters.yaml")
    filters_dicts = yaml.safe_load(filters_yaml)
    for f in filters_dicts:
        parse_filter(f)
