import json

from arkparse.parsing import ArkPropertyContainer
from arkparse.utils.json_utils import DefaultJsonEncoder


class PersistentBuffData:
    class_: str
    name: str

    def __init__(self, properties: ArkPropertyContainer):
        self.class_ = properties.find_property("ForPrimalBuffClass").value.value
        self.name = properties.find_property("ForPrimalBuffClassString").value

    def __str__(self):
        return f"class={self.class_}, name={self.name}"

    def to_json_obj(self):
        return { "ForPrimalBuffClass": self.class_, "ForPrimalBuffClassString": self.name }

    def to_json_str(self):
        return json.dumps(self.to_json_obj(), default=lambda o: o.to_json_obj() if hasattr(o, 'to_json_obj') else None, indent=4, cls=DefaultJsonEncoder)
