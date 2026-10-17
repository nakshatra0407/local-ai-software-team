import urllib.request
import json

url = "http://localhost:11434/api/generate"

data = {
    "model": "qwen2.5:1.5b",
    "prompt": "What is Python?",
    "stream": False
}

request = urllib.request.Request(
    url,
    data=json.dumps(data).encode("utf-8"),
    headers={"Content-Type": "application/json"},
    method="POST"
)

with urllib.request.urlopen(request) as response:
    result = json.loads(response.read().decode("utf-8"))

print(result["response"])