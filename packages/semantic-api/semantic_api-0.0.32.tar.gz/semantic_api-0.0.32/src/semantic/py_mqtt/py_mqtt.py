import json
import asyncio
import time
#from datetime import timezone
import datetime
import random 
import socket
import traceback
from typing import Optional, Tuple, List
from pyrsistent import m, PMap

from typing_extensions import Final
from pymonad.promise import Promise, _Promise, ResolveFunction, RejectFunction, PromiseFunction
from pymonad.tools import curry
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
        self.futureMap: PMap = m()
        self.noOfTopics = len(subscribe_topics)
        self.isSubscribed = self.loop.create_future()
        self.client = self.connect(self.broker_address, self.port, self.username, self.password)

        self.client.on_log = self._on_log
   


    async def resolve_subscription(self, value):
        self.isSubscribed.set_result(value)      
   
    async def is_subscribed(self):
        '''
            for use in the client's main to await subscription prior to publishing
            otherwise, publish will precede subscription
        '''
        value = await self.isSubscribed
        return value
    

    def _on_log(self, client, userdata, paho_log_level, messages):
        if paho_log_level == mqtt.LogLevel.MQTT_LOG_ERR: #MQTT_LOG_DEGUG
          redMsg('log: '+messages)

    def _on_connect(self, client, userdata, flags, reason_code, properties):
        msg('_on_connect ')
        if reason_code != 0:
            redMsg(f"MQTTClient: Failed to connect: {reason_code}. loop_forever() will retry connection")
        else:
            greenMsg(f'MQTTClient: on_connect success on: {self.broker_address}:{str(self.port)}')
            self.subscribe(self.subscribe_topics)

    def _on_disconnect(self, client, userdata, disconnect_flags, reason_code, properties):
            redMsg(f"MQTTClient disconnect: disconnect_flags: {disconnect_flags} reason_code: {reason_code}")
            self.isSubscribed.set_result(False)
            self.disconnected.set_result(reason_code)
          
    def _on_subscribe(self, client, userdata, mid, reason_code_list, properties):
        for i in range(len(reason_code_list)):
            greenMsg(f"MQTTClient: on_subscribe: subscribed: {mid}: {reason_code_list[i]}")
        '''
            the following is essentially a hack required due to python and paho-mqtt poor async design/impl
            _on_subscribe cannot be async since the api is defined by paho-mqtt, hence the thread...
        '''
        if mid == self.noOfTopics:
            asyncio.run_coroutine_threadsafe(self.resolve_subscription(True),self.loop)   

    def _on_message(self, client, userdata, message):
        # We need to map the request id and resolve the response promise on the main running loop
        # (where the api and main are running). This message is running on the mqtt client event loop
        try:
                payload = message.payload.decode('utf-8')
                payload_json = json.loads(payload)
                if "frame" not in payload_json or "doc" not in payload_json:
                    redMsg('MQTTClient: on_message: Error: not in payload_json')
                elif self.loop is not None and self.loop.is_running():
                   
                    '''
                        this is effectively just a resolve of the msg in the main thread
                        the promiseMap of requestId to promises should be maintained on the client (main)
                        side
                        do not need self.got_message since on_message handles this
                    '''
                    #greenMsg('MQTTClient: on_message: payload_json '+json.dumps(payload_json, indent=6))  

                    asyncio.run_coroutine_threadsafe(self.resolve_response(payload_json), self.loop)     
                else:
                    redMsg('MQTTClient: on_message: Error: self.loop issues')
        except Exception as e:
            redMsg(f'MQTTClient: on_message: exception: {e} {traceback.format_exc()}')
        return

    async def resolve_response(self, payload_json):
        '''
            pre-conditions:
                requestId in payload_json
                requestId in promiseMap
            invariants:
                clients may (as per manual insert or query), or may not be (as per auto-insert), awaiting on the promise
            post-conditions:
                awaiting clients get their response value
                auto (AsyncInsert) clients await on the promise, response value printed to console
                key-promise entry removed from map and map re-assigned (immutable)
        '''
        try:
            if not "requestId" in payload_json:
              redMsg('no requestId '+json.dumps(payload_json, indent=8))

            rId = payload_json.get("requestId") if "requestId" in payload_json else 0
            requestId = str(rId) if type(rId) == int else rId
          
            future = self.futureMap.get(requestId)
            if future is not None:
                self.futureMap = self.futureMap.remove(requestId)
          
                if "pipeType" in payload_json and payload_json.pipeType == 'AsyncInsert':
                    '''
                        no awaiting clients
                    '''
                    greenMsg(f'<resolve_response: No resolving as there should be no clients awaiting {requestId} ')
                else:
                    '''
                        resolve future for awaiting clients
                        future.insert == future(lambda resolve, reject: resolve(payload_json))
                    '''
                    future.set_result(payload_json)
                    #greenMsg(f'resolve_response: resolving: {requestId} as  {json.dumps(payload_json, indent=6)}')
            else:
                redMsg('resolve_response Error: no future assigned under publishing')
        except Exception as e:
            txt = f"MQTTClient: Error processing message: {e} {traceback.format_exc()}"
            redMsg(txt)
          

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

        except Exception as e:
            redMsg(f"MQTTClient: Error connecting to MQTT: {e}")
      
    async def publish_with_response(self, topic: str, args):
        """
        Will send a message to the broker, on the specified topic and wait for a response
        ¨ to return.'
        """
        try: 
            if self.loop is None or self.loop.is_running() == False:
                self.loop = asyncio.get_running_loop()
                redMsg('MQTTClient: publish_with_response : no loop, got it running')

            requestId = datetime.datetime.now().isoformat()
            #greenMsg('publish_with_response: requestId: '+requestId)
            args["requestId"] = requestId
            stringified= json.dumps(args)
            future = self.loop.create_future()
            self.futureMap = self.futureMap.update({requestId: future})

            msg_info = self.client.publish(topic, stringified, self.qos)
            msg_info.wait_for_publish()
          
            future_result = await future
            
            return future_result

        except Exception as e:
            redMsg(f"MQTTClient: publish_with_response : {e}")


    def publish(self, topic: str, args):
        '''
        Publishes a message to the broker, on the specified topic.
        Does not return a response, response is awaited on self.get_message future
        '''
        if self.loop is None or self.loop.is_running() == False:
                self.loop = asyncio.get_running_loop()
                redMsg('MQTTClient: publish : no loop, got it running')

        requestId = datetime.datetime.now().isoformat()
        #greenMsg('publish_with_response: requestId: '+requestId)
        args["requestId"] = requestId
        stringified= json.dumps(args)
        future = self.loop.create_future()
        self.futureMap = self.futureMap.update({requestId: future})

        if self.client.is_connected() == True:
           msg_info = self.client.publish(topic, stringified, self.qos)
           msg_info.wait_for_publish()
        else:
            redMsg("MQTTClient: publish client is not connected")

        return future
    
    def disconnect(self):
        if self.client.is_connected() == True:
            redMsg("MQTTClient: disconnect() called")
            self.client.disconnect()


