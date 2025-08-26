# Editing Ontologies

## Current Implementation

TerminusDB uses JSON-LD as its RDF format for both storage and serialization of data. They have extended the syntax of JSON-LD using the ```@``` symbol (a common, but bad practice since this is a reserved symbol in JSON-LD).

We are currently using TerminusDB's schema definition language as our internal representation. TerminusDB supports a datalog known as WOQL that can be used for both insertion and queries and they support a document (JSON-LD) oriented schema definition that is their current prefered method. 

In our current implementation of a ***typed-client***, ontologies/schemas are defined in terms of custers, each cluster consisting of a set of type definitions that are imported as a package.

Users should be able to import a clusters and create their own clusters.  

Currently clusters from all projects are in a single mono-repo and are being split out into project repositories and distributed as NPM packages.

### Temporary use

Until the availability of NPM based clusters and library for handling clusters, users will have to use the NVIDIA Server for development.

Packages are managed under [```Rush```](https://rushstack.io/) which is used for handling all dependencies of the monorepo for typescript and javascript modules. 

Each cluster is a module and has it's own package/project defininition in the rush.json file that configures the repo. The following should be added to ```rush.json``` for ```fera-machine-tending-schema```:

```
    {
        "packageName": "fera-machine-tending-schema",
        "projectFolder": "types/fera-machine-tending-schema",
        "reviewCategory": "production"
    },
```

  - copy the directory ```/srv/workspace/services/types/fera-assembly-schema``` and change the name of the copied to ```fera-machine-tending-schema```.
  - change the file name under ```src/``` to ```feraMachineTendingSchema.ts```  and edit ```index.ts``` accordingly.
  - edit the package.json file for name changes, likewise the config/api-extractor.json file
  - rush update (to update dependencies in repo)
  - rush build  (to build repo)

###  Cluster definition

A cluster is defined as an array of ```clusterType``` where ```id```, ```cluster```, ```type```, ```version```, ```woql``` are required for schema definition.

```
        interface clusterType {
        /*  
            concept: clusterType is internal program representation (should) containing all data for generating 
            - woql (or other schema format)
            - stubs
            - visualizations
            - interoperability context/concordance data
            - dependencies are the other clusters where this types dependencies are to be found 
        */
        id: string,
        cluster: string,
        type: string,
        version: string,
        inScope?: boolean,
        woql?: any,
        graphviz?: any,
        children?: any, // { childName: clusterType [] }
        }
```

Example: 
```
        import { clusterType } from 'common-types';

        export const machineTendingCluster = (id): clusterType[] => ([

        // Situations
        {
            "id": id,
            "cluster": "machineTending",
            "type": "MachineTendingSituation",
            "version": "v001",
            "woql": {
            "@type": "Class",
            "@id": "MachineTendingSituation",
            "@documentation": {
                "@title": "MachineTendingSituation", "@description": " (version:v001)",
                "@authors": [""]
            },
            "@inherits": ["ProductionSituation"],
            "@key": { "@type": "Lexical", "@fields": ["name"] }
            }
        },
        ...
        ])
```
### Schema Definition

- import your cluster to ```services/types/schema-defs/src/schemaLibs.ts``` as ```{ machineTendingCluster } from 'machine-tending-schema';```
- Add an entry for your (```machineTending```) cluster to the schema ```fera``` in the following or create your new schema in ```schemaDefs```

```
    export const schemaDefs: SchemaMapDef[] = [
        { name: 'fera', version: 'v001', clusters: [ baseCluster, dulCluster, usdCluster, usdValueCluster, feraCluster, assemblyCluster ] } 
    ]
```
- use these ```name``` and ```version``` values when defining db 
- add an entry for your cluster and each type in ```clusterFormat``` of ```services/types/schema-defs/src/schemaLibs.ts``` 

### Design rules

See schemas under /types for example code and [reference](https://terminusdb.com/docs/schema-reference-guide/)
 - Schemas are defined as a set of clusters
 - A schema is built horizontally with a set of clusters that cover different dimensions
 - A schema is built vertically by refining types from parent clusters
 - Each cluster should be a layer that presents the user with a set of cohesive types
 - It is a good practice to define more narrow abstract types in your cluster rather than re-using wider parent types from other clusters
 - See the Fera cluster and the above as examples of applied ```DUL``` and ```fera``` types
 - the URI for an instance is defined by the db and returned as```@id``` according to the ```@key``` definition
 - Human readiable, i.e. lexical URIs are prefered and would be  ```@type/{name}``` in the above example where ```name``` shall be unique for a type
 - Note that the ```@fields``` array would include ```first``` for ```TemporalEntities``` to disambiguate by timestamps 
 - Abstract types are not instantiated, i.e. they have no instances or @key definitions for their @id
 - Abstract types are denoted by ```@abstract: []```
 

### Usage

A freshly started shell service requires a default schemaId set so that it knows what schema to operate on and which logical db instance to use.
You can have multiple db instances running that have the same or different schemas installed.

See define dbID in the following table to set the schemaId and db instance for whenever a shell is restarted. 

The format shall follow ```<schema name><schema version>-<instance name>``` where ```<schema name>``` and ```<schema version>``` follow from the (yours) approriate entry in ```services/types/schema-defs/src/schemaLibs.ts```


| General tasks | Command |
|:--- |:--- |
| build | ```rush build``` |
| tmux | ```tmux attach -t fc``` |
| stop/start shell | in ```services/services/fera-shell```  or the shell pane of tmux |
| run shell | ```rushx serve``` |
| client | in ```services/apps/semantic-client``` or client pane of tmux : ```rushx serve --help``` |
| view dbId | ```rushx serve -v``` |
| define dbId (*)| ```rushx serve -d <schema name><schema version>-<instance name> ```|

(*) required for all client-shell operations

| DB tasks | Command |
|:--- |:--- |
| create db instance for current dbId | ```rushx serve -c``` |
| insert schema for dbId in db | ```rushx serve -q``` |
| insert usd instances (**) | ```rushx serve -x ../../../../semantic-services/semantic_repo/libraries/usd_to_rdf/usd-files/json/ur10.json``` |

(**) requires that usd and usdValue are included in the schema definition


| Visualization tasks | Command |
|:--- |:--- |
| for the current schema graph clusters a, b, and c (***)| ```rushx serve -g a b c``` |
| show parent dependencies | ```rushx serve -e true``` |
| show cluster boundaries | ```rushx serve -b true``` |

(***) generated .svg files are placed in ```/srv/workspace/artifacts```

 