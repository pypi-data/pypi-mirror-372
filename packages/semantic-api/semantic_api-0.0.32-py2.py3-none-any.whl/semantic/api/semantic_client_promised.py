import asyncio
import threading
import json
import re
from pymonad.either import Either, Left, Right
from typing_extensions import Final

from semantic.common.utils import msg, err, greenMsg, redMsg, subscription_topics, getDbId, config_request_topic, service_request_topic
from semantic.common.common_types import PipeArg, SemanticConfig, SchemaId

from semantic.api.config   import port, username, password
from semantic.py_mqtt.py_mqtt import MQTTClient


class semanticClient:

  def __init__(self, loop, brokerIp: str, schemaId: SchemaId):
     self.loop = loop
     self.brokerIp = brokerIp
     self.mqtt = MQTTClient( loop, brokerIp, port, username, password, subscription_topics(getDbId(schemaId)) )
     
     '''
        schmaDef state ultimately maintained on semantic server, state default is locally maintained in config.py
     '''
     self.schemaId = schemaId
  

  
  #async def insert(self, doc: str):
  def insert(self, doc: str, pipeType: str):
      '''
      deprecated this frame: old idea AFAIR
      frame = {
        '@type': 'InsertStatus',
        'status': 'requested'
      }
      '''
  
      pipe_args: PipeArg = {
          "schema": self.schemaId,
          "topic": service_request_topic(getDbId(self.schemaId)),
          "doc": doc,
          "frame": None,
          "pipeType": pipeType
      }

      #redMsg('insert args '+json.dumps(pipe_args, indent=6))
      #result = {}
      promise = None
      try:
        #result = await self.insert_primitive(pipe_args)
        promise = self.insert_primitive(pipe_args, pipeType)
      except Exception as e:
          txt = f'semantic_client: insert : Exception: {e}'
          redMsg(txt)
          
      #return result
      return promise
  

  async def frame(self, frame: str):
      pipe_args: PipeArg = {
          "schema": self.schemaId,
          "topic": service_request_topic(getDbId(self.schemaId)),
          "doc": None,
          "frame": frame 
      }
      response = None
      try:
         response =  await self.query_primitive(pipe_args)
      except Exception as e:
          txt = f'semantic_client: frame : Exception: {e}'
          redMsg(txt)
          return Left(txt)

      if response is None:
        return Left(f'error on query forframe {json.dumps(frame, indent=6)}')
      else:
        return Right(response.get('doc'))


  #async def insert_primitive(self, args: PipeArg):
  def insert_primitive(self, args: PipeArg):
      #stringified= json.dumps(args)
      
      #query_result = self.mqtt.publish(args.get('topic'), stringified)
      query_result = {}
      try:
       #query_result = await asyncio.wrap_future(asyncio.run_coroutine_threadsafe(self.mqtt.publish_with_response(args.get('topic'), stringified), self.loop))
        promise = self.mqtt.publish(args.get('topic'), args)
      except Exception as e:
          txt = f'semantic_client: insert_primitive : Exception: {e}'
          redMsg(txt)
    
      #greenMsg('insert_primitive result: '+str(query_result))
     
      #return query_result
      return promise
     
  async def query_primitive(self, args: PipeArg):
     # stringified= json.dumps(args)
      # msg('query_primitive args: '+stringified)
      
      query_result = {}
      try:
          query_result = await asyncio.wrap_future(asyncio.run_coroutine_threadsafe(self.mqtt.publish_with_response(args.get('topic'), args), self.loop))
      except Exception as e:
          txt = f'semantic_client: query_primitive : Exception: {e}'
          redMsg(txt)
      
      #greenMsg('query response: '+json.dumps(query_result, indent=6))
     
      return query_result
  

  async def semantic_config(self, command: str, args: any):
      msg('semantic_config : '+command)
      body: SemanticConfig = {
          "@type": "sc:SemanticConfig",
          "dispatch": command,
          "args": args
        }
      
     
      pipe_args: PipeArg = {
          "schema": self.schemaId,
          "topic": config_request_topic(getDbId(self.schemaId)),
          "doc": body,
          "frame": None 
        }
      #greenMsg('semantic_config pipe_args: '+json.dumps(pipe_args, indent=6))
      return await self.query_primitive(pipe_args)

  
  async def getSchemaId(self):
    result = await self.semantic_config('getSchemaIdInUse', None)
    greenMsg('getSchemaId: '+json.dumps(result, indent=6))
    return result.get('doc')
  
  async def setSchemaId(self, args: SchemaId):
    result = await self.semantic_config('setCurrentSchemaId', args)
    greenMsg('setSchemaId: '+json.dumps(result, indent=6))
    return result.get('doc')


  def listDbs():
     pass
     

  def listTypeNamesForSchema():
     pass
  def listClusterNamesForSchema():
     pass
  def listSupportedSchemas():
     pass


  def createDbForSchemaId():
    pass

  def schemaQuery():
     pass

  def queryStar():
     pass
  def getSchema():
     pass

  def getSchemaInDb():
     pass
  
  