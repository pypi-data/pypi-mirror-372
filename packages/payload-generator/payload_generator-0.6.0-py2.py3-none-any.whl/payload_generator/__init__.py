"""
payload-generator

A package for generating payloads for sending to the Ingestion Gateway.
"""

__version__ = "0.6.0"
__author__ = 'Zeshan Khatri'
__credits__ = 'Qualtrics'

from faker import Faker
from importlib_resources import files, as_file
import random
import datetime
import uuid
import json
import math
import argparse

fake = Faker()
parser = argparse.ArgumentParser(prog="Payload Generator", description="Generate payloads to send to the Ingestion Gateway.")

parser.add_argument('-m', "--multi", action="store_true", required=False, help="Saves payload file based on project ID to make multi-project generation easier.")
parser.add_argument('-b', "--brand", type=str, required=False, help="Generates payloads based on the brand passed in (Humana or Centene). Default is generic")
parser.add_argument('-p', "--payload-type", type=str, required=False, help="Generates verbatims based on the payload type passed in (chat, call, or text).")
parser.add_argument('-v', "--version", action="version", version=f'%(prog)s {__version__}')
parser.add_argument("--no_ids", action="store_true", required=False, help="Creates payloads with no natural_id.")

parser.add_argument("count", metavar="Count", type=int,
                    help="the number of payloads to generate (integer)")
parser.add_argument("project_id", metavar="Project ID", type=int,
                    help="the project the payload is intended for")
parser.add_argument("folder", metavar="Destination Folder", type=str,
                    help="the folder the payload should be saved into")

args = parser.parse_args()

brand_values_file = files('payload_generator') / 'brand_values.json'
with as_file(brand_values_file) as file:
    brand_values = json.load(file.open())

natural_id = str(uuid.uuid4())
source = "XM Discover Link"

participants = [
    {
        "participant_id": 1,
        "type": "CLIENT",
        "gender": "UNKNOWN",
        "isBot": False,
        "speechRate": 0,
        "issueResolutionParticipantOutcome": "IR_PO_UNKNOWN",
        "empathyScore": 0,
        "attributes": {}
    },
    {
        "participant_id": 2,
        "type": "AGENT",
        "gender": "UNKNOWN",
        "isBot": False,
        "speechRate": 0,
        "issueResolutionParticipantOutcome": "IR_PO_UNKNOWN",
        "empathyScore": 0,
        "attributes": {}
    }
]

template = {
    "request_body" : {
        "uuid": None,
        "project_id": None,
        "document": {
            "attributes": {},
            "verbatims": [
                {
                    f"{args.payload_type or 'call'}": {
                        "body": {},
                        "source_system": source,
                        "allRelations": True,
                        "reasonEnabled": True,
                        "processingStage": "PROCESSING_STAGE_SYNTAX"
                    }
                }
            ],
            "natural_id": None,
            "source": source,
            "document_date": None,
        },
    }
}

