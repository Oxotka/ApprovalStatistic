#!/usr/bin/python3
# -*- coding: utf-8 -*-


import requests
from requests.auth import HTTPBasicAuth
import json
from datetime import datetime
import urllib
import urllib.parse
import re


def get_meetings_list(login, password):
    base_url = "http://calypso/do8/odata/standard.odata/Catalog_Мероприятия"
    odata_object_key_guid = "5d3fa5a3-5ac9-11e5-9f46-e61f135f2c6f"
    today = datetime.today()
    f = {
        "$filter": "ВидМероприятия_Key eq guid'{}' and year(ДатаНачала) eq {} and month(ДатаНачала) eq {} and day(ДатаНачала) eq {}".format(
            odata_object_key_guid, today.strftime("%Y"), today.strftime("%m"), today.strftime("%d")),
        "allowedOnly": "true",
        "$format": "json"}
    encoded = urllib.parse.urlencode(f).replace('+', '%20')
    credentials = HTTPBasicAuth(login.encode('utf-8'), password)
    url = "{}?{}".format(base_url, encoded)
    response = requests.get(url=url, auth=credentials,
                            allow_redirects=False, verify=False).text
    meetings = json.loads(response)
    meetings_list = []
    jira_base = "https://abderus.dept07/jira/browse"
    for meeting in meetings.get('value'):
        if meeting['DeletionMark']:
            continue
        f = {"$format": "json"}
        project_name = None
        project_url = None
        stage = None
        for addinfo in meeting.get('ДополнительныеРеквизиты'):

            if addinfo.get('Свойство_Key') == "c8c16600-8138-11e5-9f46-e61f135f2c6f":

                check_ma = re.search(r'MA|ma', addinfo.get('Значение'))
                project_type = 'MA-' if check_ma is not None else 'EA-'
                project_number = re.search(r'\d{2,}', addinfo.get('Значение'))
                if project_number is not None:
                    project_name = "{}{}".format(project_type, project_number.group(0))
                    project_url = "{}/{}".format(jira_base, project_name)

            if addinfo.get('Свойство_Key') == "ae454c9c-878e-11e5-9f46-e61f135f2c6f":
                base_url = "http://calypso/do8/odata/Standard.ODATA/Catalog_ЗначенияСвойствОбъектов(guid%20'{}')".format(
                    addinfo.get('Значение'))
                encoded = urllib.parse.urlencode(f).replace('+', '%20')
                url = "{}?{}".format(base_url, encoded)
                response = requests.get(url=url, auth=credentials,
                                        allow_redirects=False, verify=False).text
                stage = json.loads(response).get('Description')

        base_url = "http://calypso/do8/odata/Standard.ODATA/Catalog_Пользователи(guid%20'{}')".format(
            meeting.get('Организатор'))
        encoded = urllib.parse.urlencode(f).replace('+', '%20')
        url = "{}?{}".format(base_url, encoded)
        response = requests.get(url=url, auth=credentials,
                                allow_redirects=False, verify=False).text

        instigator = json.loads(response).get('Description')
        instigator_email = json.loads(response).get('КонтактнаяИнформация')[0].get('АдресЭП')

        start_time = datetime.strptime(
            meeting.get('ДатаНачала'), '%Y-%m-%dT%H:%M:%S')
        finish_time = datetime.strptime(
            meeting.get('ДатаОкончания'), '%Y-%m-%dT%H:%M:%S')

        meeting_map = {"Name": meeting.get('Description'),
                       "Project_name": project_name,
                       "Project_url": project_url,
                       "Start": start_time.strftime("%H:%M"),
                       "Finish": finish_time.strftime("%H:%M"),
                       "Instigator": instigator,
                       "Instigator_email": instigator_email,
                       "Stage": stage}
        meetings_list.append(meeting_map)
    return meetings_list

def send_message(meeting):


def text_message(meeting):
    return """Привет, {name}.
    
    Сегодня проводилось согласование по проекту {project_name} в {start_time}.
    
    Как прошло согласование?
     
    
    
    
    """

for meeting in get_meetings_list():
    send_message(meeting)

