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


async def out_of_scope_promise(resolve: ResolveFunction, reject: RejectFunction):
     '''
      use-case:  use when the async promise is owned out of the scope of the function
      example:  let p = out_of_scope_promise(self.resolve, self.reject)
                const result = await p.promise
                p = p.renew()
                p.resolve(value)
                p.reject('Error')
   
            alternative design: 
                                resolve(self, resolve_func, value):
                                    return resolve_func(value)
                                reject(self, reject_func, value):
                                    return reject_func(value)
            advantages:
                                less state (no self.promise_xxx members), only awaitable
                                resolve and reject defined at time of use
            problem:
                                need them defined at time of promised definition :(
                                solution: thunk?
                                try pylint: disable=invalid-name

     '''
         
     promised = {
         "resolve": resolve,
         "reject": reject,
         "promise": await create_promise(resolve, reject),
     }

     async def create_promise():
            msg('>promised.promise')

            #function = lambda resolve, reject: resolve if resolve is not None else reject

            @curry(3)
            async def _awaitable(function, resolve, reject): 
              #resolve: ResolveFunction = promised.resolve
              #reject: RejectFunction = promised.reject
              return function(resolve, reject)
            #self.awaitable = await _Promise(_awaitable(function), None) 
            p = await _Promise(_awaitable(function), None)  # pylint: disable=no-value-for-parameter

            #p = await self.awaitable 
            msg('<promised.promise')
            return p
                 
     async def resolve(value):
            greenMsg(f'promised.resolve----- on value {value}')
            return await promised.resolve(value)
     
     async def reject(value):
            return promised.reject(value)

     return promised


async def create_promise(function: PromiseFunction):
            msg('>promised.promise')

            @curry(3)
            async def _awaitable(function, resolve, reject): 
              #resolve: ResolveFunction = promised.resolve
              #reject: RejectFunction = promised.reject
              return function(resolve, reject)
            #self.awaitable = await _Promise(_awaitable(function), None) 
            p = await _Promise(_awaitable(function), None)   # pylint: disable=no-value-for-parameter

            #p = await self.awaitable 
            msg('<promised.promise')
            return p
      

class Promised:
    #def __init__(self, resolve: ResolveFunction, reject: RejectFunction):
    def __init__(self, function: PromiseFunction):
       #self.resolve = resolve
       #self.reject = reject
        self.function = function
        self.promise = create_promise(function).__await__()
        #self.promise = create_promise(function)

    #def __await__(self):
        '''
        use-case:  use when the async promise is owned out of the scope of the function
        example:  let p = out_of_scope_promise(self.resolve, self.reject)
                    const result = await p.promise
                    p = p.renew()
                    p.resolve(value)
                    p.reject('Error')
    
                alternative design: 
                                    resolve(self, resolve_func, value):
                                        return resolve_func(value)
                                    reject(self, reject_func, value):
                                        return reject_func(value)
                advantages:
                                    less state (no self.promise_xxx members), only awaitable
                                    resolve and reject defined at time of use
                problem:
                                    need them defined at time of promised definition :(
                                    solution: thunk?
                                    try pylint: disable=invalid-name

        '''
    
        #self.promise = create_promise(self.resolve, self.reject).__await__()
   
    async def resolve(self, value):
            greenMsg(f'promised.resolve----- on value {value}')
            return await self.promise.resolve(value)
     
    async def reject(self, value):
            return self.promise.reject(value)

    def promise(self):
            return self.promise


     

