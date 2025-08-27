#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LiblibAI 通用图片生成工具
基于LiblibAI API的AI图片生成服务，支持各种风格的图片创作
"""

import json
import hmac
import hashlib
import time
import random
import string
import requests
import base64
import sys
import os
import logging
from datetime import datetime

# 设置UTF-8编码
if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from mcp.server.fastmcp import FastMCP
    
    # API密钥配置
    ACCESS_KEY = os.getenv("LIBLIB_ACCESS_KEY", "your-access-key")
    SECRET_KEY = os.getenv("LIBLIB_SECRET_KEY", "your-secret-key")
    BASE_URL = "https://openapi.liblibai.cloud"
    
    # 创建MCP服务器
    mcp = FastMCP("LiblibAI-Picture-Generator")
    
    # 延迟导入变量
    _modules_loaded = False
    _requests = None
    _hmac = None
    _hashlib = None
    _time = None
    _random = None
    _string = None
    _base64 = None
    
    def _load_modules():
        """延迟加载模块"""
        global _modules_loaded, _requests, _hmac, _hashlib, _time, _random, _string, _base64
        if not _modules_loaded:
            import requests as req_mod
            import hmac as hmac_mod
            import hashlib as hash_mod
            import time as time_mod
            import random as rand_mod
            import string as str_mod
            import base64 as b64_mod
            _requests = req_mod
            _hmac = hmac_mod
            _hashlib = hash_mod
            _time = time_mod
            _random = rand_mod
            _string = str_mod
            _base64 = b64_mod
            _modules_loaded = True
    
    def _make_api_request(endpoint: str, data: dict) -> dict:
        """发送API请求"""
        try:
            _load_modules()
            
            timestamp = str(int(_time.time() * 1000))
            nonce = ''.join(_random.choices(_string.ascii_letters + _string.digits, k=16))
            
            # 生成签名
            sign_string = f"{endpoint}&{timestamp}&{nonce}"
            signature = _base64.urlsafe_b64encode(_hmac.new(
                SECRET_KEY.encode('utf-8'),
                sign_string.encode('utf-8'),
                _hashlib.sha1
            ).digest()).decode().rstrip('=')
            
            # 请求参数
            params = {
                'AccessKey': ACCESS_KEY,
                'Signature': signature,
                'Timestamp': timestamp,
                'SignatureNonce': nonce
            }
            
            headers = {'Content-Type': 'application/json'}
            url = f"{BASE_URL}{endpoint}"
            
            response = _requests.post(url, json=data, headers=headers, params=params, timeout=15)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}: {response.text}"}
                
        except Exception as e:
            return {"error": f"请求异常: {str(e)}"}
    
    @mcp.tool()
    def create_image(prompt: str, width: int = 768, height: int = 768) -> str:
        """
        生成AI图片
        
        Args:
            prompt: 图片描述（必须提供）
            width: 图片宽度，默认768像素
            height: 图片高度，默认768像素
        
        Returns:
            str: 生成结果和任务ID
        """
        if not prompt or not prompt.strip():
            return "[ERROR] 请提供图片描述"
        
        if not (256 <= width <= 2048) or not (256 <= height <= 2048):
            return "[ERROR] 图片尺寸必须在256-2048像素之间"
        
        # API请求数据
        data = {
            "templateUuid": "6f7c4652458d4802969f8d089cf5b91f",
            "generateParams": {
                "prompt": prompt,
                "steps": 25,
                "width": width,
                "height": height,
                "imgCount": 1,
                "seed": -1,
                "restoreFaces": 0
            }
        }
        
        result = _make_api_request("/api/generate/webui/text2img", data)
        
        if "error" in result:
            return f"[FAILED] {result['error']}"
        
        if result.get("code") == 0 and "data" in result:
            task_id = result["data"]["generateUuid"]
            return f"[SUCCESS] 图片生成任务已提交！\n📋 任务ID: {task_id}\n💡 使用 check_image_status('{task_id}') 查询生成结果"
        else:
            return f"[ERROR] API响应异常: {result}"
    
    @mcp.tool()
    def check_image_status(task_id: str) -> str:
        """
        查询图片生成状态
        
        Args:
            task_id: 任务ID
            
        Returns:
            str: 生成状态和结果
        """
        if not task_id:
            return "[ERROR] 任务ID不能为空"
        
        data = {"generateUuid": task_id}
        result = _make_api_request("/api/generate/webui/status", data)
        
        if "error" in result:
            return f"[FAILED] 查询失败: {result['error']}"
        
        if result.get("code") == 0 and "data" in result:
            data = result["data"]
            percent = data.get("percentCompleted", 0)
            status = data.get("generateStatus", 0)
            
            if percent >= 1.0 and "images" in data and data["images"]:
                images = data["images"]
                if images and "imageUrl" in images[0]:
                    image_url = images[0]["imageUrl"]
                    seed = images[0].get("seed", "未知")
                    cost = data.get("pointsCost", 0)
                    balance = data.get("accountBalance", 0)
                    
                    return f"[SUCCESS] 图片生成完成！\n🖼️ 图片地址: {image_url}\n🎲 随机种子: {seed}\n💰 消耗积分: {cost}\n💳 剩余积分: {balance}"
            elif percent < 1.0:
                return f"[PROCESSING] 图片生成中... ({percent*100:.0f}% 完成)"
            else:
                return f"[WARNING] 生成状态异常: {status}"
        else:
            return f"[ERROR] API响应异常: {result}"
    
    @mcp.tool()
    def generate_and_wait(prompt: str, width: int = 768, height: int = 768, max_wait: int = 120) -> str:
        """
        生成图片并等待完成（一站式服务）
        
        Args:
            prompt: 图片描述（必须提供）
            width: 图片宽度
            height: 图片高度
            max_wait: 最大等待时间（秒）
            
        Returns:
            str: 最终生成结果
        """
        # 提交生成任务
        result = create_image(prompt, width, height)
        
        if not result.startswith("[SUCCESS]"):
            return result
        
        # 提取任务ID
        try:
            task_id = result.split("任务ID: ")[1].split("\n")[0]
        except:
            return "[ERROR] 无法提取任务ID"
        
        # 等待生成完成
        _load_modules()
        start_time = _time.time()
        
        while _time.time() - start_time < max_wait:
            status_result = check_image_status(task_id)
            
            if status_result.startswith("[SUCCESS]"):
                return status_result
            elif status_result.startswith("[FAILED]") or status_result.startswith("[ERROR]"):
                return status_result
            
            # 等待10秒后再次查询
            _time.sleep(10)
        
        return f"[TIMEOUT] 等待超时，请使用 check_image_status('{task_id}') 手动查询"
    
    @mcp.tool()
    def health_check() -> str:
        """健康检查"""
        return f"[OK] LiblibAI Picture Generator 运行正常 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    def main():
        """启动MCP服务器"""
        logger.info("🚀 启动 LiblibAI Picture Generator...")
        logger.info("📋 版本: 1.0.0")
        logger.info("🛠️ 支持功能: 图片生成、状态查询、一站式服务")
        
        # 检查API密钥配置
        if ACCESS_KEY == "your-access-key" or SECRET_KEY == "your-secret-key":
            logger.warning("⚠️ 请设置环境变量 LIBLIB_ACCESS_KEY 和 LIBLIB_SECRET_KEY")
            logger.info("💡 使用方法：")
            logger.info("   export LIBLIB_ACCESS_KEY='your-access-key'")
            logger.info("   export LIBLIB_SECRET_KEY='your-secret-key'")
        else:
            logger.info(f"✅ API配置已加载 (AccessKey: {ACCESS_KEY[:10]}...)")
        
        try:
            mcp.run()
        except KeyboardInterrupt:
            logger.info("👋 服务已停止")
        except Exception as e:
            logger.error(f"❌ 启动失败: {e}")
            sys.exit(1)

except ImportError as e:
    print(f"❌ 缺少依赖包: {e}")
    print("💡 请安装依赖: pip install mcp fastmcp requests")
    sys.exit(1)
except Exception as e:
    print(f"❌ 启动错误: {e}")
    sys.exit(1)

if __name__ == "__main__":
    main()