#! /usr/bin/python

import requests
import json
import os
import csv


radarendpointurl = 'https://radar.wandera.com'
radarusername = '<Your Radar Admin Username>'
radarpassword = '<Your Radar PW'
childaccountid = '<Customer ID for Portal>'
path_to_csv = '/Path/To/Results/csv/GetBlockPolicy.csv'

# do not modify the below
noauthheaders = {'Accept': 'application/json, text/javascript, */*; q=0.01', 'Content-Type': 'application/json'}

radararray = []
radartoken = ''
categoriesDict = {}
displayNameDict = {}


def loadradar():
    print('Attempting to login to Radar with ' + radarusername + ' user.')
    loadcredentialsurl = radarendpointurl + '/auth/getToken'
    try:
        r = requests.post(loadcredentialsurl, headers=noauthheaders,
                          data='{"username":"' + radarusername + '","password":"' + radarpassword + '"}')
    except:
        print('Error logging into Radar API')
        os._exit(1)

    if (r.text.startswith('{"code"')):
        print('Error logging into Radar API')
        os._exit(1)
    responsejson = json.loads(r.text)
    token = (responsejson['token'])
    global radartoken
    radartoken = 'Bearer ' + token
    checkpermissionsurl = radarendpointurl + '/api/admins/me'

    authdheaders = {'Accept': 'application/json, text/javascript, */*; q=0.01', 'Content-Type': 'application/json',
                    'Authorization': radartoken}
    me = requests.get(checkpermissionsurl, headers=authdheaders)
    # print me.text
    responsejson = json.loads(me.text)
    parent = (responsejson['user']['isParent'])

    if (parent):
        print('Account is parent account - logging in as child account id ' + childaccountid)
        try:
            loadcredentialschildurl = radarendpointurl + '/api/token'
            r = requests.put(loadcredentialschildurl, headers=authdheaders,
                             data='{"customerId":"' + childaccountid + '"}')
        except:
            print('Error logging into Radar API - elevate permissions to child account. Check child account id')
            os._exit(1)
        responsejson = json.loads(r.text)
        token = (responsejson['token'])
        radartoken = 'Bearer ' + token

    print('Got RADAR credentials')


def GetBlockCategories():

    print('Attempting to export block categories info from RADAR')
    get_block_categories_url = radarendpointurl + '/gate/content-block-service/v1/rules/simple-view?customerId=' + childaccountid
    # print radartoken
    authdheaders = {'Accept': 'application/json, text/javascript, */*; q=0.01', 'Content-Type': 'application/json',
                    'Authorization': radartoken}
    try:
        r = requests.get(get_block_categories_url, headers=authdheaders)

    except:
        print('Error getting device export')
        os._exit(1)

    responsejson = json.loads(r.text)

    for i in responsejson:
        categoriesDict[i['id']] = i['categoryName']
        displayNameDict[i['id']] = i['displayName']


def GetBlockPolicy():

    print('Attempting to get block policy info from RADAR')
    get_block_policy_url = radarendpointurl + '/gate/policy-service/v1/customers/' + childaccountid + '/block-policy'

    authdheaders = {'Accept': 'application/json, text/javascript, */*; q=0.01', 'Content-Type': 'application/json',
                    'Authorization': radartoken}
    try:
        r = requests.get(get_block_policy_url, headers=authdheaders)

    except:
        print('Error getting device export')
        os._exit(1)

    responsejson = json.loads(r.text)

    f = open(path_to_csv,'a')
    writer = csv.writer(f)
    header = ['Category', 'SubCategory', 'Policy', 'Inherited Policy']
    writer.writerow(header)

    for i in responsejson['rules']:
        row = [categoriesDict.get(str(i['id'])), displayNameDict.get(str(i['id'])), i['actions'], i['inheritedActions']]
        writer.writerow(row)

    print('CSV Export completed')

if __name__ == "__main__":
    loadradar()
    GetBlockCategories()
    GetBlockPolicy()
