# -*- coding: UTF-8 -*-
"""
Created on 10.11.22

:author:     Martin Dočekal
"""
from io import StringIO

from ruamel.yaml import YAML as OrigYAML


class YAML(OrigYAML):
    """
    YAML class that allows to dump into string.
    """

    def dumps(self, data, **kw) -> str:
        stream = StringIO()
        YAML.dump(self, data, stream, **kw)
        return stream.getvalue()
