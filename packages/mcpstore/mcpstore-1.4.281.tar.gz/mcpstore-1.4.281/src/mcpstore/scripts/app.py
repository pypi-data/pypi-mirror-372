"""
MCPStore API 服务
提供 HTTP API 服务入口
"""

import logging
import os
import time

from fastapi import Request, FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from mcpstore.config.json_config import MCPConfig
from mcpstore.core.orchestrator import MCPOrchestrator
from mcpstore.core.registry import ServiceRegistry
from mcpstore.core.store import MCPStore
from mcpstore.scripts.deps import app_state

from .api import router

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("Initializing MCPStore API service...")

    # 初始化配置（统一使用 SDK 的 setup_store）
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "mcp.json")
    store = MCPStore.setup_store(mcp_config_file=config_path, debug=False)

    # 存储到全局状态
    app_state["store"] = store
    app_state["orchestrator"] = store.orchestrator

    logger.info("MCPStore API service initialized successfully")

    yield  # 应用运行期间

    # 应用关闭时的清理
    logger.info("Shutting down MCPStore API service...")

    try:
        # 清理编排器资源
        await orchestrator.cleanup()
        logger.info("MCPStore API service shutdown completed")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

    try:
        yield
    finally:
        logger.info("Shutting down MCPStore API service...")
        # 清理资源
        orch = app_state.get("orchestrator")
        if orch:
            await orch.stop_global_agent_store()
            await orch.cleanup()
        app_state.clear()
        logger.info("MCPStore API service shutdown complete")

# 创建应用实例
app = FastAPI(
    title="MCPStore API",
    description="MCPStore HTTP API Service",
    version="0.2.0",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(router)

# 注册异常处理
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    error_messages = []
    for error in errors:
        loc = " -> ".join([str(l) for l in error["loc"] if l != "body"])
        msg = error["msg"]
        error_messages.append(f"{loc}: {msg}")

    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "message": "Validation error",
            "data": error_messages
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception in {request.method} {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "data": str(exc)
        }
    )

# 添加请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """记录请求日志"""
    start_time = time.time()

    try:
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000

        # 只记录错误和较慢的请求
        if response.status_code >= 400 or process_time > 1000:
            logger.info(
                f"{request.method} {request.url.path} - "
                f"Status: {response.status_code}, Duration: {process_time:.2f}ms"
            )
        return response
    except Exception as e:
        process_time = (time.time() - start_time) * 1000
        logger.error(
            f"{request.method} {request.url.path} - "
            f"Error: {e}, Duration: {process_time:.2f}ms"
        )
        raise

# 移除了startup和shutdown事件处理器，因为已经使用lifespan
