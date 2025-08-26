from typing_extensions import Final
import json
from semantic.common.utils import msg


'''
    set batch_size to ~samples/sec 

'''

batch_size = 100

schemaName: str = 'fera' 
schemaVersion: str = 'v001'
instanceName: str = 'jan2025'
dbUri: str = 'http://127.0.0.1:6363/'

brokerIp: Final = 'localhost'
port: Final = 1883
username: Final = 'semantic'
password: Final = 's3mant1c'

#deprecate following
#publishTopic: Final = 'fcs/serviceRequestTopic'
#insertAcknowledgeTopic: Final = 'insertAcknowledgeTopic'

'''
#semantic_config_topic_suffix: Final ='fcs/semanticConfig'
config_request_topic_suffix: Final ='configRequest'
#semantic_configResponseTopic_suffix: Final ='fcs/semanticConfigResponse'
config_response_topic_suffix: Final ='configResponse'
#serviceRequestTopic: Final ='fcs/serviceRequestTopic'
service_request_topic_suffix: Final ='serviceRequest'
#serviceResponseTopic: Final ='fcs/serviceResponseTopic'
service_response_topic_suffix: Final ='serviceResponse'
topics: Final = [semanticConfigResponseTopic, serviceResponseTopic]
'''
