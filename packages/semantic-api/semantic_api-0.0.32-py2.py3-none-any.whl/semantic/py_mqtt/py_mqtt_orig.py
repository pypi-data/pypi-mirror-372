import json
import asyncio
import time
import random 
import socket
import traceback
from typing import Optional, Tuple, List
import paho.mqtt.client as mqtt
import paho.mqtt.enums as CallbackAPIVersion
from semantic.common.utils import msg, redMsg, greenMsg, custom_encoder



class MQTTClient:
    def __init__(self, 
                loop,
                broker_address: str,
                port: int,
                username: Optional[str] = None,
                password: Optional[str] = None,
                subscribe_topics: str | List[str] = None):

        self.loop = loop
        self.mqtt_client_id =__name__+str(random.randrange(1, 100))


        
        greenMsg('MQTTClient '+broker_address+':'+str(port)+' mqtt_client_id '+self.mqtt_client_id+' on topics: '+','.join(subscribe_topics))
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id= self.mqtt_client_id, clean_session=False, protocol=mqtt.MQTTv311,transport='tcp', reconnect_on_failure=False)
        self.disconnected = self.loop.create_future()
        self.got_message = None
        self.client.on_connect = self._on_connect
        self.client.on_connect_fail = redMsg(f'MQTTClient: on_connect_fail: connection failed on {broker_address}:{str(port)}')
        self.client.on_disconnect = self._on_disconnect
        self.client.on_unsubscribe = redMsg('MQTTClient: on_unsubscribe')
        self.client.on_socket_close = redMsg('MQTTClient: on_socket_close')
        self.client.on_subscribe = self._on_subscribe
        self.client.on_message = self._on_message
        self.broker_address = broker_address
        self.port = port
        self.username = username
        self.password = password
        self.subscribe_topics = subscribe_topics
        self.pending_queries = {}
        self.qos = 0
    
        self.client = self.connect(self.broker_address, self.port, self.username, self.password)

        self.client.on_log = self._on_log
        #self.client.connect_timeout = 1.0

    def _on_log(self, client, userdata, paho_log_level, messages):
        if paho_log_level == mqtt.LogLevel.MQTT_LOG_ERR: #MQTT_LOG_DEGUG
          redMsg('log: '+messages)

    def _on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code != 0:
            redMsg(f"MQTTClient: Failed to connect: {reason_code}. loop_forever() will retry connection")
        else:
            greenMsg(f'MQTTClient: on_connect success on: {self.broker_address}:{str(self.port)}')
            self.subscribe(self.subscribe_topics)

 
    def _on_disconnect(self, client, userdata, disconnect_flags, reason_code, properties):
            redMsg(f"MQTTClient disconnect: disconnect_flags: {disconnect_flags} reason_code: {reason_code}")
            self.disconnected.set_result(reason_code)
          

    def _on_subscribe(self, client, userdata, mid, reason_code_list, properties):
        for i in range(len(reason_code_list)):
            greenMsg(f"MQTTClient: on_subscribe: subscribed: {mid}: {reason_code_list[i]}")


    
    def _on_message(self, client, userdata, message):
        # Do to the message is on the client event loop, we need to run it on the running loop
        # that the publish_with_response() method is running on.

        try:
            if not self.got_message:
              redMsg("MQTTClient: on_message: got unexpected message")
            else:
                payload = message.payload.decode('utf-8')
                payload_json = json.loads(payload)
                if "frame" not in payload_json or "doc" not in payload_json:
                    redMsg('MQTTClient: on_message: Error: not in payload_json')
                elif self.loop is not None and self.loop.is_running():
                    #greenMsg('MQTTClient: on_message: run coroutine threadsafe: set result of futures')
                    asyncio.run_coroutine_threadsafe(self._set_results_of_futures(payload_json), self.loop)       
                else:
                    redMsg('MQTTClient: on_message: Error: self.loop issues')
        except Exception as e:
            redMsg(f'MQTTClient: on_message: exception: {e} {traceback.format_exc()}')
        return

            
    def _get_and_remove_first_value_containing_key(self, search_string, dictionary: dict):
        for key, value in dictionary.items():
            if search_string in key:
                return dictionary.pop(key)
        return None
    
    async def _set_results_of_futures(self, payload_json):
        '''
        This is run for every message no matter the topic as of now.
        '''
        try:
           
            self.got_message.set_result(payload_json)
            '''
                nb: previous line is simplified handshake without the following map
                suggest using both handshake and map if order of requests/responses is an issue

            query_key = json.dumps(payload_json.get("frame", {}))
            future = self._get_and_remove_first_value_containing_key(query_key, self.pending_queries)
            if future is not None:
                greenMsg('set result of futures: payload :'+json.dumps(payload_json, default=custom_encoder, indent=6))
                future.set_result(payload_json)
            else:
                redMsg('MQTTClient: set_results_of_fugures: future is None')
            '''
        except Exception as e:
            redMsg(f"MQTTClient: Error processing message: {e} {traceback.format_exc()}")
    
    def subscribe(self, topics: str | List[str]):
        if self.client.is_connected() == False:
            redMsg("MQTTClient: subscribe: client is not connected")
            return
        if isinstance(topics, str):
            self.client.subscribe(topics)
        else:
            for topic in topics:
                self.client.subscribe(topic)
    
    def connect(self, broker_address: str, port: int, username: Optional[str] = None, password: Optional[str] = None) -> bool:
        if username is not None and password is not None:
            self.client.username_pw_set(username, password)
        try:
            self.client.connect(broker_address, port, 60)
            
                #see issue https://github.com/eclipse-paho/paho.mqtt.python/issues/454 
            
            started = time.time()
            while time.time() - started < 5.0:
                self.client.loop_start()
                
                if self.client.is_connected():
                  return self.client
            '''
            if self.client.is_connected():
              return self.client
            '''

        except Exception as e:
            redMsg(f"MQTTClient: Error connecting to MQTT: {e}")
      

    async def publish_with_response(self, topic: str, message: str):
        """
        Will send a message to the broker, on the specified topic and wait for a response
        ¨ to return.'
        """
        greenMsg("publish_with_response topic:   "+topic)
        try: 
            if self.loop is None or self.loop.is_running() == False:
                self.loop = asyncio.get_running_loop()
                redMsg('MQTTClient: publish_with_response : no loop, got it running')

            self.got_message = self.loop.create_future()
            '''
            see comment on set_result_of_futures w.r.t map

            current_fetch_task_name = asyncio.current_task().get_name()
            dict_key = current_fetch_task_name + message
            if dict_key in self.pending_queries:
               raise ValueError("A query with this key is already pending.")
            future = self.loop.create_future()
            self.got_message = future
            self.pending_queries[dict_key] = future
            '''
            
            msg_info = self.client.publish(topic, message, self.qos)
            msg_info.wait_for_publish()
          
            future_result = await self.got_message
           
            self.got_message = None

        except Exception as e:
            redMsg(f"MQTTClient: publish_with_response : {e}")
      

        '''
         nb: await on handshake but use result from map
         will require some code straightening to run both map and handshake
         suggest trying just map first if response ordering is required

        future_result = await future
        '''
        
        #greenMsg('MQTTClient publish_with_response: future resolved '+json.dumps(future_result, indent=6))
        return future_result

    def publish(self, topic: str, payload: str):
        '''
        Publishes a message to the broker, on the specified topic.
        Does not return a response.
        '''
        if self.client.is_connected() == True:
           msg_info = self.client.publish(topic, payload, self.qos)
           msg_info.wait_for_publish()
        else:
            redMsg("MQTTClient: publish client is not connected")
    
    def disconnect(self):
        if self.client.is_connected() == True:
            redMsg("MQTTClient: disconnect() called")
            self.client.disconnect()


def on_subscribe(mqttc, userdata, mid, reason_code_list, properties):
    greenMsg("MQTTClient: Subscribed: "+str(mid)+" "+str(reason_code_list))