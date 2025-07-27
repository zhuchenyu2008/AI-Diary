import requests
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

def get_summary_from_ai(events):
    prompt = config['DEFAULT']['AI_PROMPT']

    for event in events:
        if event['event_type'] == 'text':
            prompt += f"\n- {event['content']}"
        elif event['event_type'] == 'image':
            prompt += f"\n- [Image: {event['file_path']}]"

    headers = {
        "Authorization": f"Bearer {config['DEFAULT']['AI_API_KEY']}",
        "Content-Type": "application/json"
    }

    data = {
        "model": config['DEFAULT']['AI_MODEL_NAME'],
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(config['DEFAULT']['AI_API_BASE'], headers=headers, json=data)

    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        # Handle error
        return None
