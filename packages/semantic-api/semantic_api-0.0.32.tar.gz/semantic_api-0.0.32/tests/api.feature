Feature: python semantic API
  As a robotics programmer
  I want to insert and query semantic data
  So that I can use semantic data from python for my research

  Scenario: construct an insert
     Given we have a semantic instance for a schema
      When we narrate with a JointState instance
      Then check that what we get out is what we expect

  Scenario: serialize an insert
     Given we have constructed an insert
      When we serialize the insert
      Then we check that the serializations match

  Scenario: multiple inserts
     Given we narrate a second instance
      When we serialize all the inserts
      Then we check we got it all

   Scenario: insert the array of flattened typeMap to the db
     Given we have a connection to the semantic service and can define a schema on it

   Scenario: we have a USD model in the db for more realistic tests
      Given we have a semantic usd representation of a ur robot in the db where we can get the name for the shoulder_pan_joint
         Then we can verify that our usdPathMap works as well
         Then we can emulate the terminusdb insertion reference (terminus object uri format) for the joint object and validate that the ref matches the expected
         Then we use a type constructor and narrate
         Then we flatten the cached semantic data in the typeMap, insert it into the db, and check that the instance we query for, matches what we inserted
         Then we clear the map

   Scenario: we work with ToolCenterPointState
      Given we use the ToolCenterPointState type constructor and narrate
      Then we use the simplest means of fetching a parent ref
   
   
   Scenario: we chain functionality
      Given we construct a pipeline
      Then we chain a query
      Then we embed a query in the middle of the pipe
      Then we use a user-defined function in the pipe
      Then we test query_constructor and query function

   
   Scenario: narration of data loads and resulting insertion batching, map clearing, and map cycling
      Given we narrate a data stream