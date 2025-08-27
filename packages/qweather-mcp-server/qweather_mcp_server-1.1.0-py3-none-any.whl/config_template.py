#!/usr/bin/env python3
"""
和风天气API配置模板

请按照以下步骤配置：
1. 登录和风天气开发者控制台 https://console.qweather.com/
2. 获取您的项目ID (Project ID)
3. 获取您的密钥ID (Key ID) 
4. 将下面的配置信息替换为实际值
5. 重命名此文件为 config.py
"""

# 和风天气API配置
QWEATHER_CONFIG = {
    # 从控制台获取的项目ID
    "PROJECT_ID": "YOUR_PROJECT_ID",  # 替换为实际的项目ID
    
    # 从控制台获取的密钥ID  
    "KEY_ID": "YOUR_KEY_ID",  # 替换为实际的密钥ID
    
    # API主机地址 (通常不需要修改)
    "API_HOST": "mx3qqqcp39.re.qweatherapi.com",
    
    # 私钥内容 - 从开发者控制台获取，只需要base64字符串部分
    "PRIVATE_KEY": "YOUR_PRIVATE_KEY"
}