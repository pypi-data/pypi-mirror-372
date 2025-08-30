from json import loads
from typing import Union, Literal, Optional

import httpx

from ..compat import model_dump

# from ..function_call import registry
from ..log import ds_logger, tts_logger
from ..exception import RequestException
from ..config import ds_config, tts_config, json_config, uninfo_enable
from ..schemas import Balance, TTSModelInfo, ChatCompletions, StreamChoiceList


class API:
    _headers = {
        "Accept": "application/json",
    }

    @classmethod
    async def chat(cls, message: list[dict[str, str]], model: str = "deepseek-chat") -> ChatCompletions:
        """普通对话"""
        model_config = ds_config.get_model_config(model)

        api_key = model_config.api_key or ds_config.api_key
        prompt: str = model_dump(model_config, exclude_none=True).get("prompt", ds_config.prompt)
        if uninfo_enable:
            if json_config.prompt_func is None:
                json_config.set_prompt_func(prompt)
            else:
                prompt = await json_config.get_prompt()
        proxy = model_config.proxy

        json = {
            "messages": ([{"content": prompt, "role": "system"}] + message if prompt else message),
            "model": model,
            **model_config.to_dict(),
        }
        ds_logger(
            "DEBUG", f"使用模型 {f'{model} ({model_config.alias})' if model_config.alias else model}，配置：{json}"
        )
        # if model == "deepseek-chat":
        #     json.update({"tools": registry.to_json()})
        if model_dump(model_config, exclude_none=True).get("stream", ds_config.stream):
            ret = await stream_request(model_config.base_url, api_key, json, proxy)
        else:
            ret = await common_request(model_config.base_url, api_key, json, proxy)

        return ret

    @classmethod
    async def query_balance(cls, model_name: str) -> Balance:
        model_config = ds_config.get_model_config(model_name)
        api_key = model_config.api_key or ds_config.api_key

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{model_config.base_url}/user/balance",
                headers={**cls._headers, "Authorization": f"Bearer {api_key}"},
            )
        if response.status_code == 404:
            raise RequestException("本地模型不支持查询余额，请更换默认模型")
        return Balance(**response.json())

    @classmethod
    async def get_tts_models(cls) -> list[TTSModelInfo]:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{tts_config.base_url}/models",
                    headers={**cls._headers},
                    json={"version": tts_config.tts_version},
                    timeout=tts_config.timeout,
                )
            if response.status_code != 200:
                raise RequestException(f"获取 TTS 模型列表失败，状态码: {response.status_code}")
            return [
                TTSModelInfo(model_name=key, language_emotions=value)
                for key, value in response.json().get("models", {}).items()
                if isinstance(value, dict)
            ]
        except httpx.ConnectError as e:
            raise RequestException(f"连接 TTS 模型服务器失败: {e}")

    @classmethod
    async def text_to_speach(cls, text: str, model: str) -> bytes:
        model_config = tts_config.get_tts_model(model)
        model_name = model_config.model_name
        json = {
            "text": text,
            "model_name": model_name,
            "app_key": tts_config.access_token,
            "access_token": tts_config.access_token,
            "version": tts_config.tts_version,
            "dl_url": tts_config.dl_url,
            **model_config.to_dict(),
        }

        tts_logger("DEBUG", f"使用模型 {model}，配置：{json}")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{tts_config.base_url}/infer_single",
                    headers={**cls._headers, "Authorization": f"Bearer {tts_config.access_token}"},
                    json=json,
                    timeout=tts_config.timeout,
                )
            tts_logger("DEBUG", f"Response: {response.status_code} {response.text}")
            if audio_url := response.json().get("audio_url"):
                async with httpx.AsyncClient() as client:
                    response = await client.get(audio_url, timeout=tts_config.timeout)
                    return response.content
            else:
                raise RequestException("语音合成失败")
        except (httpx.ConnectError, httpx.ReadTimeout) as e:
            raise RequestException(f"连接 TTS 服务器失败: {e}")


async def common_request(base_url: str, api_key: str, json: dict, proxy: Optional[str] = None):
    timeout_config = ds_config.timeout
    async with httpx.AsyncClient(proxy=proxy) as client:
        response = await client.post(
            f"{base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=json,
            timeout=(timeout_config if isinstance(timeout_config, int) else timeout_config.api_request),
        )
    if error := response.json().get("error"):
        raise RequestException(error["message"])
    return ChatCompletions(**response.json())


async def stream_request(base_url: str, api_key: str, json: dict, proxy: Optional[str] = None):
    json["stream"] = True
    async with httpx.AsyncClient(http2=True, proxy=proxy, timeout=None) as client:
        async with client.stream(
            "POST",
            f"{base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=json,
        ) as response:
            ret_list: Optional[StreamChoiceList] = None
            async for chunk in response.aiter_lines():
                ret = sse_middle(chunk)
                if ret is None:
                    continue
                elif ret[0] == "data":
                    if ret[1] == "[DONE]":
                        break
                    else:
                        try:
                            i = loads(ret[1])
                            if ret_list is None:
                                ret_list = StreamChoiceList(**i)
                            else:
                                ret_list += StreamChoiceList(**i)
                        except Exception as e:
                            ds_logger("ERROR", f"解析数据块失败：{ret[1]} ||{e}")

                elif ret[0] == "::":
                    ds_logger("ERROR", f"SSE注释：{ret[1]}")
                    continue
                elif ret[0] == "error":
                    raise RequestException(ret[1])
                else:
                    continue
            if ret_list is None:
                raise RequestException("Oops! 网络超时，请稍后重试")
            return ret_list.transform()


def sse_middle(
    line: str,
) -> Union[tuple[Literal["data", "event", "id", "retry", "::", "error"], str], None]:
    """单行SSE数据解析"""
    line = line.strip("\r")
    if not line:
        return None
    if ":" in line:
        field, value = line.split(":", 1)
        value = value.strip()
    else:
        return None
    if field == "":
        return "::", value
    elif field == "data" or field == "event" or field == "id" or field == "retry":
        return field, value

    return "error", line
