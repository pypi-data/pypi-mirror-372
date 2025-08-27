import requests
from typing import Type

from docarray import BaseDoc
from pydantic import BaseModel


class BaseConfig(BaseDoc):
    pass


class WConfig(BaseModel):
    cluster_key: str
    cluster_name: str
    group_name: str = "default_group"
    namespace: str = "default_namespace"
    base_url: str = "https://portal-wconfig.58corp.com"
    config_schema: Type[BaseConfig]

    def get(self, key: str):
        pass

    @property
    def main_url(self):
        return (
            self.base_url
            + "/api/namespace/item/master"
            + f"?clusterKey={self.cluster_key}&clusterName={self.cluster_name}&groupName={self.group_name}&namespaceName={self.namespace}"
        )

    def get_main_config(self):
        res = requests.get(url=self.main_url).json()
        data = res["data"]
        items = {}
        for d in data:
            items[d["itemKey"]] = d["itemValue"]
        return self.config_schema(**items)
