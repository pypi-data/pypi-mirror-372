## Wconfig
五八同城配置平台WConfig Python SDK。

### 安装

```bash
pip install wconfig
```

### 使用

```python
from wconfig import BaseConfig, WConfig

class MyConfig(BaseConfig):
    a: str
    b: int

config = WConfig(
    cluster_key="xx",
    cluster_name="xx",
    group_name="xx",
    namespace="xx",
    config_schema=MyConfig,
).get_main_config()

print(config.a)
print(config.b)
```
