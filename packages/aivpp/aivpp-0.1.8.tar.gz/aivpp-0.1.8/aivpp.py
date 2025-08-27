import requests
import os
import pandas as pd
from typing import Literal
from pydantic import BaseModel, Field, field_validator, model_validator
import time

from alibabacloud_brain_industrial20200920.client import Client as brain_industrial20200920Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_brain_industrial20200920 import models as brain_industrial_20200920_models

from alibabacloud_credentials.client import Client as CredClient
from alibabacloud_credentials.models import Config as CreConfig
from alibabacloud_sts20150401.client import Client as StsClient
from alibabacloud_sts20150401.models import AssumeRoleRequest
from alibabacloud_tea_util.models import RuntimeOptions
from mcp.server.fastmcp import FastMCP

# 初始化 FastMCP server
mcp = FastMCP("aivpp")

def create_client() -> brain_industrial20200920Client:
    if 'ROLE_ARN' in os.environ and os.environ['ROLE_ARN']:
        sts_config = open_api_models.Config(
            region_id='cn-hangzhou',
            access_key_id=os.environ['ALIBABA_CLOUD_ACCESS_KEY_ID'],  # RAM用户的AccessKey ID
            access_key_secret=os.environ['ALIBABA_CLOUD_ACCESS_KEY_SECRET']  # RAM用户的AccessKey Secret
        )
        sts_config.endpoint = "sts.aliyuncs.com"  # STS服务的Endpoint
        sts_client = StsClient(sts_config)

        # 调用AssumeRole接口获取STS Token
        assume_role_request = AssumeRoleRequest(
            role_arn=os.environ['ROLE_ARN'],  # 目标RAM角色的ARN
            role_session_name='aivpp_' + os.environ['ROLE_ARN'].split('/')[1] + '_' + str(time.time()),  # 角色会话名称
            duration_seconds=3600  # Token有效期（单位：秒）
        )
        runtime = RuntimeOptions()

        try:
            response = sts_client.assume_role_with_options(assume_role_request, runtime)
            credentials = response.body.credentials  # 获取STS Token信息

            credentials_config = CreConfig(
                type='sts',
                access_key_id=credentials.access_key_id,
                access_key_secret=credentials.access_key_secret,
                security_token=credentials.security_token
            )
            # 使用STS Token初始化凭据客户端
            cred_client = CredClient(credentials_config)

            config = open_api_models.Config(
                region_id='cn-hangzhou',
                credential=cred_client,  # 使用STS Token初始化的凭据客户端
                read_timeout=60000,
                connect_timeout=60000
            )
            return brain_industrial20200920Client(config)
        except Exception as e:
            raise Exception(f"获取STS权限失败：{e}，请检查角色ARN或权限配置")

    """
    使用AK&SK初始化账号Client
    @return: Client
    @throws Exception
    """
    # 工程代码泄露可能会导致 AccessKey 泄露，并威胁账号下所有资源的安全性。以下代码示例仅供参考。
    # 建议使用更安全的 STS 方式，更多鉴权访问方式请参见：https://help.aliyun.com/document_detail/378659.html。
    config = open_api_models.Config(
        # 必填，请确保代码运行环境设置了环境变量 ALIBABA_CLOUD_ACCESS_KEY_ID。,
        access_key_id=os.environ['ALIBABA_CLOUD_ACCESS_KEY_ID'],
        # 必填，请确保代码运行环境设置了环境变量 ALIBABA_CLOUD_ACCESS_KEY_SECRET。,
        access_key_secret=os.environ['ALIBABA_CLOUD_ACCESS_KEY_SECRET']
    )
    # Endpoint 请参考 https://api.aliyun.com/product/brain-industrial
    config.endpoint = f'brain-industrial.cn-hangzhou.aliyuncs.com'
    # 预发cloudservice
    # config.endpoint = f'brain-industrial-vpc.cn-hangzhou.aliyuncs.com'
    return brain_industrial20200920Client(config)

