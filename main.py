from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from astrbot.api import AstrBotConfig
from astrbot.core.config.default import VERSION
from typing import Optional, Any
import aiohttp
import json  # For logging payloads and parsing JSON responses if needed


@register("astrbot_dg_lab_plugin", "RC-CHN", "郊狼API控制插件", "3.1")
class MyPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config
        game_api_config = config.get("game_api", {})
        target_info = config.get("target_info", {})
        self.session = aiohttp.ClientSession(trust_env=True)
        # Game API 配置初始化
        self.base_url = game_api_config.get("base_url", "")
        self.default_client_id = game_api_config.get("default_client_id", "all")
        self.verify_ssl = game_api_config.get("verify_ssl", True)
        # 目标受控者信息
        self.target_user_id = target_info.get("user_id", "未指定")

    async def _request(self, method: str, path: str, **kwargs):
        if not self.base_url:
            return {"error": "API基础URL未配置"}
        target_client_id = self.default_client_id
        if not target_client_id:
            return {"error": "客户端ID未指定且未配置默认值"}
        url = f"{self.base_url.rstrip('/')}/api/v2/game/{target_client_id}{path}"
        logger.debug(f"Calling API: {url} with {kwargs}")

        headers = {
            "Accept": "application/json",
            "Referer": "https://astrbot.app/",
            "User-Agent": f"AstrBot/{VERSION}",
            "UAK": "AstrBot/plugin_dglab",
        }
        if "json" in kwargs:
            headers["Content-Type"] = "application/json"
            logger.debug(f"Payload: {json.dumps(kwargs['json'])}")

        try:
            async with self.session.request(
                method, url, ssl=self.verify_ssl, headers=headers, **kwargs
            ) as response:
                try:
                    res_json = await response.json()
                    logger.debug(
                        f"API response JSON: {json.dumps(res_json, ensure_ascii=False)}"
                    )
                    return res_json
                except Exception:
                    text = await response.text()
                    logger.error(f"非正常JSON响应: {text[:200]}")
                    return {
                        "error": f"非正常JSON响应 (状态码 {response.status}): {text[:200]}",
                        "status_code": response.status,
                    }
        except aiohttp.ClientConnectorError as e:
            logger.error(f"连接错误: {e}")
            return {"error": f"连接到API服务器失败: {e}"}
        except Exception as e:
            logger.error(f"API请求出错: {e}")
            return {"error": str(e)}

    @filter.llm_tool(name="dglab_get_target_info")
    async def dglab_get_target_info(self, event: AstrMessageEvent) -> str:
        """获取当前郊狼插件控制的目标受控人员信息以及可用指令说明。当你想知道你在控制谁，或需要了解有哪些控制能力时，请调用此函数。"""
        help_text = f"当前郊狼设备的佩戴者/受控者是：{self.target_user_id}。\n\n"
        help_text += "作为助手，你可以通过 API 对该受控者进行操作。以下是你可以调用的主要函数说明：\n"
        help_text += "- dglab_get_game_info: 获取受控者的设备状态与最大强度限制（强烈建议操作前调用）。\n"
        help_text += "- dglab_get_strength: 查看当前的基础与随机强度。\n"
        help_text += "- dglab_set_strength: 修改当前的基础与随机强度。\n"
        help_text += "- dglab_get_pulse_list: 查看完整电击波形列表。\n"
        help_text += "- dglab_get_pulse: 查看当前启用的电击波形。\n"
        help_text += "- dglab_set_pulse: 修改电击波形。\n"
        help_text += "- dglab_set_strength: 修改当前的基础与随机强度，这是**基础的使用和控制方式**。\n"
        help_text += "- dglab_action_fire: 对该受控者进行一次性电击（需要给出强度，可附加时间），这是**偏重的惩罚方式**。\n"
        return help_text

    @filter.llm_tool(name="dglab_get_game_info")
    async def dglab_get_game_info(self, event: AstrMessageEvent) -> str:
        """获取郊狼游戏终端的整体信息。包含当前设定的基础和随机强度、波形列表、波形播放模式，以及客户端被限制的最大强度等。建议调整参数或开火前先查询。"""
        res = await self._request("GET", "")
        return json.dumps(res, ensure_ascii=False)

    @filter.llm_tool(name="dglab_get_pulse_list")
    async def dglab_get_pulse_list(self, event: AstrMessageEvent) -> str:
        """获取郊狼所有可用的波形列表及其ID。可以使用这些波形ID来设置当前波形或者进行一键开火。"""
        res = await self._request("GET", "/pulse_list")
        return json.dumps(res, ensure_ascii=False)

    @filter.llm_tool(name="dglab_get_strength")
    async def dglab_get_strength(self, event: AstrMessageEvent) -> str:
        """获取当前的游戏强度配置，包括基础强度(strength)和随机强度(randomStrength)。"""
        res = await self._request("GET", "/strength")
        return json.dumps(res, ensure_ascii=False)

    @filter.llm_tool(name="dglab_set_strength")
    async def dglab_set_strength(
        self,
        event: AstrMessageEvent,
        strength_add: Optional[int] = None,
        strength_sub: Optional[int] = None,
        strength_set: Optional[int] = None,
        random_strength_add: Optional[int] = None,
        random_strength_sub: Optional[int] = None,
        random_strength_set: Optional[int] = None,
    ) -> str:
        """设置或修改郊狼的基础强度与随机强度配置，这是控制郊狼的**基础使用方式**。提供增、减或直接设定的功能。未指定参数则不修改相关属性。

        Args:
            strength_add (number): 可选，增加的基础强度值。
            strength_sub (number): 可选，减少的基础强度值。
            strength_set (number): 可选，直接设置的基础强度值。请避免超过客户端配置的最大限制。
            random_strength_add (number): 可选，增加的随机强度值。
            random_strength_sub (number): 可选，减少的随机强度值。
            random_strength_set (number): 可选，直接设置的随机强度值。
        """
        payload = {}
        if any(x is not None for x in [strength_add, strength_sub, strength_set]):
            payload["strength"] = {}
            if strength_add is not None:
                payload["strength"]["add"] = strength_add
            if strength_sub is not None:
                payload["strength"]["sub"] = strength_sub
            if strength_set is not None:
                payload["strength"]["set"] = strength_set
        if any(
            x is not None
            for x in [random_strength_add, random_strength_sub, random_strength_set]
        ):
            payload["randomStrength"] = {}
            if random_strength_add is not None:
                payload["randomStrength"]["add"] = random_strength_add
            if random_strength_sub is not None:
                payload["randomStrength"]["sub"] = random_strength_sub
            if random_strength_set is not None:
                payload["randomStrength"]["set"] = random_strength_set

        if not payload:
            return "没有提供需要修改的参数配置。"

        res = await self._request("POST", "/strength", json=payload)
        return json.dumps(res, ensure_ascii=False)

    @filter.llm_tool(name="dglab_get_pulse")
    async def dglab_get_pulse(self, event: AstrMessageEvent) -> str:
        """获取当前已启用的波形ID。可能是单个(string)也可能是数组(array)。"""
        res = await self._request("GET", "/pulse")
        return json.dumps(res, ensure_ascii=False)

    @filter.llm_tool(name="dglab_set_pulse")
    async def dglab_set_pulse(self, event: AstrMessageEvent, pulse_id: str) -> str:
        """设置当前郊狼使用的波形ID。

        Args:
            pulse_id (string): 必需，需要设置的波形ID，如果有多个波形ID请使用英文逗号拼接。
        """
        payload = {}
        if "," in pulse_id:
            payload["pulseId"] = [p.strip() for p in pulse_id.split(",") if p.strip()]
        else:
            payload["pulseId"] = pulse_id.strip()

        res = await self._request("POST", "/pulse", json=payload)
        return json.dumps(res, ensure_ascii=False)

    @filter.llm_tool(name="dglab_action_fire")
    async def dglab_action_fire(
        self,
        event: AstrMessageEvent,
        strength: int,
        time: Optional[int] = None,
        override: Optional[bool] = None,
        pulse_id: Optional[str] = None,
    ) -> str:
        """使用郊狼进行一键开火电击，这是对受控者**偏重的惩罚方式**。请保证该开火强度不会超过游戏设置或客户端限制上限。

        Args:
            strength (number): 必需，开火电击强度。建议开火前判断或通过 `dglab_get_game_info` 查询 `clientStrength.limit`，防止强度越界或对用户造成惊吓。
            time (number): 可选，电击时间，单位：毫秒。最高30000（30秒），不传默认为5000。
            override (boolean): 可选，多次一键开火时，是否重置时间 (true为重置, false为叠加)，不传默认为false。
            pulse_id (string): 可选，一键开火期望指定使用的专属波形ID。
        """
        payload: dict[str, Any] = {"strength": strength}
        if time is not None:
            payload["time"] = time
        if override is not None:
            payload["override"] = override
        if pulse_id is not None:
            payload["pulseId"] = pulse_id.strip()

        res = await self._request("POST", "/action/fire", json=payload)
        return json.dumps(res, ensure_ascii=False)

    async def terminate(self):
        """插件被卸载/停用时调用，用于清理资源。"""
        if self.session and not self.session.closed:
            await self.session.close()
            logger.info(f"{self.__class__.__name__}: HTTP session closed.")
