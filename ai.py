import requests
import config


def analyze_entry(text, image_url=None):
    messages = []
    if text:
        messages.append({"role": "user", "content": text})
    if image_url:
        messages.append({
            "role": "user",
            "content": {
                "type": "image_url",
                "image_url": image_url
            }
        })

    payload = {
        "model": config.AI_MODEL,
        "messages": messages
    }
    headers = {
        "Authorization": f"Bearer {config.AI_API_KEY}",
        "Content-Type": "application/json"
    }
    try:
        r = requests.post(config.AI_API_URL, json=payload, headers=headers, timeout=30)
        r.raise_for_status()
        data = r.json()
        return data['choices'][0]['message']['content']
    except Exception as e:
        return f"AI解析失败: {e}"


def summarize_day(entries):
    content = "\n".join(
        f"{e['timestamp']}: {e['content_text']} {e['analysis']}" for e in entries
    )
    messages = [
        {"role": "system", "content": "你是一个日记助手，帮用户总结每天的活动"},
        {"role": "user", "content": content}
    ]
    payload = {
        "model": config.AI_MODEL,
        "messages": messages
    }
    headers = {
        "Authorization": f"Bearer {config.AI_API_KEY}",
        "Content-Type": "application/json"
    }
    try:
        r = requests.post(config.AI_API_URL, json=payload, headers=headers, timeout=60)
        r.raise_for_status()
        data = r.json()
        return data['choices'][0]['message']['content']
    except Exception as e:
        return f"AI总结失败: {e}"
