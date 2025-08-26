from behave import *
from behave.api.async_step import async_run_until_complete
import asyncio
from typing_extensions import Final
from pyrsistent import pmap, m
from pymonad.either import Either
from pymonad.promise import Promise
from pymonad.tools import curry
import json, re

from semantic.common.utils import msg, redMsg, greenMsg, sort_by_instance, refForPath, defineSchemaId, out_either, resolve_promised, chain_out, resolve_either, reject_either
from semantic.api.semantic_api import frame_constructor, flatten, function_constructor

from semantic.fera.fera_types.type_constructors import joint_state, tool_center_point_state
from tests.steps.deprecate_test_data import  type1, name1, name2, shoulder_pan_name, joint_state_test1, joint_state_test2, parent, shoulder_pan_path, float6



'''
  construct an insert
  see ../environment.py for semantic and MQTTClient initialization
'''

@given('we have a semantic instance for a schema')
def step_impl(context):
  assert context.semantic.client.schemaId is not None

@when('we narrate with a JointState instance')
@async_run_until_complete
async def step_impl(context):
    context.semantic.set_auto_insertion(False)
    await context.semantic.narrate(joint_state_test1)
    keys = context.semantic.type_map_keys()
    for k in keys:
     assert k == 'JointState'

@then('check that what we get out is what we expect')
def step_impl(context):
    eitherMap: Either = context.semantic.get_insert_instance(type1,name1)
    result = eitherMap.either(lambda e: f'Error: get_insert_instance: {e}', lambda x: x)
    if eitherMap.is_left():
       msg('result of get_insert_instance '+type1+'  '+name1+' is_left()')

    msg('result '+json.dumps(result))
    js = joint_state_test1().either(lambda e: f'Error: joint_state_instance: {e}', lambda x: x)
    msg('joint_state_test1 '+json.dumps(js))
    assert result == js

'''
  serialize an insert
'''

@given('we have constructed an insert')
def step_impl(context):
  assert context.semantic.type_map_keys() != None

@when('we serialize the insert')
def step_impl(context):
    flatMap: Either = context.semantic.get_flat_type_map()
    context.flatMap = flatMap.either(lambda e: f'Error: get_flat_type_map: {e}', lambda x: x)
    assert flatMap.is_right()

@then('we check that the serializations match')
def step_impl(context):
    js = joint_state_test1().either(lambda e: f'Error: joint_state_instance: {e}', lambda x: x)
    assert json.dumps(context.flatMap) == json.dumps([js])

'''
  multiple inserts
'''
    
   
@given('we narrate a second instance')
@async_run_until_complete
async def step_impl(context):
  context.semantic.set_auto_insertion(False)
  await context.semantic.narrate(joint_state_test2)
  assert context.semantic.type_map_keys() != None



@when('we serialize all the inserts')
def step_impl(context):
    flatMap: Either = context.semantic.get_flat_type_map()
    context.flatMap = flatMap.either(lambda e: f'Error: get_flat_type_map: {e}', lambda x: x)
    assert flatMap.is_right()

@then('we check we got it all')
def step_impl(context):
    #note extra cost sorting: required only for assertion

    js1 = joint_state_test1().either(lambda e: f'Error: joint_state_instance: {e}', lambda x: x)
    js2 = joint_state_test2().either(lambda e: f'Error: joint_state_instance: {e}', lambda x: x)

    serializedInsert = json.dumps(sorted(context.flatMap, key=sort_by_instance))
    referenceInsert = json.dumps(sorted([js1, js2], key=sort_by_instance))
    context.semantic.remove_from_map(type1, name1)
    context.semantic.remove_from_map(type1, name2)

    assert  serializedInsert == referenceInsert

'''
    insert the array of flattened typeMap to the db
'''    

@given('we have a connection to the semantic service and can define a schema on it')
@async_run_until_complete
async def step_impl(context):
   '''
        get current schema in service 
   '''
   currentSchemaId = await context.semantic.client.getSchemaId()
   '''
        define a schema id, set that in service, and get the service definition
   '''
   testSchemaId = defineSchemaId('someschema', 'v000', 'someinstance','somedbip')
   testSchemaIdInUse = await context.semantic.client.setSchemaId(testSchemaId)
   '''
        set back the original schema def 
   '''
   await context.semantic.client.setSchemaId(currentSchemaId)
   '''
        assert that the schema was set in the service as intended
   '''
   assert testSchemaId.get('schemaName') == testSchemaIdInUse.get('schemaName') and testSchemaId.get('schemaVersion') == testSchemaIdInUse.get('schemaVersion') and testSchemaId.get('instanceName') == testSchemaIdInUse.get('instanceName')
 

'''
   Scenario: we have a USD model in the db for more realistic tests
'''

