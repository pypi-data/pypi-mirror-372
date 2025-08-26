# Intellif ArcternWeb SDK

**Intellif ArcternWeb** 官方 Python 开发包。
一个 `Client` 对象即可完成推理任务、模型组查询等常见操作，无需手写 HTTP 请求。

```
arcternweb_sdk/
├─ pyproject.toml
├─ requirements.txt
├─ src/arcternweb/
│   ├─ client.py
│   ├─ exceptions.py
│   ├─ models/…
│   ├─ services/…
│   └─ utils/…
└─ tests/
```

---

## 💻 安装

```bash
# PyPI 安装
pip install intellif-arcternweb
# 运行环境：Python ≥ 3.9
```

---

## 🚀 快速上手

```python
import json
from pathlib import Path
from arcternweb import Client

BASE  = "http://192.168.99.63:30026"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJYLXVpZCI6MTQ3LCJleHAiOjIzODYzMDgxOTgsImlhdCI6MTc1NTU4ODE5OH0.ZRnHmTmbwvxdrvhX4qZfPqSCafvNf3I-JduQ7EEBHnI"   # 或设置环境变量：export ARCTERNWEB_TOKEN=...

client = Client(base_url=BASE_URL, token=TOKEN)
# arcternweb 上的测试 ID
infer_task_id = 13447
try:
    infer_task_info = client.infer_task_server.get(infer_task_id)
    print(infer_task_info)

    # 此处的 bin_name 将作为后续的模型名字使用
    bin_name = Path(infer_task_info.result_path).stem
    print("bin_name: ", bin_name)
except Exception as e:
    print(f"infer_task_server error: {e}")
```

---

## 🌍 环境变量

| 变量                       | 作用                                      | 默认值                           |
|----------------------------|-------------------------------------------|----------------------------------|
| `ARCTERNWEB_TOKEN`             | API 鉴权 Token（可不在 `Client` 中显式传入） | –                                |

---

## 📦 打包 & 发布

项目采用 PEP 517 / `pyproject.toml` 构建规范。

```bash
# 1️⃣ 构建 wheel / sdist
python3 -m pip install --upgrade build
python3 -m build                 # 生成 dist/*.whl dist/*.tar.gz

# 2️⃣ 本地验证
pip3 install --force-reinstall dist/*.whl
python3 -c "import arcternweb, sys; print('SDK 版本:', arcternweb.__version__)"

# 3️⃣ 发布到 PyPI 或私有仓库
python3 -m pip install --upgrade twine
twine upload dist/*
```

---