#!/usr/bin/python3
# -*- coding: utf-8 -*-


import requests
from requests.auth import HTTPBasicAuth
import json
from datetime import datetime
import urllib
import urllib.parse
import re
import smtplib
from textwrap import dedent
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

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


def template_letter(username='Уважаемый', log='', what=''):

    template = dedent('''\
               Здравствуйте, {username}.
                              
               GitLab CI говорит, что при закладке в хранилище:
               
               {log}
               
               Вероятно этому есть разумное объяснение:
               "Возможно, {what_happened}"
               
               Но лучше поскорее во всем разобраться.
               Спасибо за внимание и чудесного дня!''')

    return template.format(username=username, log=log, what_happened=what_happened(what))


def subject(happened='Что-то пошло не так'):

    return random_item(list_subject()).format(happened=happened.capitalize())


def random_item(items):
    return items[random.randint(0, len(items) - 1)]


def what_happened(happened):

    what_happened = random_item(list_reasons()).format(happened=happened.lower())
    return what_happened[0].lower() + what_happened[1:]


def name(author):
    fio = author['name'].split(" ")
    if len(fio) > 1:
        return fio[1]  # Считаем, что имя всегда идет вторым
    else:
        return author['name']


def send_message(author, log):

    happened = 'Найдена ошибка'
    mail_coding = 'windows-1251'

    multi_msg = MIMEMultipart()
    multi_msg['From'] = 'GitLab CI <gitbp@1c.ru>'
    multi_msg['To'] = author['email']
    multi_msg['Subject'] = Header(subject(happened), mail_coding)

    text_msg = template_letter(name(author), log, happened)

    msg = MIMEText(text_msg.encode('cp1251'), 'plain', mail_coding)
    msg.set_charset(mail_coding)
    multi_msg.attach(msg)

    # Отправка письма
    server = smtplib.SMTP('relay.1c.ru', port=25)
    server.sendmail("gitbp@1c.ru", author['email'], multi_msg.as_string())
    server.quit()


def text_message(meeting):
    return """Привет, {name}.
    
    Сегодня проводилось согласование по проекту {project_name} в {start_time}.
    
    Как прошло согласование?
     
    
    
    
    """

for meeting in get_meetings_list():
    send_message(meeting)

