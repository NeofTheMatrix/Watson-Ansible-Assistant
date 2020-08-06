import json
import time
import re
import slack
import configparser
import time
import threading
import logging
from ibm_watson import AssistantV1
from ibm_watson import AssistantV2
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import ApiException
from W2A.IterateAnsible import IterateAnsible


# Get config params ---------------------------------------------------------------
config = configparser.ConfigParser()
config.read('w2a.cfg')

# Logging config ------------------------------------------------------------------
logging.basicConfig(filename=config['W2A']['FILE_LOG'], level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

# create logger
logger = logging.getLogger('')
ch = logging.StreamHandler()
logger.addHandler(ch)

logger.info('(i) IBM Watson Ansible Assistant: Starting...')

# Set Watson ----------------------------------------------------------------------
assistantID = config['WATSON']['ASSISTANT_ID']
sessionID = None
authenticator = IAMAuthenticator(config['WATSON']['IAM_AUTHENTICATOR'])
working = False

assistantv1 = AssistantV1(
    version='2019-02-28',
    authenticator = authenticator
)
assistantv2 = AssistantV2(
    version='2019-02-28',
    authenticator=authenticator
)

assistantv1.set_service_url(config['WATSON']['SERVICE_URL'])
assistantv2.set_service_url(config['WATSON']['SERVICE_URL'])
#assistantv1.set_disable_ssl_verification(True)
#assistantv2.set_disable_ssl_verification(True)

# Create a session Watson service -------------------------------------------------
logger.info('(i) IBM Watson Ansible Assistant: Creating Watson session...')

response = assistantv2.create_session(
    assistant_id=assistantID
).get_result()

sessionID = response['session_id']


# Get alls playbooks ---------------------------------------------------------------
playbooks_dirs = [config['ANSIBLE']['PLAYBOOKS_DIR']]
i = 1
while True:
	Dir = config['ANSIBLE'].get('PLAYBOOKS_DIR'+str(i))
	if Dir:
		playbooks_dirs.append(config['ANSIBLE']['PLAYBOOKS_DIR'+str(i)])
		i+=1
	else:
		break

iterateAnsible = IterateAnsible(
	assistantv1, 
	config['WATSON']['WORKSPACE_ID'],
	playbooks_dirs,
    config['ANSIBLE']['VAULT_PASS_FILE']
)

# Update data of playbooks in Watson Assistant ------------------------------------
iterateAnsible.updatePlaybooksInEntities()


# Send message to Watson Assistant ------------------------------------------------
def sendWatsonMessage(msgUser):
    try:
        response = assistantv2.message(
            assistant_id=assistantID,
            session_id=sessionID,
            input={
                'message_type': 'text',
                'text': msgUser
            }
        ).get_result()

        return response
    
    except ApiException as ex:
        logger.error('(X) main.sendWatsonMessage: Method failed with status code ' + str(ex.code) + ': ' + ex.message)


def keepSessActive():       # <- Keep the session active of IBM Watson
    while True:
        if not working:
            sendWatsonMessage('hello')
        time.sleep(240)


# Get Slack events ----------------------------------------------------------------
@slack.RTMClient.run_on(event='message')
def Slack_event(**payload):
    try:
        data = payload['data']
        web_client = payload['web_client']
        rtm_client = payload['rtm_client']

        channel_id = data['channel']
        thread_ts = data['ts']
        user = data.get('user', [])
        msgUser = data.get('text', [])

        if user: # <- Para no generar un bucle infinito de eventos, un feedback
            working  = True
            response = sendWatsonMessage(msgUser)
            if 'suggestions' in response["output"]["generic"][0]:  # <- If return suggestions, not undertanded the request of the user
                response = sendWatsonMessage('Sugg')
                web_client.chat_postMessage(
                    channel=channel_id,
                    text="<@%s> %s" % (user, response["output"]["generic"][0]["text"])
                )
            else:
                for res in response["output"]["generic"]:
                    web_client.chat_postMessage(
                        channel=channel_id,
                        text="<@%s> %s" % (user, res["text"])
                        #thread_ts=thread_ts # <- Con esto responde el mensaje en un nuevo hilo
                    )

                result = iterateAnsible.execute(response, user)
                if result:
                    response = sendWatsonMessage(result['msg'])
    
                    web_client.chat_postMessage(
                        channel=channel_id,
                        text='<@%s> %s:\n```%s```' % (user, response["output"]["generic"][0]["text"], result['Ansible_result'])
                    )
            working = False
    except Exception as e:
        logger.error('(X) main.Slack_event: Method failed with status code ' + str(type(e).__name__ ) + ': '+ str(e))


#slack_token = os.environ["SLACK_API_TOKEN"]
slack_token = config['SLACK']['TOKEN']
rtm_client = slack.RTMClient(token=slack_token)
logging.info('(i) IBM Watson Ansible Assistant is Running.')
t1 = threading.Thread(target=keepSessActive)
t1.start()
rtm_client.start()


