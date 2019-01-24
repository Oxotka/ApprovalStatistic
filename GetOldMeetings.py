#!/usr/bin/python3
# -*- coding: utf-8 -*-
import requests
from requests.auth import HTTPBasicAuth
import json
from datetime import datetime
import urllib
import urllib.parse
import re


def get_meetings_list(base_url, login, password, skip, top):
    catalog_url = "Catalog_Мероприятия"
    odata_object_key_guid = "5d3fa5a3-5ac9-11e5-9f46-e61f135f2c6f"
    f = {
        "$orderby": "ДатаНачала",
        "$top": str(top),
        "$skip": str(skip),
        "$filter": "ВидМероприятия_Key eq guid'{}'".format(
            odata_object_key_guid),
        "allowedOnly": "true",
        "$format": "json"}
    encoded = urllib.parse.urlencode(f).replace('+', '%20')
    credentials = HTTPBasicAuth(login.encode('utf-8'), password)
    url = "{}/{}?{}".format(base_url, catalog_url, encoded)
    response = requests.get(url=url, auth=credentials,
                            allow_redirects=False, verify=False).text
    meetings = json.loads(response)
    meetings_list = []
    for meeting in meetings.get('value'):
        if meeting['DeletionMark']:
            continue

        stage = ''
        project_name = ''
        for addinfo in meeting.get('ДополнительныеРеквизиты'):
            if addinfo.get('Свойство_Key') == "c8c16600-8138-11e5-9f46-e61f135f2c6f":
                check_ma = re.search(r'MA|ma', addinfo.get('Значение'))
                project_type = 'MA-' if check_ma is not None else 'EA-'
                project_number = re.search(r'\d{2,}', addinfo.get('Значение'))
                if project_number is not None:
                    project_name = "{}{}".format(project_type, project_number.group(0))

            if addinfo.get('Свойство_Key') == "ae454c9c-878e-11e5-9f46-e61f135f2c6f":
                catalog_url = "Catalog_ЗначенияСвойствОбъектов(guid%20'{}')".format(
                    addinfo.get('Значение'))
                encoded = urllib.parse.urlencode(f).replace('+', '%20')
                url = "{}/{}?{}".format(base_url, catalog_url, encoded)
                response = requests.get(url=url, auth=credentials,
                                        allow_redirects=False, verify=False).text
                stage = json.loads(response).get('Description')

        url_user = "{}/Catalog_Пользователи(guid%20'{}')".format(base_url, meeting.get('Организатор'))
        encoded = urllib.parse.urlencode(f).replace('+', '%20')
        url = "{}?{}".format(url_user, encoded)
        response = requests.get(url=url, auth=credentials,
                                allow_redirects=False, verify=False).text

        instigator = json.loads(response).get('Description')
        start_time = datetime.strptime(
            meeting.get('ДатаНачала'), '%Y-%m-%dT%H:%M:%S')

        meeting_map = {"Name": meeting.get('Description'),
                       "Date": str(start_time),
                       "Stage": stage,
                       "Instigator": instigator,
                       "Project_name": project_name}
        meetings_list.append(meeting_map)
    return meetings_list


def add_to_file(filename, name, project, stage, author, date):
    text = "{name};{project};{stage};{author};{date}".format(
        name=name,project=project, stage=stage, author=author, date=date)
    with open(filename, 'a') as file:
        file.write(text + '\n')


login = ''
password = ''
base_url = ''
filename = 'old_stat.txt'

skip = 0
top = 250
end_list = False
while not end_list:
    meeting_list = get_meetings_list(base_url, login, password, skip, top)
    for meeting in meeting_list:
        add_to_file(
            filename,
            name=meeting.get('Name'),
            project=meeting.get('Project_name'),
            stage=meeting.get('Stage'),
            author=meeting.get('Instigator'),
            date=meeting.get('Date'))

    len_meeting = len(meeting_list)
    end_list = (len_meeting == 0)
    print('Обработано {}'.format(skip + len_meeting))
    skip = skip + top


