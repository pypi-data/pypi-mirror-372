

## Python API Concept

The intent of the python API is to simplify the robot programmer's work with semantic data, both meta, and empirically based.

The API is conceptually twofold, a **narrate** method for creating instances of semantic types to describe the world, and a **chain** method for querying, formatting, and processing semanticv data and  events.

The approach of enabling a high level semantic narrative follows Michael Beetz et. al work on NEEM and SOMA at the University of Bremen.

This API is intended to work in parallel, and independently, from the low level robot data aquired through the ```ur_rtde``` API.


### USD-SOMA-FERA ontology
Both the low level and high level data streams share the same semantic model, i.e. the ontology that defines the type schema of the data base.

This ontology is built from an integration of ontology modules (clusters):
 - usd
 - dul (DULCE, SOMA subset)
 - fera (Frederik's Novo assembly schema and machine tending types)

The design choice/postulates for this effort are:
 - follow USD as the primary ontology and enable integration and interoperability with USD and Ominverse ecosystems
 - follow SOMA to enable integration and interoperability (at the ontology level) with work from Bremen
 - follow a closed world approach where all objects are identified by a URI
 - properties are defined statically on a type or mixed in from other types via inheritance (i.e Type, not Class and Properties as per OWL)
 - child-to-parent relationship (```typeOf```) is prefered over the standard parent-to-child (```hasType```) due to performance and query decoupling
 - integration of upper level ontologies with usd is via ```UsdMultiAppliedAPI``` (also requires child-to-parent as per previous point)

### Semantic API

The semantic API offers the user two core methods. 
First, a **narrate** method for constructing and capturing meta, and empirical data that is cached in a **typeMap** untill a suitable batch size is reached for insertion into the database. Secondly, a **chain** method is used for processing data, i.e. for querying the semantic database, formatting the result, and any post processing. A post processing function may involve constructing type instances that are added to the **typeMap**.

| core methods | arguments | pre-condition | post-condition |
|:--- |:--- |:--- |:--- |
| **narrate(type-constructors-thunks)** |*type-constructor-thunks*(type, name, timestamp(s), parentObject, ...data), ... |  narrate takes one or more type specific data constructors that wraps the return of **Either**, i.e. either a validated dictionary for the type or an error in a function of no arguments | updates typeMap  with objects created by type-constructors |
| **chain(object, functions)** | initial dictionary seed object (typically frame) followed by one or more functions of one argument for the data flowing through the chain | sequence starting with object followed by functions with matching input and outputs  | functions return Promise(lambda resolve, reject: resolve(processed)) |


The indirection of the type constructors is exemplified in the following:

```
a_type_constructor = type_constructor('a-type', 'a-name', ... data)
a_type_either = a_type_constructor()
a_type = a_type_either.either(lambda e: f'Validation Error in a_type_constructor: {e}', lambda x: x)
print(json.dumps( a_type, indent=6 ))

    {
        "type": "a-type",
        "name": "a-name",
        ... data
    }

```
Type constructors can be used in **chain** as well as **narrate**.  The use-case for type constructors in the processing chain is for when a type instance is created as the result of the previous query or processing function. In this case, the final **lambda** function that is returned in the **type-constructor-thunk** shall take a (data) argument that corresponds to the output from the previous function. 


| utility methods | arguments | pre-condition | post-condition |
|:--- |:--- |:--- |:--- |
| **insert()** | None | Non-empty typeMap | insert typeMap in semantic db, then **clear()** |
| **clear()** | None | Non-empty typeMap | clear pastTypeMap, assign typeMap to pastTypeMap, create new typeMap |
| **listAbstractTypes()** | | 
| **listConcreteTypes()** | | 
| **listSubTypes(type)** | | 
| **listProperties(type)** | | 


<!-- 
Semantic configuration in main:
``` 
    semantic.configure(type, id, property, value)
``` 
-->
   

The narrative  API is based on type constructors for either meta-data or sampled-data type instances:
```
    semantic.narrate( type-1-constructor, type-2-constructor, ...type-i-constructor )
```

The **semantic.insert()** operation is typically done automatically when narrating streaming data. 

Automatic insertion is done according to the side of the typeMap in order to optimize database throughput and will depend on the sampling interval and the amount of data per sample.

An ideal target request frequency is around 1Hz for low data rates.

The buffering requires that a **semantic.insert()** call is made on completion of any narration or data collection session.

```
    semantic.narrate( type-1-constructor, type-2-constructor, ...type-i-constructor)
```
is equivalent to:

```
    semantic.narrate( type-1-constructor )
    semantic.narrate( type-2-constructor )
    semantic.narrate( type-i-constructor )
```
### Narrative decorators

Python decorators will be provided for use on user's program realization of states or events so that the appropriate meta data and timestamps are logged automatically.

Details to follow here...

### Process API

The process API takes the form of a chain of async or synchronous funtions that process input and return output as a pipeline.

```
    semantic.chain( object, func-1, func-2, ...func-i, chain_out )
```

Where **object** is the input seed that starts the chain of processing functions.

All functions in the chain,  **func-1, func-2, ...func-i** operate sequentially as an asynchronous chain to form a function pipeline.

All functions in the chain shall take a single argument that is the output from the previous function.

Functions such as select that take a parameter object as input, shall return a function with closure of that parameter object of one argument for the chain, and it is this function that is used in the chain.

### Function Constructors

| constructors | constructor arguments | returned function |
|:--- |:--- |:--- |
| **query_constructor** | no arguments (only provices closure of the semantic API data) | returns a query function for use in pipe  |
| **select_constructor** |  frame object | function for use in pipe that selects from input data according to frame and returns framed input to pipe |
| **frame_constructor** | frame object | function for use in the middle of the pipe that returning frame object to pipe for use by a following query function |
| **function_constructor** | user defined function of one argument and return type |  returns user's function wrapped for use in pipe |


### Chain (Pipe) Functions

| chain function | origin | input pre-condition | output post-condition |
|:--- |:--- |:--- |:--- |
| **query** |  semantic.query_constructor | raw frame object (chain seed or returned by previous function) | query result in JSON-LD format as Promised Either |
| **select** | semantic.select_constructor |input object as Promised Either and function with closure on frame | framed input object as Promised Either|
| **flatten** | imported from semantic | input object as Promised Either| flattend array of values  as Promised Either|
| *user-defined-function* | semantic.function_constructor and user defined function | input in format of preceding function output |  return Promise(lambda resolve, reject: resolve(Right(processed))) |
| **chain_out** | imported from semantic | input object as Promised Either| raw object or array if flattened |
| *type-constructor* | imported from fera | data input from preceding function, or partial function with closure on static variables with returned function taking one arg for use with chain input data |  return  of a function (thunk) that returns an **Either**, i.e. a function of no arguments (potentially one for data streaming in chain) that when invoked, returns either a validated dictionary for the type or an error in a function of one argument |
| **update_map** |  previous function is a *type-constructor* |  updates semantic.typeMap with object freom *type-constructor* |

The chain of async functions allows users flexibility in defining sequential processing of data as it allows a mix of functions for:

 -  frame formulation: functions for simplifying construction of frames 
 -  query response formatting: secondary (or a sequence of) frame to select and format pipeline data derived from db or sample streams
 -  user defined data processing functions to analyze data in the pipeline
 -  semantic data creation and database insertion
 -  functions as policy guards operating on conditions defined on semantic data
 -  function return as Promised Either to allow a mix of async and synchronous pipeline with error handling
 

A common use-case takes the form of:

```
    result = await semantic.chain( object , query, frame, flatten, process, out  )
```

The input is typically an object representing a JSON-LD frame that forms a declarative query against the database when followed by the query function. 

The query function takes the frame object as input which it uses to query the database.

The frame-db-response function is a partial function that has previously been defined with a frame that it will use to process the output of the query.

The flatten function will take its input object and return a value-only array.

The out function resolves the promised Either for the returned result.


### Frame node primitives

the API provides a function **frame(seed, *functions)** takes a seed frame dictionary as input to a chain of functions that operate on the seed.
One common use-case is a seed that is the desired frame and no helper **functions** are requied.
Another common use-case is a seed that is an empty dict '''{}''' and a series of helper **functions** to build up the desired frame.

are query (declarative data framing) and data processing functions that form a data processing pipeline.
The processing pipeline is defined by the function sequence: **func-1, func-2, ...func-i**.

| frame primitive functions | input pre-condition | output post-condition |
|:--- |:--- |:--- |
| **findByType(type)** |  frame and type name | **'@type': type** added to frame|
| **findByName(name)** |  frame and name | **'name': name** added to frame|
| **findByPair(key, value)** |  frame and key value | **key: value** added to frame |
| **findByCondition(key, operator, value)** |  frame and start timestamp | **key: {operator: value}** added to frame |


### Frame graph primitives

To frame the graph in either the range or domain, recurse and walk the graph using the following:

| functions for recursive framing in the range or domain of a node | input pre-condition | output post-condition |
|:--- |:--- |:--- |
| **frameRange(key, frame)** |  frame providing parent scope and key for range scope | **key: { }** added range frame on key |
| **frameDomain(key, frame)** |  frame providing parent scope and key for domain scope  | **"@reverse":{key: [{}]}** added domain frame on key |


example:

```
joint_state_frame = frame({}, findByType('JointState'), findByName('shoulder_pan_joint', findByPair('first', 'now')))

print(json.dumps(joint_state_frame(), indent=6))

    {
    "@type": "JointState",
    "name": "shoulder_pan_joint",
    "first": "now"
    }
```

to pull in the UsdPrim that that joint state is an an attribute of, you can either choose to have the graph's named node be **JointState** or the named node be **UsdPrim** with **typeName** **PhysicsRevoluteJoint**. 

```
joint_state_range = frame(joint_state_frame, frameRange('parentObject'), frame({}, findByType('UsdPrim'), findByPair('segmentName', 'shoulder_pan_joint')))

print(json.dumps(joint_state_range, indent=6))

    {
    "@type": "JointState",
    "name": "shoulder_pan_joint",
    "first": "now",
    "parentObject": 
        { 
            "@type": "UsdPrim",
            "segmentName": "shoulder_pan_joint"
        }
    }
```

```
joint_state_domain = frame({}, findByType('UsdPrim'), findByPair('segmentName', 'shoulder_pan_joint'), frameDomain(joint_state_frame))

print(json.dumps(joint_state_domain, indent=6))

    {
    "@type": "UsdPrim",
    "segmentName": "shoulder_pan_joint",
    "@reverse" : {
        "parentObject": [
        { 
            "@type": "JointState",
            "name": "shoulder_pan_joint",
            "first": "now"
        }
        ]
    }
    }
```

The playground should be used to develop frames as it can be used incrementally to explore what is in the database as for example with the frame joint_state_domain() and verify that it matches the equivalent operation via semantic.chain:

```
print(json.sdumps( await semantic.chain( joint_state_domain(), query, out )))

{
  "@context": {
    "@base": "terminusdb:///data/",
    "@vocab": "terminusdb:///schema#"
  },
  "@id": "UsdPrim/UR10%2Bur10%2Bbase_link%2Bshoulder_pan_joint+terminusdb%3A%2F%2F%2Fschema%23UsdSpecifier%2FSpecifierDef",
  "@type": "UsdPrim",
  "active": true,
  "apiSchemas": [
    "PhysicsDriveAPI:angular",
    "PhysicsJointStateAPI:angular",
    "PhysxJointAPI"
  ],
  "definedIn": "usd",
  "name": "UR10+ur10+base_link+shoulder_pan_joint",
  "parentObject": "UsdPrim/UR10%2Bur10%2Bbase_link+terminusdb%3A%2F%2F%2Fschema%23UsdSpecifier%2FSpecifierDef",
  "path": "/ur10/base_link/shoulder_pan_joint",
  "relationships": [
    "UsdRelationship/UR10%2Bur10%2Bbase_link%2Bshoulder_pan_joint%2Bphysics%3Abody0",
    "UsdRelationship/UR10%2Bur10%2Bbase_link%2Bshoulder_pan_joint%2Bphysics%3Abody1"
  ],
  "segmentName": "shoulder_pan_joint",
  "specializesName": "shoulder_pan_joint",
  "specifier": "SpecifierDef",
  "typeName": "PhysicsRevoluteJoint",
  "@graph": [
    {
      "@id": "JointState/shoulder_pan_joint+now",
      "@type": "JointState",
      "count": 1,
      "first": "now",
      "hasJointEffort": 0.11,
      "hasJointPosition": 0.22,
      "hasJointVelocity": 0.33,
      "last": "now",
      "name": "shoulder_pan_joint",
      "parentObject": "UsdPrim/UR10%2Bur10%2Bbase_link%2Bshoulder_pan_joint+terminusdb%3A%2F%2F%2Fschema%23UsdSpecifier%2FSpecifierDef"
    }
  ]
}
```




### Use-case specific framing functions

Use-case specific functions are defined in user code in terms of the previous function primitives.

TODO: provide function set for the following questions. Note, the answers given in the following are early concepts only.

<!-- 
Give me all images after the insertion of all unsuccessful insertions for object A

note: image.insertion requires that camera and image instances are modeled with insertion.

Question: is 'A' a type or an instance of a type? i.e. a 'CartridgeHolder' or a specific CartridgeHolder instance named A?

 ``` findBy(object('CartidgeHolder, 'A')).findBy(insertion('success',0).uriSelectBy(insertion.image) ```

 Question: how are objects typed? as ```WorkItem```s of type  ```PenBody, PenCap, BodyLiner, CartridgeHolder, PistonRod```? 

 Give me the force profile for all insertions for all objects
 ``` findBy(insertion.all).uri(force-profile) ```

 Implies task:  select functions ```uriSelectBy, literalSelectBy```


Give me the force profile for all insertions for all objects.

``` findBy(insertion.all).uriSelectBy(insertion.force-profile) ```
	
Question: how is force profile defined? as the forces on the tool end effector during the insertion process?

Give me the force profile for all insertions for all objects at the end effector.
``` findBy(insertion.all).uriSelectBy(insertion.force-profile) ```

Give me all images of camera B and the force profile at the end effector after the insertion of all unsuccessful insertions for object A.
``` findBy(workItem.A).findBy(insertion.failure).uriSelectBy(cameraB.images, insertion.force-profile) ```

Show me all instances of the insertion where the force at the end effector was larger than 5 newtons.
``` findBy(insertion.all).findCondition(endEffector.force, '>', 5).literalSelectBy(insertion) ```

What the names of the different phases for task A.
    NB!: need to discuss modeling of this! Currently:

``` 
PenAssemblyTask:
    BinPickTask
    GraspTask
    GraspValidationTask
    PoseEstimationTask
    ProcessingTask
    InsertionTask
    InsertionInspectionTask
```
``` findBy(task.).literalSelect```


What tasks have been performed with object A.
	
Give me all the point clouds and objects poses where the objects expected grasp pose matches the in-hand pose for object A.
	

Give me all the point clouds and objects poses where the objects expected grasp pose is within a translation of 1 cm with the in-hand pose for object A.

Give me the complete information you have available for one instance of a false grasp for object A.
	

Give me all joint information at a frequency of one hour for robot A over the last five years.

Give me the timestamps each failed grasping.

How many times today were no pose estimations obtained on object A. 
	

User: Give me all the instances were the grasping resulted in imprecise poses.
System: Define imprecise poses.
User: Were the in-hand pose differs with the expected grasp pose with more than 5mm. 
	Are you asking for the ability to define pose tolerances for use in a query, and if so, 




``` 
   jointstate_1 = semantic.by_type('JointState')
   name_1 = semantic.by_name('elbow-joint')
   status_1 = semantic.by_predicate_value('status', 'failure')
   first_1 = semantic.by_predicate_condition('first', '>', t1)
   last_1 = semantic.by_predicate_condition('last', '<', t1)

   semantic.query(jointstate_1, name_1, status_1, first_1, last_1).select('JointState','hasJointForce')

   semantic.query_joint_force(name_1, status_1, first_1, last_1)
   
``` 
-->
