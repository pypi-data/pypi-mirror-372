from mcp.server.fastmcp import FastMCP

import requests
import json
import base64

mcp = FastMCP("fofaService")

key = ""

@mcp.tool()
async def auth(newkey: str):
    """
    这是进行fofa搜索之前所必须的验证部分，
    在运行本mcp服务其他功能之前必须调用该函数，
    在运行其他所有功能之前，必须先验证
    key的内容必须通过询问用户获得
    
    Args:
        key (str): 验证所需要的key

    Returns:
        dict: 返回一个字典，包含key
    """
    global key
    key = newkey
    return {"key": key}

@mcp.tool()
async def search(content: str, page: str = "1"):
    """
    使用fofa搜索相关内容，
    要求语法规范符合fofa搜索的语法
    
    Args:
        content (str): 需要搜索的内容
        page (str): 需要搜索的内容页码，默认为1

    Returns:
        dict: 返回一个字典，包含搜索结果
    """
    

    search_string = content
    encoded_bytes = base64.b64encode(search_string.encode("utf-8"))
    encoded_string = encoded_bytes.decode("utf-8")
    url = "https://fofa.info/api/v1/search/all?&key=" + key + "&page=" + page + "&size=100&qbase64=" + encoded_string
    print(url)

    res = requests.get(url)
    results = json.loads(res.text)
    print(results)
    return {"results": results}

if __name__ == "__main__":
    mcp.run(transport="stdio")