def get_random_timestamp():
    start_datetime = datetime.datetime.strptime("2020-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
    end_datetime = datetime.datetime.today()
    
    time_diff = end_datetime - start_datetime
    random_seconds = random.randint(0, int(time_diff.total_seconds()))
    
    random_timestamp = start_datetime + datetime.timedelta(seconds=random_seconds)
    return random_timestamp.strftime("%Y-%m-%dT%H:%M:%S+0000")

current_time = datetime.datetime.today().strftime("%Y-%m-%dT%H:%M:%S+0000")

def set_attributes():
    allowed_letters = 'abcdefghijklmnpqrstuvwxyz' # used for bothify method

    if args.brand:
        attributes = brand_values[args.brand]["attributes"]

        # System attributes
        attributes['job_name'] = f'{args.brand}_Generated_Gatling'
        attributes['dnis'] = f'{fake.random_number(digits=10, fix_len=True)}'
        attributes['donedate'] = current_time
        attributes['loaddate'] = get_random_timestamp()
        attributes['cb_vtt_file_id'] = fake.bothify(text='%??%%?%?-%%%%-%??%-?%?%-?%%%%%%??%%%', letters=allowed_letters)

    if args.brand == "humana":
        attributes['acdid'] = fake.company().replace(" ", "_").replace("-", "_") + '_Prod'
        attributes['agentid'] = fake.company_email()
        attributes['agentname'] = fake.name()
        attributes['agentusername'] = f'CLB{fake.random_number(digits=4, fix_len=True)}'
        attributes['ani'] = f'{fake.random_number(digits=10, fix_len=True)}'
        attributes['callid'] = f'{fake.random_number(digits=9, fix_len=True)}'
        attributes['callstarttimeutc'] = get_random_timestamp()
        attributes['employee_id'] = f'{fake.random_number(digits=7, fix_len=True)}'
        attributes['externalcallid'] = attributes['ucid'] = fake.bothify(text='??%%%%%?-%???-%?%%-%%??-%?%%?%%%?%?%', letters=allowed_letters) # both reference same value
        attributes['feedback_provider'] = source
        attributes['hire_date'] = get_random_timestamp()
        attributes['job_name'] = attributes['job_name'] + '_Prod_Gen'
        attributes['level_1_name'] = fake.name()
        attributes['manager_level_1_name'] = fake.name()
        attributes['manager_level_2_name'] = fake.name()
        attributes['manager_level_3_name'] = fake.name()
        attributes['role'] = fake.job()
        attributes['vendor_name'] = fake.company()
    elif args.brand == "centene":
        npi = f'{fake.random_number(digits=9, fix_len=True)}'

        attributes['callid'] = natural_id
        attributes['customertelnumber'] = f'{fake.msisdn()[3:]}'
        attributes['emp_num'] = f'CN{fake.random_number(digits=6, fix_len=True)}'
        attributes['filename'] = f'{natural_id}_{get_random_timestamp()[:16]}_UTC.wav'
        attributes['ivrprovidernpi'] = npi
        attributes['job_name'] = attributes['job_name'] + '_Prod_XMLink'
        attributes['memberauthenticated'] = random.choice(['true', 'false'])
        attributes['omnicaseid'] = f'I-{fake.random_number(digits=9, fix_len=True)}'
        attributes['parentorguardianname'] = random.choice([' ', fake.name()])
        attributes['paymentdueflag'] = random.choice(['true', 'false'])
        attributes['planstate_v'] = fake.state_abbr(include_territories=False, include_freely_associated_states=False)
        attributes['providerauthenticated'] = random.choice(['true', 'false'])
        attributes['providerfullname'] = fake.name()
        attributes['providernpi'] = npi
        attributes['recording_end_time'] = get_random_timestamp()
    else:
        attributes = {
            "cb_interaction_type": "feedback",
            "cb_content_type": "contentful",
            "cb_content_subtype": "contentful",
            "cb_vtt_file_id": fake.bothify(text='%??%%?%?-%%%%-%??%-?%?%-?%%%%%%??%%%', letters=allowed_letters)
        }

    return attributes


def set_body(verbatim_count):
    body = {}
    sentences = generate_verbatims(count=verbatim_count)

    if args.payload_type == "text":
        return sentences # block of text
    else:
        if not args.payload_type or args.payload_type == "call":
            body.update({
                "total_silence": "13898",
                "total_dead_air": "11268",
                "total_overtalk": "42408",
                "total_hesitation": "0",
                "percent_silence": 0.037
            })
        body.update({
            "duration": "378049",
            "processingOpts": {
                "reason_enabled": True
            },
            "source_system": "aws-default",
            "special_events": [],
            "participants": participants,
            "segment_type": "SENTENCE",
            "segments": sentences # array of segments
        })
    return body



def generate_verbatims(count):
    sentence_source = files('payload_generator') / f'{args.brand}_sentences.txt' if args.brand else files('payload_generator') / 'sentences.txt'
    with as_file(sentence_source) as file:
        sentences = file.open().read().split('\n')

    if args.payload_type == "text": # text verbatims are just one big block of text
        return fake.sentence(nb_words=count, variable_nb_words=False, ext_word_list=sentences)

    segments = []
    start = fake.random_int(min=1000, max=2500) # random verbatim start timestamp

    for j in range(count):
        sentence = fake.sentence(nb_words=1, variable_nb_words=False, ext_word_list=sentences) # takes a random sentence from the source txt file
        end = start + fake.random_int(min=100, max=1500)
        verbatim = {
            "participant_id": (j % 2) + 1,
            "text": sentence,
            "start": start,
            "end": end
        }
        segments.append(verbatim)
        start = end

    return segments


def generate_payloads():    
    count=args.count
    project_id=f'{args.project_id}'
    folder=args.folder
    file_name=f'payload_{args.project_id}.json' if args.multi else "payload.json"

    with open(f'{folder}/{file_name}', 'w') as file:
        file.write('[')
        for i in range(1, count+1):
            request = template
            payload = request['request_body']
            document = payload['document']

            if args.no_ids:
                payload['uuid'] = "%s"
                payload['project_id'] = "%s"
                document['natural_id'] = "Gatling_Generated_%s"
            else:                
                payload['uuid'] = natural_id
                payload['project_id'] = project_id
                document['natural_id'] = f'Gatling_Generated_{natural_id}'
                document['document_date'] = current_time
            
            # Set attributes
            attributes = set_attributes()
            document['attributes'] = attributes

            verbatims = document['verbatims'][0][args.payload_type or "call"]

            # Set verbatim types based on brand
            if args.payload_type == "text":
                verbatims['verbatim_type'] = "unknownverbatim"
            elif args.brand:
                verbatims['verbatim_types'] = brand_values[args.brand]['verbatim_types']
            else:
                verbatims['verbatim_types'] = ["clientverbatim", "agentverbatim", "unknownverbatim"]

            # Set verbatim body (includes sentences/segments depending on payload type)
            payload_size = fake.random_int(min=25, max=300, step=25) # number of verbatims to generate
            verbatims['body'] = set_body(verbatim_count=payload_size)

            file.write(json.dumps(request))
            file.write(',' if i != count else '\n')

            if(count < 20): # to avoid making output too verbose
                print(f"Generated Payload {i} with {payload_size} verbatims")
        file.write(']')
    print(f'Generated array of {count} payloads of variable sizes in {folder}/{file_name}')
