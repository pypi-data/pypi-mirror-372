import sys, os 
# 获取t.py 的父目录（即wittiot包路径）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
sys.path.insert(0,  BASE_DIR)  # 添加到模块搜索路径 
 
from wittiot.api  import API  # 改为绝对导入

import json
import logging
#from api import API
from aiohttp import ClientSession
from tabulate import tabulate

def table_print(data: dict) -> str:
    """使用表格格式输出设备数据"""
    # 分组数据
    groups = {
        "气象数据": [],
        "空气质量": [],
        "设备信息": [],
        "电池状态": [],
        "其他传感器": []
    }
    
    # 定义每个组的键
    weather_keys = ["tempinf", "humidityin", "baromrelin", "baromabsin", "tempf", "humidity", 
                  "winddir", "windspeedmph", "windgustmph", "solarradiation", "uv", "daywindmax", 
                  "dewpoint", "rainratein", "eventrainin", "dailyrainin", "weeklyrainin", 
                  "monthlyrainin", "yearlyrainin"]
    
    air_quality_keys = ["pm25_ch1", "pm25_aqi_ch1", "pm25_avg_24h_ch1", "co2", "co2_24h", 
                     "pm25_co2", "pm25_24h_co2", "pm10_co2", "pm10_24h_co2", "pm10_aqi_co2", 
                     "pm25_aqi_co2"]
    
    device_info_keys = ["ver", "devname", "mac"]
    iot_info_keys = ["iot_list"]
    
    battery_keys = [k for k in data.keys() if "_batt" in k]
    
    # 填充组数据
    for key, value in data.items():
        if key in weather_keys:
            groups["气象数据"].append([key, value])
        elif key in air_quality_keys:
            groups["空气质量"].append([key, value])
        elif key in device_info_keys:
            groups["设备信息"].append([key, value])
        elif key in battery_keys:
            groups["电池状态"].append([key, value])
        elif key in iot_info_keys:
            print((value))
        else:
            groups["其他传感器"].append([key, value])
    
    # 创建输出
    output = []
    output.append("==== 设备数据报告 ====")
    output.append(f"设备名称: {data.get('devname', '未知设备')}")
    output.append(f"MAC地址: {data.get('mac', '未知')}")
    output.append(f"固件版本: {data.get('ver', '未知')}\n")
    
    # 添加每个组的表格
    for group, items in groups.items():
        if items:
            output.append(f"◆ {group}")
            output.append(tabulate(items, headers=["参数", "值"], tablefmt="grid"))
            output.append("")
    
    return "\n".join(output)

async def main() -> None:
    async with ClientSession() as session:
        try:
            api = API("192.168.1.114", session=session)
            res = await api._request_loc_allinfo()
            
            # 使用表格格式输出
            print(table_print(res))
            res = await api.switch_iotdevice(1753,1,0)
            print((res))
        except Exception as e:
            logging.error("发生错误: %s", e, exc_info=True)

if __name__ == "__main__":
    # 配置日志记录
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    import asyncio
    asyncio.run(main())