import re
import json

from SOLIDserverRest import *
from SOLIDserverRest import adv as sdsadv


def add_classparams_from_string(sdsobj: sdsadv.ClassParams, meta: str) -> None:
    if not meta or meta == "":
        return

    kvs = re.findall(r'((\w+)=\'([^\']*)\'),?', meta)
    if kvs:
        for g in kvs:
            sjson = f'{{"{g[1]}":"{g[2]}"}}'
            sdsobj.add_class_params(json.loads(sjson))
