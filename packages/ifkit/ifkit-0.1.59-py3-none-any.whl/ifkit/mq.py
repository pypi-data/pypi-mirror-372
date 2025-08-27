"""
pip install mq_http_sdk
"""

import sys
import time
from mq_http_sdk.mq_exception import MQExceptionBase
from mq_http_sdk.mq_producer import *
from mq_http_sdk.mq_client import *


# 生产者通过HTTP协议发送消息
def send_http(host, access_id, access_key, instance_id, topic_name, message_body, message_tag, message_key):
    mq_client = MQClient(host=host, access_id=access_id, access_key=access_key)

    producer = mq_client.get_producer(instance_id, topic_name)
    
    try:
        msg = TopicMessage(message_body, message_tag)           
        msg.put_property("__key", "__value")  # 设置属性
        msg.set_message_key(message_key)
        # msg.set_sharding_key("")

        re_msg = producer.publish_message(msg)        
        return re_msg.message_id
    except MQExceptionBase as e:
        if e.type == "TopicNotExist":
            print("Topic not exist, please create it.")            
        print("Publish Message Fail. Exception:%s" % e)

    return None


# 消费者通过HTTP协议消费消息
def consume_loop_http(host, access_id, access_key, instance_id, topic_name, group_id, callback):

    mq_client = MQClient(host=host, access_id=access_id, access_key=access_key)    
    consumer = mq_client.get_consumer(instance_id, topic_name, group_id)
    wait_seconds = 3
    batch = 3
    while True:
        try:
            # recv_msgs = consumer.consume_message_orderly(batch, wait_seconds)
            recv_msgs = consumer.consume_message(batch, wait_seconds)
            for message in recv_msgs:
                # 回调业务方法
                callback(message)
                consumer.ack_message(message.receipt_handle.split())                
                
        except MQExceptionBase as e:
            if e.type == "MessageNotExist":
                # print(("No new message! RequestId: %s" % e.req_id))                
                # continue
                # break
                time.sleep(5)
                continue

            print(("Consume Message Fail! Exception:%s\n" % e))
            time.sleep(2)
            continue


