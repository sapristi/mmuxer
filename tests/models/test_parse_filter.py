import yaml

from mail_juicer.models import Filter


def test_parse_filter(data):
    filters_yaml = data("models/filters.yaml")
    filters_dicts = yaml.safe_load(filters_yaml)
    for f in filters_dicts:
        Filter.parse_obj(f)
