# 这里是一个构建包的标准品

1 使用z_init 创建项目
2 在github_disktop上纳入管理

3 src中 提供了log 和 server 的能力

4 uv pip install -e .

5 uv add pytest 

6 uv add anyio pytest-tornasync pytest-asyncio 

5 uv run pytest -s tests/test_main.py::test_get_id_from_name          

uv add fastapi  

uv add uvicorn