@given('we have a semantic usd representation of a ur robot in the db where we can get the name for the shoulder_pan_joint')
@async_run_until_complete
async def step_impl(context):
   '''
        get the name for the shoulder_pan_joint 
   '''
   path_either : Either = await context.pathMap.get_usd_path_for_segment( shoulder_pan_name)
   path = path_either.either(lambda e: f'Error: shoulder_pan_name: {e}', lambda x: x)

   if path_either.is_right() and path is not None:
      assert path == shoulder_pan_path
   else:
      redMsg(f'asserting False as get_usd_path_for_segment: {path}')
      assert False


@then('we can verify that our usdPathMap works as well')
@async_run_until_complete
async def step_impl(context):
   await context.pathMap.set_usd_path_for_segment( shoulder_pan_name)

   path = context.pathMap.get(shoulder_pan_name)
 
  # assert path == shoulder_pan_path
   if  path is not None:
    greenMsg(f'usdPathMap: path {path}')
    assert path == shoulder_pan_path
   else:
      redMsg(f'asserting False as pathMap.get: {path}')
      assert False

@then('we can emulate the terminusdb insertion reference (terminus object uri format) for the joint object and validate that the ref matches the expected')
@async_run_until_complete
async def step_impl(context):
      ref_either = await context.pathMap.ref_for_usd_object(shoulder_pan_name)
      ref = ref_either.either(lambda e: f'ref_for_usd_object Error: shoulder_pan_name: {e}', lambda x: x)
      greenMsg(f'ref_for_usd_object {ref}')
      greenMsg(f'parent {parent}')
      assert ref == parent



@then('we use a type constructor and narrate')
@async_run_until_complete
async def step_impl(context):
    
    ref_either = await context.pathMap.ref_for_usd_object( shoulder_pan_name)
    parent = ref_either.either(lambda e: f'ref_for_usd_object Error: shoulder_pan_name: {e}', lambda x: x)
    greenMsg(f'parent {parent}')

    joint_state_data = joint_state(shoulder_pan_name, 'now', 'now', 1, parent, 0.11, 0.22, 0.33)
    context.semantic.set_auto_insertion(False)
    await context.semantic.narrate(joint_state_data)

    eitherMap: Either = context.semantic.get_insert_instance(type1, shoulder_pan_name)
    result = eitherMap.either(lambda e: f'Error: get_insert_instance: {e}', lambda x: x)
    if eitherMap.is_left():
       msg('result of get_insert_instance '+type1+'  '+shoulder_pan_name+' is_left()')

    msg('result '+json.dumps(result))
    msg('joint_state_test1 '+json.dumps(out_either(joint_state_data(), 'joint state')))
    assert result == out_either(joint_state_data(), 'joint state')
    

@then('we flatten the cached semantic data in the typeMap, insert it into the db, and check that the instance we query for, matches what we inserted')
@async_run_until_complete
async def step_impl(context):
  
  eitherMap: Either = context.semantic.get_insert_instance(type1, shoulder_pan_name)
  instance_from_insert = eitherMap.either(lambda e: f'Error: get_insert_instance: {e}', lambda x: x)
  if eitherMap.is_right():
      greenMsg('instance_from_insert '+json.dumps(instance_from_insert, indent=6))

  await context.semantic.insert()
  
  frame = {
                "@type": type1,
                "name": shoulder_pan_name
          }
  

  retrieved = await context.semantic.client.frame(frame)

  assert out_either(retrieved, 'frame')['name'] == instance_from_insert['name']
  #assert False


@then('we clear the map')
def step_impl(context):

  context.semantic.clear_map()
    
  eitherClearedMap: Either = context.semantic.get_insert_instance(type1, shoulder_pan_name)

  assert eitherClearedMap.is_left()

'''    
    Scenario: we work with ToolCenterPointState
'''

@given('we use the ToolCenterPointState type constructor and narrate')
@async_run_until_complete
async def step_impl(context):
#from semantic_api.api_python.src.test_data import  type1, name1, name2, shoulder_pan_name, joint_state_test1, joint_state_test2, parent, shoulder_pan_path, float6

   
   path_either : Either = await context.pathMap.get_usd_path_for_segment( 'base_link')
   path = path_either.either(lambda e: f'Error: base_link: {e}', lambda x: x)

   if path_either.is_right() and path is not None:
      parent = refForPath("UsdPrim", path, "SpecifierDef")
      greenMsg('refForPath: '+json.dumps(parent, indent=6))
      tcp_state = tool_center_point_state('base_link', 'now', 'now', 1, parent, float6, float6, float6)
      context.semantic.set_auto_insertion(True)
      await context.semantic.narrate(tcp_state)
      eitherMap: Either = context.semantic.get_insert_instance('ToolCenterPointState', 'base_link')
      result = eitherMap.either(lambda e: f'Error: get_insert_instance: {e}', lambda x: x)
      if eitherMap.is_left():
          assert False
          redMsg(f'asserting False as get_usd_path_for_segment: {path}')
      else:
          assert True
     
