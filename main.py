from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from astrbot.api import AstrBotConfig
import aiohttp
import json # For logging payloads and parsing JSON responses if needed

@register("astrbot_dg_lab_plugin", "RC-CHN", "郊狼API一键开火插件", "0.1")
class MyPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config
        game_api_config = config.get("game_api", {})
        self.session = aiohttp.ClientSession(
            trust_env=True
        )
        # Game API 配置初始化
        self.base_url = game_api_config.get("base_url", "")
        self.default_client_id = game_api_config.get("default_client_id", "all")
        self.verify_ssl = game_api_config.get("verify_ssl", False) # Matches updated schema

    @filter.llm_tool(name="fire_action")
    async def fire_action(
        self,
        event: AstrMessageEvent,
        strength: int,
        time: int = None,
        override: bool = None
    ) -> str:
        '''使用郊狼进行电击，向默认配置的客户端发送一键开火电击指令 (POST /api/v2/game/{clientId}/action/fire)

        Args:
            strength (number): 电击强度，最高40 (必需)。
            time (number): 可选，电击时间，单位：毫秒。API默认为5000，最高30000。
            override (boolean): 可选，多次电击时，是否重置时间 (true为重置, false为叠加)。API默认为false。

        Returns:
            str: API的响应消息或错误信息。
        '''
        target_client_id = self.default_client_id # Always use default_client_id from config
        
        if not self.base_url:
            logger.error("API基础URL未配置 (self.base_url is empty)")
            return "错误：API基础URL未配置。"
        if not target_client_id:
            logger.error("客户端ID未指定且未配置默认值 (target_client_id is empty)")
            return "错误：客户端ID未指定且未配置默认值。"

        api_url = f"{self.base_url.rstrip('/')}/api/v2/game/{target_client_id}/action/fire"
        logger.debug(f"Calling API: {api_url}")

        payload = {"strength": strength}
        if time is not None:
            payload["time"] = time
        if override is not None:
            payload["override"] = override
        
        logger.debug(f"Payload: {json.dumps(payload)}")
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        try:
            async with self.session.post(api_url, json=payload, ssl=self.verify_ssl, headers=headers) as response:
                logger.debug(f"API response status: {response.status}")
                response_text_for_error = "" # Store text for error reporting if JSON parsing fails
                try:
                    response_json = await response.json()
                    logger.debug(f"API response JSON: {json.dumps(response_json)}")
                except (aiohttp.ContentTypeError, json.JSONDecodeError) as json_err:
                    response_text_for_error = await response.text()
                    logger.error(f"Failed to parse API response as JSON: {json_err}. Status: {response.status}. Response text: {response_text_for_error[:500]}")
                    if response.status >= 200 and response.status < 300:
                        return f"操作可能已成功 (状态码 {response.status})，但响应非标准JSON: {response_text_for_error[:200]}"
                    return f"API请求失败 (状态码 {response.status})，响应非标准JSON: {response_text_for_error[:200]}"

                if response.status >= 200 and response.status < 300:
                    success_msg = response_json.get("message", "操作成功完成。")
                    if response_json.get("status") == 1 and response_json.get("code") == "OK":
                        clients_affected = response_json.get("successClientIds")
                        if isinstance(clients_affected, list) and clients_affected:
                            success_msg += f" 成功影响的客户端: {', '.join(map(str, clients_affected))}."
                    return success_msg
                else:
                    error_message = response_json.get("message", f"API返回错误，但未提供详细信息。原始响应: {str(response_json)[:200]}")
                    return f"API请求失败 (状态码 {response.status}): {error_message}"
        except aiohttp.ClientConnectorError as e:
            logger.error(f"连接错误: {e}")
            return f"连接到API服务器失败: {e}"
        except Exception as e:
            logger.exception(f"调用 'fire_action' 工具时发生意外错误: {e}")
            return f"执行开火指令时发生意外错误: {str(e)}"

    async def terminate(self):
        '''插件被卸载/停用时调用，用于清理资源。'''
        if self.session and not self.session.closed:
            await self.session.close()
            logger.info(f"{self.__class__.__name__}: HTTP session closed.")
