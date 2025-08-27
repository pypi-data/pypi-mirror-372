#!/usr/bin/env python3
import asyncio
import json
import logging
import os
from typing import Any, Dict, Optional
import httpx
import jwt
from datetime import datetime, timezone, timedelta
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QWeatherClient:
    def __init__(self):
        # 优先从环境变量加载配置
        self.project_id = os.getenv("QWEATHER_PROJECT_ID")
        self.key_id = os.getenv("QWEATHER_KEY_ID")
        self.api_host = os.getenv("QWEATHER_API_HOST")
        private_key_raw = os.getenv("QWEATHER_PRIVATE_KEY")
        
        # 如果环境变量存在，使用环境变量配置
        if all([self.project_id, self.key_id, self.api_host, private_key_raw]):
            # 构建完整的PEM格式私钥
            self.private_key = f"""-----BEGIN PRIVATE KEY-----
{private_key_raw}
-----END PRIVATE KEY-----"""
            logger.info("成功加载环境变量配置")
        else:
            # 尝试从config.py加载配置
            try:
                from config import QWEATHER_CONFIG
                self.api_host = self.api_host or QWEATHER_CONFIG["API_HOST"]
                self.project_id = self.project_id or QWEATHER_CONFIG["PROJECT_ID"]
                self.key_id = self.key_id or QWEATHER_CONFIG["KEY_ID"]
                private_key_raw = private_key_raw or QWEATHER_CONFIG["PRIVATE_KEY"]
                
                # 构建完整的PEM格式私钥
                self.private_key = f"""-----BEGIN PRIVATE KEY-----
{private_key_raw}
-----END PRIVATE KEY-----"""
                logger.info("成功加载config.py配置文件")
            except ImportError:
                logger.error("未找到配置！请配置环境变量或创建config.py文件")
                raise Exception("缺少必要的API配置，请设置环境变量或创建config.py")
            except Exception as e:
                logger.error(f"加载配置失败: {e}")
                raise
        
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                'User-Agent': 'MCP-Weather-Server/1.0',
                'Accept': 'application/json',
                'Accept-Encoding': 'gzip'
            }
        )
    
    def _generate_jwt_token(self) -> str:
        """按照官方示例生成JWT令牌"""
        import time
        
        # 按照官方示例的payload格式
        payload = {
            'iat': int(time.time()) - 30,  # 当前时间减30秒
            'exp': int(time.time()) + 900,  # 当前时间加15分钟
            'sub': self.project_id  # 项目ID
        }
        
        # 按照官方示例的headers格式
        headers = {
            'kid': self.key_id  # 密钥ID
        }
        
        try:
            token = jwt.encode(payload, self.private_key, algorithm='EdDSA', headers=headers)
            logger.info(f"按照官方格式生成JWT token: {token[:50]}...")
            logger.info(f"Payload: {payload}")
            logger.info(f"Headers: {headers}")
            return token
        except Exception as e:
            logger.error(f"生成JWT token失败: {e}")
            logger.error("请检查project_id和key_id是否正确配置")
            raise e
    
    async def get_city_location(self, city: str) -> Optional[Dict[str, Any]]:
        """根据城市名获取城市位置信息"""
        try:
            token = self._generate_jwt_token()
            
            # 完全按照示例格式构建请求
            url = f"https://{self.api_host}/geo/v2/city/lookup"
            headers = {
                'Authorization': f'Bearer {token}',
                'Accept': 'application/json',
                'Accept-Encoding': 'gzip, deflate'
            }
            params = {'location': city}
            
            logger.info(f"城市查询请求: {url}?location={city}")
            logger.info(f"请求头: Authorization: Bearer {token[:20]}...")
            
            response = await self.client.get(url, headers=headers, params=params)
            
            logger.info(f"响应状态码: {response.status_code}")
            logger.info(f"响应头: {dict(response.headers)}")
            
            if response.status_code != 200:
                logger.error(f"API调用失败: HTTP {response.status_code}")
                logger.error(f"响应内容: {response.text}")
                return None
            
            data = response.json()
            logger.info(f"API响应: {data}")
            
            if data.get('code') == '200' and data.get('location'):
                location = data['location'][0]
                logger.info(f"找到城市: {location.get('name')} (ID: {location.get('id')})")
                return location
            else:
                logger.warning(f"城市查询失败: code={data.get('code')}, 城市={city}")
                return None
                
        except Exception as e:
            logger.error(f"城市位置查询异常: {e}")
            return None
    
    async def get_weather(self, city: str) -> Dict[str, Any]:
        """获取指定城市的天气信息"""
        try:
            # 首先获取城市位置信息
            location = await self.get_city_location(city)
            
            if not location:
                return {"error": "无效的城市名，请输入中国境内城市"}
            
            location_id = location.get('id')
            if not location_id:
                logger.error(f"未获取到城市ID: {city}")
                return {"error": "无效的城市名，请输入中国境内城市"}
            
            # 获取天气信息
            token = self._generate_jwt_token()
            headers = {
                'Authorization': f'Bearer {token}',
                'Accept': 'application/json',
                'Accept-Encoding': 'gzip, deflate'
            }
            
            url = f"https://{self.api_host}/v7/weather/now"
            params = {'location': location_id}
            
            logger.info(f"天气查询请求: {url}?location={location_id}")
            logger.info(f"请求头: Authorization: Bearer {token[:20]}...")
            
            response = await self.client.get(url, headers=headers, params=params)
            
            logger.info(f"天气API响应状态码: {response.status_code}")
            if response.status_code != 200:
                logger.error(f"天气API调用失败: HTTP {response.status_code}")
                logger.error(f"响应内容: {response.text}")
                return {"error": "获取天气信息失败，请稍后重试"}
            
            data = response.json()
            logger.info(f"天气API响应: {data}")
            
            if data.get('code') == '200' and data.get('now'):
                weather_now = data.get('now', {})
                
                # 构建统一的天气响应格式
                weather_response = {
                    "city": location.get('name', city),
                    "adm1": location.get('adm1', ''),
                    "adm2": location.get('adm2', ''),
                    "temperature": f"{weather_now.get('temp', 'N/A')}°C",
                    "feels_like": f"{weather_now.get('feelsLike', 'N/A')}°C",
                    "weather": weather_now.get('text', 'N/A'),
                    "wind_direction": weather_now.get('windDir', 'N/A'),
                    "wind_speed": f"{weather_now.get('windSpeed', 'N/A')} km/h",
                    "humidity": f"{weather_now.get('humidity', 'N/A')}%",
                    "pressure": f"{weather_now.get('pressure', 'N/A')} hPa",
                    "visibility": f"{weather_now.get('vis', 'N/A')} km",
                    "cloud_cover": f"{weather_now.get('cloud', 'N/A')}%",
                    "update_time": weather_now.get('obsTime', 'N/A')
                }
                
                logger.info(f"天气查询成功: {city} -> {weather_response}")
                return weather_response
            else:
                error_msg = f"天气API返回错误: code={data.get('code')}"
                logger.error(error_msg)
                return {"error": "获取天气信息失败，请稍后重试"}
                
        except Exception as e:
            logger.error(f"获取天气信息异常: {e}")
            return {"error": "获取天气信息失败，请稍后重试"}
    
    async def close(self):
        """关闭HTTP客户端"""
        await self.client.aclose()

