
## 1 Background

The semantic-api assumes that the user is concerned with the ontological modeling and subequent programatic use in systems rather than the semantic-web representation of the system. The difference is subtle, but significant, as the concerns of system wide exploitation of a taxonomy used to define the system are different than that of an interface to a semantic-web application. 

The system-wide defintion of types is assumed to be a requirement in the following, with the exposure to the semantic-web as secondary to client and system services usage.

In the ideal case, all aspects of the sytem are staticlly typed such that the ontology serves as a system wide definition that the compiler checks at build time on every signature and return type.

In the worst case, the data types are only validated on insertion to the database for programming languages with little or no type support.

The central postulate of the author is that modeling is a infinite task that implies continuous change to type definitions throughout the system. The approach taken here, is not to resist type change through standardization, or containment to an API or external interfaces,  but to assume and embrace type change through the system programming. 

The central postulate is that an ontolgogicaly defined system requires an environment that supports type change and that this is best achieved with system libraries that are compliled for the ontologies at hand. Statically typed languages are the obvious choice under these requirements but this type centric approach should be maintained for non-statically-typed languages such as Python.

In all cases, the type definitions for the ontology should be local such that code generation is available to the programmer. This can be realized via the native type definitions of statically type languages, definition language for schemas or ontolgies, a DSL for types, or a combination of paths.  Regardless of the means, some form of definition becomes the internal representation that results in compiled type definitions to allow for type validation, code generation, and reasoning. This can be thought of as a ***typed-client*** analogous to a ***thick-client*** where services (in this case types) are available directly on the client.

Versioning shall be applied such that type evolution can be discerned at the type, cluster, and schema levels.

The following documents the current state of this development from the user's point of view.


### 1.1 Context

The context for this effort is formed by a set of observations or ***postulates***:

 - ***types are the symbolic representations of the system (vocabulary, taxonomy, langauge model)***
 - ***the inter-dependence of system types forms a graph of types which we call an ontology***
 - ***system design and inteface design starts with types***
 - ***these types define the semantics of the system, i.e. form a model of the system***
 - ***specific instances of types are what we call semantic data***
 - ***a function is defined by the mapping between the type of its argument and its return type***
 - ***modeling of the world (system) is an infinite task since our concerns and the world are both continuously changing***
 - ***we need to be able to easily handle the evolution and change of our world models (ontologies)***
 - ***system wide types have a positive effect on the development and the subsequent quality of the system***
 - ***we need to be able to handle the evolution and change of our program types***
 - ***the complexity of programing with semantic data, i.e. defining, creating, querying, formatting, and processing of semantic data is limiting exploitation***
 - ***programming with semantic data (on graphs of type instances) is poorly developed in light of its potential***
 

### 1.2 Goals

The goal is to enable semantic techologies to be exploited in projects. This envolves simplifying:

 - the definition, selection, and layering of ontologies
 - the creation of semantic data
 - the querying, formatting, and processing of semantic data
 

Furthermore, It is an implied requirement is that any semantic middleware, or configuration detail, is kept out of the user's functional, in-band, or business logic.
 

### 1.3 Use and Exploitation Potential

System wide ontologies and local programming with types are expeced to be exploited in:
 - code quality: ensuring instance data is correct at run-time (as well as development and compile time correctness)
 - metadata: model higher level environmental contexts, use-cases, configuration, scenarios, tasks, agents, actors, not just entities, behaviour, and actions
 - state machines: state machine states and events as types
 - observability: full semantic coverage of system and sub-system states and errors
 - availability: provide clients with the list of the current actions/operations that a user can make for the current service/error state (HATEOAS)
 - controllability: model the full plant and control space with parameter, error, and noise effects
 - modeling: address the extra dimensions of concern that are not modeled
 - temporality: model the temporal dimension so that all captured semantic data is unique and represents an event
 - policies: exploit events by using ontologically defined conditions on policy agents
 - reasoning: exploit reasoning on types and type properties to create knowledge bases
 - empirical models: use bottom up techniques, both classical and machine learning techniques to validate if not inform symbolic types

