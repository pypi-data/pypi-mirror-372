import json

import requests

from utils.image import image_to_base64


def umi_ocr(
    image_path: str, data_fmt="dict", api_url: str = "http://192.168.123.7:1224/api/ocr"
) -> str:
    base64_str = image_to_base64(image_path)
    data = {
        "base64": base64_str,
        # 可选参数示例
        # ["dict","含有位置等信息的原始字典"],
        # ["text","纯文本"]
        "options": {
            "data.format": data_fmt,
        },
    }
    headers = {"Content-Type": "application/json"}
    data_str = json.dumps(data)
    resp = requests.post(api_url, data=data_str, headers=headers)
    resp.raise_for_status()
    resp_dict = json.loads(resp.text)
    # resp_dict = DotDict(resp_dict)
    if resp_dict["code"] == 100:
        return resp_dict["data"]
    else:
        return None