def out_of_scope_promise_(resolve: ResolveFunction, reject: RejectFunction):
     '''
      use-case:  use when the async promise is owned out of the scope of the function
      example:  let p = out_of_scope_promise(self.resolve, self.reject)
                const result = await p.promise
                p = p.renew()
                p.resolve(value)
                p.reject('Error')
      '''
     
         
     class promised:
        
        def __init__(self, resolve: ResolveFunction, reject: RejectFunction):
            msg('>promised.init')
            self.promise_resolve = resolve
            self.promise_reject = reject
            #self.awaitable = Promise(self.promise_resolve, self.promise_reject)
            '''
            @curry(3)
            async def _awaitable(function, resolve, reject): 
              return function(resolve, reject)
            self.awaitable = await _Promise(_awaitable(function), None) 
            '''
            msg('<promised.init')
        '''
        def __await__(self):
           return self.value(self.promise_resolve, self.promise_reject).__await__()
        '''

        async def promise(self):
            msg('>promised.promise')

            function = lambda resolve, reject: resolve if resolve is not None else reject

            @curry(3)
            async def _awaitable(function, resolve, reject): 
              resolve: ResolveFunction = self.promise_resolve
              reject: RejectFunction = self.promise_reject
              return function(resolve, reject)
            #self.awaitable = await _Promise(_awaitable(function), None) 
            p = await _Promise(_awaitable(function), None) 

            #p = await self.awaitable 
            msg('<promised.promise')
            return p
        '''
            alternative design: 
                                resolve(self, resolve_func, value):
                                    return resolve_func(value)
                                reject(self, reject_func, value):
                                    return reject_func(value)
            advantages:
                                less state (no self.promise_xxx members), only awaitable
                                resolve and reject defined at time of use
            problem:
                                need them defined at time of promised definition :(
                                solution: thunk?
                                try pylint: disable=invalid-name

        '''
        async def resolve(self, value):
            greenMsg(f'promised.resolve----- on value {value}')
            return await self.promise_resolve(value)
        async def reject(self, value):
            return self.promise_reject(value)

     return promised(resolve, reject)

     '''
     def renew(self):
         greenMsg('out_of_scope_promise: renew')
         return out_of_scope_promise(self.resolve, self.reject)
     '''
         
def resolveFunction(value):
    redMsg(f'resolveFunction resolving value: {value}')
    return value

