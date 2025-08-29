'''
Author: 823042332@qq.com 823042332@qq.com
Date: 2025-08-29 14:39:16
LastEditors: 823042332@qq.com 823042332@qq.com
LastEditTime: 2025-08-29 15:23:21
FilePath: /standard_packages/src/standard_packages/server.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''

from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, model_validator



# TODO ADD
app = FastAPI(
    title="LLM Service",
    description="Provides an OpenAI-compatible API for custom large language models.",
    version="1.0.1",
)

# --- Configure CORS ---
# ! Add this section !
# Define allowed origins. Be specific in production!
# Example: origins = ["http://localhost:3000", "https://your-frontend-domain.com"]
origins = [
    "*", # Allows all origins (convenient for development, insecure for production)
    # Add the specific origin of your "别的调度" tool/frontend if known
    # e.g., "http://localhost:5173" for a typical Vite frontend dev server
    # e.g., "http://127.0.0.1:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Specifies the allowed origins
    allow_credentials=True, # Allows cookies/authorization headers
    allow_methods=["*"],    # Allows all methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],    # Allows all headers (Content-Type, Authorization, etc.)
)
# --- End CORS Configuration ---




@app.get("/")
async def root():
    """ x """
    return {"message": "LLM Service is running."}



if __name__ == "__main__":
    # 这是一个标准的 Python 入口点惯用法
    # 当脚本直接运行时 (__name__ == "__main__")，这里的代码会被执行
    # 当通过 python -m YourPackageName 执行 __main__.py 时，__name__ 也是 "__main__"
    import argparse
    import uvicorn
    from .log import Log
    
    
    default=8008
    

    parser = argparse.ArgumentParser(
        description="Start a simple HTTP server similar to http.server."
    )
    parser.add_argument(
        'port',
        metavar='PORT',
        type=int,
        nargs='?', # 端口是可选的
        default=default,
        help='Specify alternate port [default: 8000]'
    )
    # 创建一个互斥组用于环境选择
    group = parser.add_mutually_exclusive_group()

    # 添加 --dev 选项
    group.add_argument(
        '--dev',
        action='store_true', # 当存在 --dev 时，该值为 True
        help='Run in development mode (default).'
    )

    # 添加 --prod 选项
    group.add_argument(
        '--prod',
        action='store_true', # 当存在 --prod 时，该值为 True
        help='Run in production mode.'
    )
    args = parser.parse_args()

    if args.prod:
        env = "prod"
    else:
        # 如果 --prod 不存在，默认就是 dev
        env = "dev"

    port = args.port
    if env == "dev":
        port += 100
        Log.reset_level('debug',env = env)
        reload = True
        # app_import_string = "src.clientz.server:app" # <--- 关键修改：传递导入字符串
        app_import_string = f"{__package__}.server:app" # <--- 关键修改：传递导入字符串
    elif env == "prod":
        Log.reset_level('info',env = env)# ['debug', 'info', 'warning', 'error', 'critical']
        reload = False
        app_import_string = app
    else:
        reload = False
        app_import_string = app
    

    # 使用 uvicorn.run() 来启动服务器
    # 参数对应于命令行选项
    uvicorn.run(
        app_import_string,
        host="0.0.0.0",
        port=port,
        reload=reload  # 启用热重载
    )