weather_client = QWeatherClient()
app = Server("weather_server")

@app.list_tools()
async def list_tools() -> list[Tool]:
    """列出可用的工具"""
    logger.info("收到工具列表请求")
    tools = [
        Tool(
            name="get_weather",
            description="获取中国指定城市的实时天气信息",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "中国的城市名，例如：北京、上海、广州"
                    }
                },
                "required": ["city"]
            }
        )
    ]
    logger.info(f"返回 {len(tools)} 个工具")
    return tools

@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> list[TextContent]:
    """处理工具调用"""
    logger.info(f"收到工具调用: {name}, 参数: {arguments}")
    
    if name != "get_weather":
        error_msg = f"未知工具: {name}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    city = arguments.get("city")
    if not city:
        error_response = {"error": "缺少必需参数: city"}
        logger.error(f"参数错误: {error_response}")
        return [TextContent(
            type="text",
            text=json.dumps(error_response, ensure_ascii=False, indent=2)
        )]
    
    logger.info(f"查询城市天气: {city}")
    weather_info = await weather_client.get_weather(city)
    logger.info(f"天气查询结果: {weather_info}")
    
    return [TextContent(
        type="text",
        text=json.dumps(weather_info, ensure_ascii=False, indent=2)
    )]

async def main():
    """主函数"""
    try:
        async with stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options()
            )
    except KeyboardInterrupt:
        logger.info("服务器已停止")
    finally:
        await weather_client.close()

if __name__ == "__main__":
    asyncio.run(main())