def get_history_data_from_csv(url: str = None, file_path: str = None, time_col: str = "runTime", value_col: str = "value"):
    try:
        if url:
            response = requests.get(url)
            file_name = 'tmp.csv'
            if response.status_code == 200:
                with open(file_name, 'wb') as file:
                    file.write(response.content)
            else:
                raise Exception(f"下载失败，状态码：{response.status_code}")
        elif file_path:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"文件路径不存在：{file_path}")
            file_name = file_path
        else:
            raise Exception("必须提供url或者文件路径")
        ts_df = pd.read_csv(file_name)
        if ts_df.empty:
            raise Exception("csv文件为空，请检查文件内容是否正确")
    except Exception as e:
        raise Exception(f"读取csv文件失败，请确认文件格式是否正确 - {str(e)}")
    if time_col not in ts_df.columns:
        raise Exception(f"csv文件中缺少时间列：{time_col}，请检查列名是否正确")
    if value_col not in ts_df.columns:
        raise Exception(f"csv文件中缺少值列：{value_col}，请检查列名是否正确")
    ts_df['runTime'] = ts_df[time_col]
    ts_df['value'] = ts_df[value_col]
    try:
        ts_df['runTime'] = pd.to_datetime(ts_df['runTime']).dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        raise Exception("时间列格式错误，格式应为%Y-%m-%d %H:%M:%S")
    try:
        ts_df['value'] = ts_df['value'].astype(float)
    except:
        raise Exception("值列类型错误，只允许float格式")
    history_data = ts_df[['runTime', 'value']].to_dict(orient='records')
    return history_data

@mcp.tool(
    name="get_job_result_tool",
    title="查询任务结果",
    description="用于查询指定jobId的算法任务执行结果",
)
def get_job_result(jobId):
    client = create_client()
    get_aivpp_algo_job_request = brain_industrial_20200920_models.GetAivppAlgoJobRequest()
    get_aivpp_algo_job_request.job_id = jobId
    try:
        get_aivpp_algo_job_response = client.get_aivpp_algo_job(get_aivpp_algo_job_request)
    except Exception as e:
        raise Exception(f"调用API失败：获取AIVPP算法任务结果时发生错误 - {str(e)}")
    body = get_aivpp_algo_job_response.body
    if body.data.status == 'SUCCESS':
        result = body.data.response.result
        return result
    elif body.data.status == 'FAIL':
        err_msg = body.data.response.result
        return {"status": "FAIL", "error": err_msg}

class Load_Forecast_Config(BaseModel):
    url: str = Field(default=None, description="历史数据文件 API 地址（可选）")
    file_path: str = Field(default=None, description="本地CSV文件路径（可选）")
    time_col: str = Field(default="runTime", description="时间列（默认值：runTime）")
    value_col: str = Field(default="value", description="值列（默认值：value）")
    device_type: Literal["electricityMeter", "gateway-hvac", "gateway-charging"] = Field(
        default="electricityMeter",
        description="设备类型（枚举值：electricityMeter/gateway-hvac/gateway-charging）"
    )
    system_type: Literal["load", "hvac", "flexible", "charge"] = Field(
        default="load",
        description="系统类型（枚举值：load/hvac/flexible/charge）"
    )
    run_date: str = Field(default=None, description="执行日期（格式：YYYY-MM-DD, 必填）")
    duration: int = Field(default=1, description="持续时间（默认值：1）")
    freq: Literal["FIFTEEN_MIN", "FIVE_MIN", "ONE_HOUR", "ONE_DAY"] = Field(
        default="FIFTEEN_MIN",
        description="频率（枚举值：FIFTEEN_MIN/FIVE_MIN/ONE_HOUR/ONE_DAY）"
    )
    timezone: str = Field(default="Asia/Shanghai", description="时区（默认值：Asia/Shanghai）")
    model_version: str = Field(default="latest", description="模型版本（默认值：latest）")

    @model_validator(mode='after')
    def check_url_or_file_path(self):
        if not self.url and not self.file_path:
            raise ValueError("必须提供 url 或 文件路径")
        if self.url and self.file_path:
            raise ValueError("url 和 文件路径 不能同时提供")
        return self

    @field_validator('run_date')
    def check_run_date(cls, v):
        try:
            pd.to_datetime(v)
        except Exception:
            raise ValueError("run_date 必须是 YYYY-MM-DD 格式")
        return v

@mcp.tool(
    name="load_forecast_tool",
    title="负荷预测工具",
    description="""
                根据历史数据执行负荷预测，适用于市电电表、空调、照明电表、充电桩等设备。
                支持多种时间粒度和模型版本选择，可指定预测持续时间及时区。
                """
)
def load_forecast(config: Load_Forecast_Config):
    client = create_client()
    create_load_forecast_job_request = brain_industrial_20200920_models.CreateLoadForecastJobRequest()
    history_data = get_history_data_from_csv(
        url=config.url,
        file_path=config.file_path,
        time_col=config.time_col,
        value_col=config.value_col
    )
    history_data_req = []
    for item in history_data:
        historyDataItem = brain_industrial_20200920_models.CreateLoadForecastJobRequestHistoryData()
        historyDataItem.run_time = item['runTime']
        historyDataItem.value = item['value']
        history_data_req.append(historyDataItem)
    create_load_forecast_job_request.history_data = history_data_req
    create_load_forecast_job_request.system_type = config.system_type
    create_load_forecast_job_request.run_date = config.run_date
    create_load_forecast_job_request.duration = config.duration
    create_load_forecast_job_request.freq = config.freq
    create_load_forecast_job_request.timezone = config.timezone
    create_load_forecast_job_request.model_version = config.model_version
    try:
        result = client.create_load_forecast_job(create_load_forecast_job_request)
        return result
    except Exception as e:
        return {"API调用失败": str(e)}