async def renew_promise(function: PromiseFunction):
    return Promise(function).__await__()

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
        #self.got_message = None
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
        self.promiseMap: PMap = m()
        self.resolve: ResolveFunction = resolveFunction
        self.reject: RejectFunction = lambda e: f"Exception: {e}"

        

        self.subscribe_function = lambda resolve, reject : self.resolve if self.resolve is not None else self.reject
        self.isSubscribed = Promise(self.subscribe_function).__await__()
        
        #self.isSubscribed = out_of_scope_promise(self.resolve, self.reject)
        #self.isSubscribed = Promise(self.subscribe_function)

        self.client = self.connect(self.broker_address, self.port, self.username, self.password)

        self.client.on_log = self._on_log
        #self.client.connect_timeout = 1.0
    
    def __await__(self):
        #return self.value(self._resolve, _reject).__await__()
        self.isSubscribed = self.set_promise(Promise(self.subscribe_function)) #.__await__()

    async def get_promise(self):
        return self.isSubscribed
    
    async def set_promise(self, promise):
        self.isSubscribed = await promise

    async def is_subscribed(self):
        '''
            for use in the client's main to await subscription prior to publishing
            otherwise, publish will precede subscription
        '''
        msg('>is_subscribed , awaiting subscription')
        #promise = await self.isSubscribed.promise()

        promise = await self.get_promise()
        #promise = await self.isSubscribed


        msg('<is_subscribed')
        return promise
        #return await self.client.on_subscribe
        #return await promise.promise
    
    async def resolution(self, promise):
        '''
            for use in the client's main to await subscription prior to publishing
            otherwise, publish will precede subscription
        '''
        return await Promise.apply().to_arguments(promise).catch(lambda error: 'on resolution error')


    def _on_log(self, client, userdata, paho_log_level, messages):
        if paho_log_level == mqtt.LogLevel.MQTT_LOG_ERR: #MQTT_LOG_DEGUG
          redMsg('log: '+messages)

    def _on_connect(self, client, userdata, flags, reason_code, properties):
        #self.isSubscribed = out_of_scope_promise(self.resolve, self.reject)
        msg('_on_connect ')
        if reason_code != 0:
            redMsg(f"MQTTClient: Failed to connect: {reason_code}. loop_forever() will retry connection")
        else:
            greenMsg(f'MQTTClient: on_connect success on: {self.broker_address}:{str(self.port)}')
            self.subscribe(self.subscribe_topics)

 
    def _on_disconnect(self, client, userdata, disconnect_flags, reason_code, properties):
            redMsg(f"MQTTClient disconnect: disconnect_flags: {disconnect_flags} reason_code: {reason_code}")
            self.isSubscribed.resolve(False)
            self.disconnected.set_result(reason_code)
          

    def _on_subscribe(self, client, userdata, mid, reason_code_list, properties):
        msg('>_on_subscribe ')

        for i in range(len(reason_code_list)):
            greenMsg(f"MQTTClient: on_subscribe: subscribed: {mid}: {reason_code_list[i]}")
        '''
            the following is essentially a hack required due to python and paho-mqtt poor async design/impl
            _on_subscribe cannot be async since the api is defined by paho-mqtt, hence the thread...
        '''
        #self.isSubscribed.resolve(True)
        self.resolve(True)
       # self.isSubscribed = renew_promise(self.subscribe_function).__await__()


        #asyncio.run_commmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmroutine_threadsafe(self.isSubscribed.resolve(True), self.loop)
        msg('<_on_subscribe ')

    #deprecate
    def _on_message_orig(self, client, userdata, message):
        # Do to the message is on the client event loop, we need to run it on the running loop
        # that the publish_with_response() method is running on.

        try:
                '''
                if not self.got_message:
                redMsg("MQTTClient: on_message: got unexpected message")
                else:
                '''
                payload = message.payload.decode('utf-8')
                payload_json = json.loads(payload)
                if "frame" not in payload_json or "doc" not in payload_json:
                    redMsg('MQTTClient: on_message: Error: not in payload_json')
                elif self.loop is not None and self.loop.is_running():
                    #greenMsg('MQTTClient: on_message: run coroutine threadsafe: set result of futures')
                    '''
                        this is effectively just a resolve of the msg in the main thread
                        the promiseMap of requestId to promises should be maintained on the client (main)
                        side
                        do not need self.got_message since on_message handles this
                    '''
                    asyncio.run_coroutine_threadsafe(self._set_results_of_futures(payload_json), self.loop)       
                else:
                    redMsg('MQTTClient: on_message: Error: self.loop issues')
        except Exception as e:
            redMsg(f'MQTTClient: on_message: exception: {e} {traceback.format_exc()}')
        return
    
    def _on_message(self, client, userdata, message):
        # We need to map the request id and resolve the response promise on the main running loop
        # (where the api and main are running). This message is running on the mqtt client event loop
        greenMsg('>_________MQTTClient: on_message ------------------------------')

        try:
                payload = message.payload.decode('utf-8')
                payload_json = json.loads(payload)
                if "frame" not in payload_json or "doc" not in payload_json:
                    redMsg('MQTTClient: on_message: Error: not in payload_json')
                elif self.loop is not None and self.loop.is_running():
                    #greenMsg('MQTTClient: on_message: run coroutine threadsafe: set result of futures')
                    '''
                        this is effectively just a resolve of the msg in the main thread
                        the promiseMap of requestId to promises should be maintained on the client (main)
                        side
                        do not need self.got_message since on_message handles this
                    '''
                    asyncio.run_coroutine_threadsafe(self.resolve_response(payload_json), self.loop)       
                else:
                    redMsg('MQTTClient: on_message: Error: self.loop issues')
        except Exception as e:
            redMsg(f'MQTTClient: on_message: exception: {e} {traceback.format_exc()}')
        return


    #deprecate       
    def _get_and_remove_first_value_containing_key(self, search_string, dictionary: dict):
        for key, value in dictionary.items():
            if search_string in key:
                return dictionary.pop(key)
        return None
    
    #deprecate
    async def _set_results_of_futures(self, payload_json):
        '''
        change name to resolve_future
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
            #greenMsg('resolve_response: payload_json: '+json.dumps(payload_json, indent=8)
            greenMsg('>resolve_response')


            if not "requestId" in payload_json:
              redMsg('no requestId '+json.dumps(payload_json, indent=8))
            else:
              greenMsg('requestId '+json.dumps(payload_json, indent=8))


            rId = payload_json.get("requestId") if "requestId" in payload_json else 0
            requestId = str(rId) if type(rId) == int else rId
            greenMsg('requestId: '+requestId)
            promise = self.promiseMap.get(requestId)
            self.promiseMap = self.promiseMap.remove(requestId)
          
            if "pipeType" in payload_json and payload_json.pipeType == 'AsyncInsert':
                '''
                    no awaiting clients
                '''
                greenMsg(f'<resolve_response: No resolving as there should be no clients awaiting {requestId} ')
            else:
                '''
                    resolve promise for awaiting clients
                    promise.insert == promise(lambda resolve, reject: resolve(payload_json))
                '''
                msg('resolve_response: resolving promise with payload')
                promise.resolve(payload_json)
                greenMsg(f'<resolve_response: resolving: {requestId} as  {json.dumps(payload_json, indent=6)}')

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
            '''
            if self.client.is_connected():
              return self.client
            '''

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

            #on promise change: self.got_message = self.loop.create_future()
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

            #requestId: Final = datetime.datetime.now(timezone.utc)
            greenMsg('prior dt')
            requestId = datetime.datetime.now().isoformat()
            args["requestId"] = requestId
            stringified= json.dumps(args)
            greenMsg('publish_with_response: requestId: '+requestId)

            
            promise  = Promised(self.resolve, self.reject)
            greenMsg('publish_with_response: updating')
            self.promiseMap = self.promiseMap.update({requestId: promise})
            greenMsg('publish_with_response: updated')
         
            #stringified.update({"requestId": requestId})
            
            greenMsg('publish_with_response: publishing')
            msg_info = self.client.publish(topic, stringified, self.qos)
            msg_info.wait_for_publish()
          
            greenMsg('publish_with_response: awaiting ')
            #future_result = await self.got_message
            promise_result = await promise.promise()
            
           
            #on promise chagnge: self.got_message = None
            greenMsg('<publish_with_response')

        except Exception as e:
            redMsg(f"MQTTClient: publish_with_response : {e}")


    # deprecate
    async def get_response(self, topic: str, message: str):
        """
        Will send a message to the broker, on the specified topic and wait for a response
        ¨ to return.'
        """
       
        try: 
            if self.loop is None or self.loop.is_running() == False:
                self.loop = asyncio.get_running_loop()
                redMsg('MQTTClient: get_response : no loop, got it running')

          
            future_result = await self.got_message
           
            self.got_message = None

            return future_result

        except Exception as e:
            redMsg(f"MQTTClient: get_response : {e}")
      

        '''
         nb: await on handshake but use result from map
         will require some code straightening to run both map and handshake
         suggest trying just map first if response ordering is required

        future_result = await future
        '''
        
        #greenMsg('MQTTClient publish_with_response: future resolved '+json.dumps(future_result, indent=6))
        return future_result

    def publish(self, topic: str, args):
        '''
        Publishes a message to the broker, on the specified topic.
        Does not return a response, response is awaited on self.get_message future
        '''
        if self.loop is None or self.loop.is_running() == False:
                self.loop = asyncio.get_running_loop()
                redMsg('MQTTClient: publish : no loop, got it running')

        #self.got_message = self.loop.create_future()
        #future  = self.loop.create_future()
        
        requestId = datetime.datetime.now().isoformat()
        promise  = Promised(self.resolve, self.reject)
        self.promiseMap = self.promiseMap.update(requestId, promise)

        args.update({"requestId", requestId})
        stringified= json.dumps(args)



        if self.client.is_connected() == True:
           msg_info = self.client.publish(topic, stringified, self.qos)
           msg_info.wait_for_publish()

           '''
            do we return the future  to the publishing client and let them register it with the message dispatcher?
                for transparency: yes
            currently the future is assigned to got_message
            
            porting from self.got_message 
           '''

           return promise
        else:
            redMsg("MQTTClient: publish client is not connected")
    
    def disconnect(self):
        if self.client.is_connected() == True:
            redMsg("MQTTClient: disconnect() called")
            self.client.disconnect()


def on_subscribe(mqttc, userdata, mid, reason_code_list, properties):
    greenMsg("MQTTClient: Subscribed: "+str(mid)+" "+str(reason_code_list))