import copy
from typing_extensions import Final
from utils import msg
from common_types import PipeArg

'''
    status: this is a port-in-progress from ts. Andreas' filter should be scanned for comparison
            object style makes it less useful, need filter for chain/pipe application

    system options:

        narration client --> temporalFilter service --> semanticShell --> db

        temporalFilter can be hosted in a pipe:
            1) as shown in ts
            2) as shown in python
            3) embedded in narration client
            4) embedded in semanticShell
        
        1) is probably the best as it leaves the client/user out of the problem
        2) allows the client/user to handle performance issues
        3) offload to thread while narration is ongoing is a good idea, except w.r.t load effects
        4) single point of loading limits bandwidth
        
    1) is target ==> this port on hold
'''


async def publishMsgOnChange(args: PipeArg):
    '''
        preconditions:
                    either object or aray

        publish ROS1 and MQTT on change for TemporalEntities (TE)s, note type dependencies:
        TemporalEntity properties not to diff
        publish on change current TemporalEntity to ROS1 
        update previous TemporalEntity (ref) last with current first
        publish on change to DB the previous TemporalEntity that was constant up to this event 
        TE ref is not inserted into db until a change has occurred, thus it has complete info
        with first, last, count updated as part of the TE processing
        nb: count will be used in the TE @id to ensure uniqueness (rather than timestamp) which is not present under processing
    '''
    msg('publishMsgOnChange')

    result: PipeArg = copy.deepcopy(args)
    docs = [args.doc] if isinstance(args.doc, list) else args.doc
    '''
    generate SensedOccupancy Type for the any

    pre-conditions:
                    current data as array or object
    rising_edge is a current change that marks an event
    falling_edge is the last (ref) static data prior to the change
    post-conditions:
                      as array or object:
                      real-time effect of publishing rising_edge change
                      return falling_edge
    '''
    falling_edge: list[any] = []
    rising_edge: list[any] = []

    async for doc in docs:

        current = doc
        ref: str

        id: Final = emulateLexicalId(current['@type'], current.name)

        if (stateProxy.exists(id)):
            ref = stateProxy.getState(id)
            current.count = ref.count 
            
            stateProxy.setState(id, current)                                                                                                                                
        else:
            current.count = 0
            stateProxy.setInitialState(id, current)
            ref = current
        
        haveCompleteInfo: Final = (exists(current) && exists(ref))
        threshold: Final = current.threshold

        if (haveCompleteInfo):

            '''
                NB!  Type dependency in the following line  can be factored out
            '''

            const { isEqual: noChange, change: haveChange } = (current['@type'] === 'UbiLocation') ?
                objectIsEqual(ref, current, ['timeStamp', 'first', 'last', 'count', 'threshold', 'variance'], threshold) :
                objectIsEqual(ref, current, ['timeStamp', 'first', 'last', 'count', 'threshold'], threshold)
            const stateMsg = (noChange) ? chalk.blue(`no state change: no publishing (updated ref.last)`) : chalk.green(`state change since last sample: publishing`)
            // trc('publishMsgOnChange', stateMsg)

            '''
                NB!  Type dependency in the following line !!!
            '''
            if (noChange):
                if (exists(ref.method) && ref.method === 'CumulativeMovingAverage'):
                    ref.point.x = (current.point.x + ref.count * ref.point.x) / (ref.count + 1)
                    ref.point.y = (current.point.y + ref.count * ref.point.y) / (ref.count + 1)
                    ref.point.z = (current.point.z + ref.count * ref.point.z) / (ref.count + 1)
                
                ''' no change, update ref.last to current.first '''
                ref.last = exists(current.first) ? current.first : DateTime.now()
                ''' no change, update sample count '''
                ref.count = ref.count + 1

                #trc('publishMsgOnChange', chalk.blue(`nochange: current: ${JSON.stringify(current, null, 2)} `))
                #trc('publishMsgOnChange', chalk.blue(`nochange: ref ${JSON.stringify(ref, null, 2)} `))

            
                stateProxy.setState(id, ref)
            
            else:
              try:

                # trc('publishMsgOnChange', `current: ${JSON.stringify(current, null, 2)} `)
                # trc('publishMsgOnChange', `ref ${JSON.stringify(ref, null, 2)} `)
                '''
                    identifier is the uniqueness index of a type/name pair used to create a unique id
                    count is the number of 'equal' samples for a unique data instance
                    nb: name is modified here only on insertion into db, as it is only here that we have the uniqueness index
                    this means that diff map and values are operating on non unique names (of course, since that is how we determine uniqueness)
                '''
                
                identifier: Final = stateProxy.incrementInstanceIndex(id)
                trc('publishMsgOnChange', `identifier: ${identifier} `)

                # change: set current count to 0, assume first is current time stamp
                current.count = 0

               
                stateProxy.setState(id, current)

                '''
                    return reference, i.e. previous change set (not current change) in DB
                    for external insertion in db
                    ROS msg is critical path, db isn't
                '''
                # ref.name = `${ref.name}_${identifier}`
                ref.index = identifier
                falling_edge = [...falling_edge, ref]
                rising_edge = [...rising_edge, current]

                #trc('publishMsgOnChange', chalk.green(`change: current: ${JSON.stringify(current, null, 2)} `))
                #trc('publishMsgOnChange', chalk.green(`change: ref ${JSON.stringify(ref, null, 2)} `))
                
              except Exception as e:
                txt = f'semantic_client: insert : Exception: {e}'
                redMsg(txt)
                err('publishMsgOnChange', `Error: ${error.stack} `)
        
        else:
            err('publishMsgOnChange', chalk.red('the current or reference object does not exist which implies a dropped data sample'))
            

    trc('publishMsgOnChange', ` rising_edge  ${JSON.stringify(rising_edge, null, 2)} `)
    trc('publishMsgOnChange', ` falling_edge  ${JSON.stringify(falling_edge, null, 2)} `)
    result.doc = (rising_edge.length == 1) ? rising_edge[0] : rising_edge

    ''' client pipe publishes change(s) to db after ros is published here in returned result'''
    currentDocInPipe: Final = insertDocInPipe((falling_edge.length == 1) ? falling_edge[0] : falling_edge)

    result = await pipeline(result, ros1Msg, ros1PublisherInArgs, currentDocInPipe)


    now: Final = DateTime.now().toUTC().toISO()
    trc('publishMshOnChange', chalk.green(`after publishing ROS: ${JSON.stringify(now, null, 2)}`))

    #¤trc('publishMsgOnChange', ` result.doc ${JSON.stringify(result.doc, null, 2)} `)
    trcO('publishMsgOnChange')
    return result