class New_Eng_Config(BaseModel):
    url: str = Field(default=None, description="历史数据文件 API 地址（可选）")
    file_path: str = Field(default=None, description="本地CSV文件路径（可选）")
    time_col: str = Field(default="runTime", description="时间列（默认值：runTime）")
    value_col: str = Field(default="value", description="值列（默认值：value）")
    device_type: str = Field(default="solarInverter", description="设备类型（默认值：solarInverter）")
    system_type: str = Field(default="solar", description="系统类型（默认值：solar）")
    run_date: str = Field(default=None, description="执行日期（格式：YYYY-MM-DD, 必填）")
    duration: int = Field(default=1, description="持续时间（默认值：1）")
    freq: Literal["FIFTEEN_MIN", "FIVE_MIN", "ONE_HOUR", "ONE_DAY"] = Field(
        default="FIFTEEN_MIN",
        description="频率（枚举值：FIFTEEN_MIN/FIVE_MIN/ONE_HOUR/ONE_DAY）"
    )
    timezone: str = Field(default="Asia/Shanghai", description="时区（默认值：Asia/Shanghai）")
    model_version: str = Field(default="latest", description="模型版本（默认值：latest）")
    longitude: float = Field(default=None, description="经度（必填）")
    latitude: float = Field(default=None, description="纬度（必填）")
    altitude: float = Field(default=10, description="海拔（默认值：10）")

    @model_validator(mode='after')
    def check_url_or_file_path(self):
        if not self.url and not self.file_path:
            raise ValueError("必须提供 url 或 文件路径")
        if self.url and self.file_path:
            raise ValueError("url 和 文件路径 不能同时提供")
        return self

    @field_validator('run_date')
    def check_run_date(cls, v):
        try:
            pd.to_datetime(v)
        except Exception:
            raise ValueError("run_date 必须是 YYYY-MM-DD 格式")
        return v

    @field_validator('longitude')
    def check_longitude(cls, v):
        if not v:
            raise ValueError("经度不能为空")
        return v

    @field_validator('latitude')
    def check_latitude(cls, v):
        if not v:
            raise ValueError("纬度不能为空")
        return v

@mcp.tool(
    name="power_forecast_tool",
    title="功率预测工具",
    description="""
                根据历史数据和地理位置信息执行功率预测，适用于光伏能源系统。
                支持多种时间粒度和模型版本选择，可指定预测持续时间及时区。
                """,
)
def power_forecast(config: New_Eng_Config):
    client = create_client()
    create_power_forecast_job_request = brain_industrial_20200920_models.CreatePowerForecastJobRequest()
    history_data = get_history_data_from_csv(
        url=config.url,
        file_path=config.file_path,
        time_col=config.time_col,
        value_col=config.value_col
    )
    history_data_req = []
    for item in history_data:
        historyDataItem = brain_industrial_20200920_models.CreatePowerForecastJobRequestHistoryData()
        historyDataItem.run_time = item['runTime']
        historyDataItem.value = item['value']
        history_data_req.append(historyDataItem)
    create_power_forecast_job_request.history_data = history_data_req
    create_power_forecast_job_request.system_type = config.system_type
    create_power_forecast_job_request.device_type = config.device_type
    create_power_forecast_job_request.run_date = config.run_date
    create_power_forecast_job_request.duration = config.duration
    create_power_forecast_job_request.freq = config.freq
    create_power_forecast_job_request.timezone = config.timezone
    location_req = brain_industrial_20200920_models.CreatePowerForecastJobRequestLocation()
    location_req.latitude = config.latitude
    location_req.longitude = config.longitude
    location_req.altitude = config.altitude
    create_power_forecast_job_request.location = location_req
    create_power_forecast_job_request.time_zone = config.timezone
    try:
        result = client.create_power_forecast_job(create_power_forecast_job_request)
        return result
    except Exception as error:
        return {"API调用失败": str(error)}
def main():
    print("Server Running")
    # 初始化并运行 server
    mcp.run(transport='stdio')
    
if __name__ == "__main__":
   main()


