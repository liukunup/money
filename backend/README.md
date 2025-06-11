# Money

参考 https://github.com/fastapi/full-stack-fastapi-template/

## 目录

```
.
├── Dockerfile
├── README.md
├── app  # 源代码
│   ├── __init__.py
│   ├── config
│   │   ├── config.py
│   │   ├── constant.py
│   │   ├── database.py
│   │   └── response.py
│   ├── dependencies.py
│   ├── internal
│   │   └── __init__.py
│   ├── main.py
│   ├── models
│   │   ├── __init__.py
│   │   └── user.py
│   ├── routers
│   │   ├── __init__.py
│   │   ├── items.py
│   │   ├── system.py
│   │   └── users.py
│   ├── test_main.py
│   └── utils
│       ├── __init__.py
│       ├── auth.py
│       └── email.py
├── pyproject.toml
└── uv.lock
```

## 调试

uv pip install .

uv run fastapi dev