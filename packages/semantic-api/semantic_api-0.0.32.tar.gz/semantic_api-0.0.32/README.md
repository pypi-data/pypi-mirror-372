
# Semantic API

#### Versions

```0.0.32``` : Intial version with only the API for insertion and query.

| Feature | Element | Status | Comment |
|:--- |:--- |:--- | :--- |
| semantic data insertion capability | |✅ | complete |
| semantic data query capability | |✅ | complete |
| documentation of semantic and semantic.client methods and functions |  | ❌  | in-process |
| typelib |  | ❌  | in-process |
| type tools | |❌ | in-process |
| database tools | | minimum added in 22 | in-process |
| chain tools  | |❌ | in-process | 


### Install

```pip3 install semantic-api```

### Use

#### Import
```
from semantic.api.semantic_api import semantic
from semantic.common.utils import defineSchemaId
from semantic.api.config import brokerIP, dbUri, batch_size
```


#### Schema context configuration

An ontology is assumed to built from a set of ontology clusters and identified by a ```schemaName```, and a ```schemaVersion```.

This ```schemaName-schemaVersion``` pair defines a schema instance in the database which is further identified by ```instanceName``` since it is common  practice to have multiple logical instances in the database for the same ontology.

The function ```defineSchemaId(schemaName, schemaVersion, instanceName, dbUri)``` from ```semantic.common.utils```defines and instance of the type ```SchemaID``` that is used to bind with the semantic context in the database. 

The extra ```dbUri``` parameter provides the domain information of the schema and data and the ```JSON-LD``` ```@context``` that is returned in queries.

The Semantic API shall be instantiated before using api.narration or api.chain methods as these require a connection to the MQTT broker. Note that a database with the ```schemaName-schemaVersion-instanceName``` is assumed to be running along with a semantic service (out of scope of this project).

```
api = semantic( brokerIp, defineSchemaId(schemaName, schemaVersion, instanceName, dbUri), batch_size
```

| Parameter | Use | Suggestion |
|:--- |:--- |:--- |
| brokerIP | MQTT Broker IP | use remote broker for project, default from config is 'localhost' |
| schemaName | identifying name for schema | according to defined schemas |
| schemaVersion | schema version | according to defined schemas|
| instanceName | database instance for schemaName-schemaVersion | suggest user defined instance assuming this has been created and instantiated with schema |
| dbUri | db IP:port URI | use default from config defined as 'http://127.0.0.1:6363/'|
                                      

#### Database client

The API supports a lower level database client ```semantic.client```that is useful for database configuration tasks. Currently, only two methods are exposed on ```client``` but will be filled out and adequately documented to match the current service API. A commnand line version of this client libary will also be provided as the command line is more useful for maintenance than programtic use, as per the current node.js based semantic-client.


| semantic.client methods | return |
|:--- |:--- |
| ```getSchemaId()``` |  ```SchemaID``` instance in service |
| ```setSchemaId(schemaName, schemaVersion, instanceName)``` | sets ```SchemaId``` instance (assumning current ```dBUri```)|


The following section describes the usage of the API.

#### 1 [Semantic API](src/doc/python-api.md)

#### 2 [Background](src/doc/background.md)

#### 3 [RDF and Types](src/doc/rdf-and-types.md)

#### 4 [Editing Ontologies](src/doc/editing-ontologies.md)




