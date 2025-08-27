from user_agents import parse as ua_parse

def parse(ua_string):

    user_agent = ua_parse(ua_string)

    data = {}
    # 浏览器属性
    data['browser_family'] = user_agent.browser.family
    data['browser_version'] = user_agent.browser.version_string

    # 操作系统属性
    data['os_family'] = user_agent.os.family
    data['os_version'] = user_agent.os.version_string

    # 设备属性
    data['device_family'] = user_agent.device.family
    data['device_brand'] = user_agent.device.brand
    data['device_model'] = user_agent.device.model


    data['is_mobile'] = user_agent.is_mobile
    data['is_pc'] = user_agent.is_pc
    data['is_touch_capable'] = user_agent.is_touch_capable # 可触摸
    data['is_tablet'] = user_agent.is_tablet # 平板(iPad,Kindle)
    data['is_bot'] = user_agent.is_bot # 是否搜索引擎爬虫
    data['is_email_client'] = user_agent.is_email_client

    return data