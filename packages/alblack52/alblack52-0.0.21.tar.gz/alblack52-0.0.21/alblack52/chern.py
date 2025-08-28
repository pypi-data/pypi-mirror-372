import requests

PROXY_BASE_URL = "http://10.158.240.13:8000"
PROXY_SECRET = "dns"  # тот самый, что ты задал в PROXY_SECRET

def ask_phind(messages, model="deepseek-ai/DeepSeek-R1-0528"):
    url = f"{PROXY_BASE_URL}/api/proxy"
    headers = {"X-Proxy-Secret": PROXY_SECRET, "Content-Type": "application/json"}
    data = {"messages": messages, "model": model}
    resp = requests.post(url, headers=headers, json=data, timeout=60)

    if resp.status_code == 200:
        j = resp.json()
        return j.get("text") or j.get("upstream")
    else:
        return f"Error {resp.status_code}: {resp.text}"
