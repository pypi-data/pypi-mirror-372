import os
import yaml
from box import Box

from config.settings import ROOT_DIR


class YamlUtil(object):
    def __init__(self, file_path):
        self.file_path = file_path

    def load_yml(self, key=None, is_box=False):
        """

        @param key:
        @param is_box:
        @return:
        """
        with open(os.path.join(ROOT_DIR, self.file_path), mode="r", encoding="utf-8") as f:
            result = yaml.safe_load(stream=f) or dict()
            if key:
                result = result.get(key)
            if is_box:
                result = Box(result) if isinstance(result, dict) else result
            return result
