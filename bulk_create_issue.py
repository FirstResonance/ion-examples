import csv
from subprocess import call
from getapikey import get_access_token, call_api
import requests
import json
from urllib.parse import urljoin

API_URL = 'https://api.buildwithion.com'
AUTHENTICATION_SERVER = 'auth.buildwithion.com'

file = open('issuesa.csv')
csvreader = csv.reader(file)

rows = []
for row in csvreader:
    rows.append(row)

file.close()

CREATE_ISSUE_MUTATION = '''
mutation CreateIssue($input:CreateIssueInput!)
{
    createIssue(input:$input)
    {
        issue
        {
        id
        causeCondition
    }
    }
}
'''


access_token = get_access_token()

for row in rows:
     
    call_api(CREATE_ISSUE_MUTATION,{"input":{"partInventoryId":row[0],"causeCondition":[ {  "children": [ { "type": "p",  "children": [ { "text": row[1]  } ]   }   ]  } ]}},access_token)
