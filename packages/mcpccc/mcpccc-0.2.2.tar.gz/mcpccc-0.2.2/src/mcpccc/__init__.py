from mcp.server.fastmcp import FastMCP
import requests
import json
import time

# Create an MCP server
mcp = FastMCP("Demo")


# require subject get content
@mcp.tool()
def getContentBySubject(subject: str) -> str:
    """请求Google Search接口传值并返回内容"""
    api_url = "https://v5.kaleido.guru/api/api_flow/invoke/46423c66-c7bc-4f59-af43-7cea335b2da1"
    headers = {
        "apiKey": "default",
        "Content-Type": "application/json"
    }
    
    # POST请求获取内容
    post_data = {
        "data_rows": {
            "keyword": subject,
            "method": "GET"
        }
    }
    
    try:
        response = requests.post(api_url, json=post_data, headers=headers)
        response.raise_for_status()  # 检查HTTP错误
        
        # 返回响应内容
        result = response.json()
        
        # 检查status是否为0，如果是则获取job_id并开始轮询
        if result.get("status") == 0:
            body = result.get("body", {})
            job_id = body.get("job_id")
            if not job_id:
                return "未找到job_id"
            
            # 开始轮询获取结果
            poll_url = f"{api_url}/{job_id}"
            max_attempts = 60
            
            for attempt in range(max_attempts):
                try:
                    poll_response = requests.get(poll_url, headers=headers)
                    poll_response.raise_for_status()
                    poll_result = poll_response.json()
                    
                    # 检查body下的content
                    poll_body = poll_result.get("body", {})
                    content = poll_body.get("content")
                    
                    if content is not None:
                        return content
                    
                    # 如果content为null，等待5秒后继续轮询
                    time.sleep(5)
                    
                except requests.exceptions.RequestException as e:
                    return f"轮询请求错误: {str(e)}"
                except json.JSONDecodeError as e:
                    return f"轮询JSON解析错误: {str(e)}"
            
            # 轮询60次还没结果
            return "出错啦，请重新输入"
            
        else:
            return f"API错误: status={result.get('status')}, message={result.get('message', '未知错误')}"
        
    except requests.exceptions.RequestException as e:
        return f"请求错误: {str(e)}"
    except json.JSONDecodeError as e:
        return f"JSON解析错误: {str(e)}"
    except Exception as e:
        return f"未知错误: {str(e)}"

# require url get content
@mcp.tool()
def getContentByUrl(url: str) -> str:
    """提供url链接获取网页内容"""
    api_url = "https://v5.kaleido.guru/api/api_flow/invoke/8c23597c-95d3-4f3a-aca3-be22f849f451"
    headers = {
        "apiKey": "default",
        "Content-Type": "application/json"
    }
    
    # POST请求获取内容
    post_data = {
        "data_rows": {
            "url": url,
        }
    }
    
    try:
        response = requests.post(api_url, json=post_data, headers=headers)
        response.raise_for_status()  # 检查HTTP错误
        
        # 返回响应内容
        result = response.json()
        
        # 检查status是否为0，如果是则获取job_id并开始轮询
        if result.get("status") == 0:
            body = result.get("body", {})
            job_id = body.get("job_id")
            if not job_id:
                return "未找到job_id"
            
            # 开始轮询获取结果
            poll_url = f"{api_url}/{job_id}"
            max_attempts = 60
            
            for attempt in range(max_attempts):
                try:
                    poll_response = requests.get(poll_url, headers=headers)
                    poll_response.raise_for_status()
                    poll_result = poll_response.json()
                    
                    # 检查body下的content
                    poll_body = poll_result.get("body", {})
                    content = poll_body.get("content")
                    
                    if content is not None:
                        return content
                    
                    # 如果content为null，等待5秒后继续轮询
                    time.sleep(5)
                    
                except requests.exceptions.RequestException as e:
                    return f"轮询请求错误: {str(e)}"
                except json.JSONDecodeError as e:
                    return f"轮询JSON解析错误: {str(e)}"
            
            # 轮询60次还没结果
            return "出错啦，请重新输入"
            
        else:
            return f"API错误: status={result.get('status')}, message={result.get('message', '未知错误')}"
        
    except requests.exceptions.RequestException as e:
        return f"请求错误: {str(e)}"
    except json.JSONDecodeError as e:
        return f"JSON解析错误: {str(e)}"
    except Exception as e:
        return f"未知错误: {str(e)}"


# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"

def main() -> None:
    mcp.run(transport="stdio")