@then('we use the simplest means of fetching a parent ref')
@async_run_until_complete
async def step_impl(context):
   
   ref_either : Either = await context.pathMap.ref_for_usd_object('base_link')
   ref = ref_either.either(lambda e: f'Error: getRefForPrim: {e}', lambda x: x)

   if ref_either.is_right():
          assert True
   else:
          assert False
     

'''
     Scenario: we chain functionality
'''

@given('we construct a pipeline')
@async_run_until_complete
async def step_impl(context):
  @curry(2)
  def div(y, x):
    return x / y

  async def long_id(x):
    await asyncio.sleep(1)
    return await Promise(lambda resolve, reject: resolve(x))
  
  async def add_1(x):
     result = x+1
     return await Promise(lambda resolve, reject: resolve(result))
  
  

  result = await context.semantic.chain(3, add_1, add_1, add_1, resolve_promised)
  assert result == 6


@then('we chain a query')
@async_run_until_complete
async def step_impl(context):

  query = context.semantic.query_constructor()

  db_frame = {
                "@type": type1,
                "name": shoulder_pan_name
          }
  
  local_frame = {
                "name": ""
          }
 
  select_shoulder_pan = context.semantic.select_constructor(local_frame)
 
  result = await context.semantic.chain(db_frame, query, select_shoulder_pan, flatten, chain_out)

  greenMsg('chain result query'+json.dumps(result, indent=6))
  assert result[0] == shoulder_pan_name


@then('we embed a query in the middle of the pipe')
@async_run_until_complete
async def step_impl(context):
  
  query = context.semantic.query_constructor()

  frame = frame_constructor({
                "@type": 'UsdPrim',
                "segmentName": 'base_link'
          })
  
  path = {
          "path": {}
         }
  
  select_path = context.semantic.select_constructor(path)

  result = await context.semantic.chain({},frame, query, select_path, chain_out)

  greenMsg('chain result query'+json.dumps(result, indent=6))
  assert result['path'] == "/ur10/base_link"


@then('we use a user-defined function in the pipe')
@async_run_until_complete
async def step_impl(context):

  query = context.semantic.query_constructor()

  db_frame = {
                "@type": 'UsdPrim',
                "segmentName": 'base_link'
             }
    
  
  def user_func(args):
     result: list[str] = []
     api_schemas = args['apiSchemas']
     
     for api in api_schemas:
        result.append(api)
     return result
  
  users_function = function_constructor(user_func)
  
  result = await context.semantic.chain(db_frame, query, users_function, chain_out)
 
  greenMsg('chain result query'+json.dumps(result, indent=6))
  assert result[0] == "PhysicsArticulationRootAPI"



@then('we test query_constructor and query function')
@async_run_until_complete
async def step_impl(context):

  query = context.semantic.query_constructor()

  db_frame = {
                "@type": 'UsdPrim',
                "segmentName": 'base_link'
             }
    
  
  def user_func(args):
     result: list[str] = []
     api_schemas = args['apiSchemas']
     
     for api in api_schemas:
        result.append(api)
     return result
  
  users_function = function_constructor(user_func)
  
  result = await context.semantic.chain(db_frame, query, users_function, chain_out)
 
  greenMsg('chain result query'+json.dumps(result, indent=6))
  assert result[0] == "PhysicsArticulationRootAPI"


'''    
    Scenario: narration of data loads and resulting insertion batching, map clearing, and map cycling'
'''

@given('we narrate a data stream')
@async_run_until_complete
async def step_impl(context):


   ref_either : Either = await context.pathMap.ref_for_usd_object('base_link')
   ref = ref_either.either(lambda e: f'ref_for_usd_object(base_link) Error : {e}', lambda x: x)
   if ref_either.is_right() and ref is not None:
      parent = ref
      
      async def async_generator():
        for i in range(10):
            yield i

      async_iter = aiter(async_generator())

      async for index in async_iter:
         await context.semantic.narrate( tool_center_point_state('base_link_test_df_'+str(index), 'now', 'now', 1, parent, float6, float6, float6))

      await context.semantic.insert()
   else:
      redMsg('narration failure as path is left or None')

   '''
    frame for type/name to assert type/name equality with one of the narrated
    currently using false to flush out console logs
   '''
   query = context.semantic.query_constructor()
   db_frame = {
                "@type": "ToolCenterPointState",
                "name": "base_link_test_df_1"
             }
   select_frame = {
                "name": "resultwildcard"
              }
   select_name = context.semantic.select_constructor(select_frame)
   result = await context.semantic.chain(db_frame, query, select_name, chain_out)
   greenMsg('result '+json.dumps(result, indent=6))

   assert  result.get("name") == db_frame.get("name")


   '''
    todo tests:
                  set_batch_size
                  semantic.insert() for remainder

    todo other:
                  investigate acknowledge handshake at insertion rather than insertion success to || processing
                  check timestamp correlation and duration of query invocation vs terminus PUT timestamps,i.e. where is insertion processing costing time
                  plot lag of second batch vs memory size for different batch
   '''