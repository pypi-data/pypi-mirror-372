import requests

def send_markdown_message(content, key):
    url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=%s'
    url = url % (key,)
    payload = {
        'msgtype': 'markdown',
        'markdown': {
            'content': content
        }
    }
    response = requests.post(url, json=payload)
    return response.json()