import yaml
from django.conf import settings

YAML_FILE_BASE_DIR = getattr(settings, 'BASE_DIR')


def get_connector_map():
    """获取所有的连接器"""
    with open(f"{YAML_FILE_BASE_DIR}/connector_map.yaml", 'r', encoding='utf-8') as f:
        connectors = yaml.load(f, Loader=yaml.FullLoader)
        return connectors


connectors = get_connector_map()
