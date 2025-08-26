 
# Querying USD

Semantic graphs are queried by formulating nested json-ld frame objects that are specific to a given semantic data schema (ontology).\
The pattern matching capability of the query forumlated as an object frame is realized through the match of the properties of the frame with the semantic data instances in the database.\
A property key is the predicate of a triple, and it's value is either a literal type or an object type.\
Each nested object represents a node in a graph such that a graph with n linkage hops (currently) requires n object frame definitions.\(

The outer object and it's inner objects (including reverse objects) represents one large ***AND*** query, i.e it will only be satisfied iff all sub-objects match.\\

Ususually, the exact nature of a graph is not known and therefore ***OR*** logic is requried. However, this ***OR*** logic is not currently implemented and a sequence of muliple frames is recommended rather than the future array of ***OR'd*** frames.

The URI of the subject (@id) and the object URI c)an be used for exact matches, i.e. an explicit lookup.

A frame with an object defined with an empty object will act as a wild card for the predicate as no constraints are defined.

## Implications of child-centric linkage

All USD objects are linked from child to parent for reasons of performance and scalability.\
This is in contrast with the USD API that is formulated with parent centric linkage with a / separated path definition to define the containment hierarchy in the parent-child nesting.

### Reverse framing for parent-child graphs

The USD parent to child nesting format can be achieved by using the standard JSON-LD Framing @reverse formulation.
```
{
    <parent (subject) predicate to literal> : <literal pattern>,
    <parent (subject) predicate to object> : <object pattern>
}
```
The object type in forward subject-predicate-object triples is defined by a single concrete or abstract type in the schema (ontology).\
However, the subject type in a reverse object-predicate-subject frame may be of different types.\
This is the case of the predicate parentObject in UsdObject that points to a UsdObject or its derivations of UsdStage, UsdPrim, UsdAttribute, or UsdRelationship.\
An array of matches to cover the different subject types may be required to match the parent subject.


### Forward framing for child-parent graphs

```
{
    <parent (subject) predicate to literal> : <literal pattern>,
    <parent (subject) predicate to object> : <object pattern>
    "@reverse" : {
            <child (object) predicate> : [
                <child literal pattern>,
                <child object pattern>
            ]
    }
}
```


## Scene Root

### Scene Root from defaultPrim


### Forward framing of Scene Root
Match Frame:
 - with type ```UsdStage```
 - with name ```UR10-truncated```
 - with any and all child Prims that are pointing to this ```parentObject```
```
 {
      "@type": "UsdStage",
      "name": "UR10-truncated",
      "@reverse": {
                    "parentObject" : [ {"@type": "UsdPrim"} ]
                  }
}
```

The same for all ```UsdObject``` pointing to this ```parentObject```

```
 {
      "@type": "UsdStage",
      "name": "UR10-truncated",
      "@reverse": {
                    "parentObject" : [ {"@type": "UsdObject"} ]
                  }
}
```


The following queries for the ```UsdStage/UR10-truncated``` instance with a graph of children of any type that are referencing their parent through the childs's predicate ```parentObject``` ***AND*** recsusively for a total of 4 levels of nested children.\

The frame only matches for UsdObjects and UsdPrims that have both leaf objects ***AND*** nested objects for 4 levels.

The frame could be further specified with specific types and properties if needed.\

```
{
    "@type": "UsdStage",
    "name": "UR10-truncated",
    "@reverse": {
        "parentObject": [
            {},
            {
                "@reverse": {
                    "parentObject": [
                        {},
                        {
                            "@reverse": {
                                "parentObject": [
                                    {},
                                    {
                                        "@reverse": {
                                            "parentObject": [
                                                {}
                                            ]
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
        ]
    }
}
```

Nesting can continue at the risk of a match failure, better to walk the tree in the client code rather than in a non ***OR'd*** frame.



## Data-centric query 

The reverse formulation is required to get parent-child view given the child-to-parent linkage. 

In other words, the reverse frame formulation is required to get a response in the form of:

```
{
  "@type": "Parent",
  "@id": "Parent/parent_name",
  ...,
  "@graph" : [ {"@type": "Child1", ...},... {"@type": "ChildN", ...} ]
}
```

A forward frame formulation results in a data- or child- centric response in the form of:

{
  "@type": "Child",
  ...,
  "parentObject": "Parent/parent_name"
  "@graph" : [ {"@type": "Parent", ...} ]
}

The data centric child formulation of attributes on their prims, specify name 
 
```
{
  "@type": "UsdAttribute",
  "parentObject" : {}
}
```
To get the attributes on the second level
```
{
  "@type": "UsdAttribute",
  "parentObject" : { 
    "parentObject" : {}
  }
}
```
