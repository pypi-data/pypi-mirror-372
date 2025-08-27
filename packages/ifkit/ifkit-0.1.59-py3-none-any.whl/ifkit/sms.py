import requests

# 发送短信
def send_sms(content, accesskey, secret, sign, templateId, mobile):

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'
    }

    data = {
        'accesskey': accesskey,
        'secret': secret,
        'sign': sign,
        'templateId': templateId,
        'mobile': mobile,
        'content': content
    }

    # 发送
    response = requests.post('http://api.1cloudsp.com/api/v2/single_send', data=data, headers=headers)
    return response.text