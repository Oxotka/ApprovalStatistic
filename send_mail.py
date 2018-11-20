#!/usr/bin/python3
# -*- coding: utf-8 -*-
import requests
from requests.auth import HTTPBasicAuth
import json
from datetime import datetime
import urllib
import urllib.parse
import smtplib
import re
from textwrap import dedent
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header


def get_meetings_list(base_url, login, password):
    catalog_url = "Catalog_Мероприятия"
    odata_object_key_guid = "5d3fa5a3-5ac9-11e5-9f46-e61f135f2c6f"
    today = datetime.today()
    f = {
        "$filter": "ВидМероприятия_Key eq guid'{}' and year(ДатаНачала) eq {} and month(ДатаНачала) eq {} and day(ДатаНачала) eq {}".format(
            odata_object_key_guid, today.strftime("%Y"), today.strftime("%m"), today.strftime("%d")),
        "allowedOnly": "true",
        "$format": "json"}
    encoded = urllib.parse.urlencode(f).replace('+', '%20')
    credentials = HTTPBasicAuth(login.encode('utf-8'), password)
    url = "{}/{}?{}".format(base_url, catalog_url, encoded)
    response = requests.get(url=url, auth=credentials,
                            allow_redirects=False, verify=False).text
    meetings = json.loads(response)
    meetings_list = []
    jira_base = "https://abderus.dept07/jira/browse"
    project_url = None
    for meeting in meetings.get('value'):
        if meeting['DeletionMark']:
            continue

        for addinfo in meeting.get('ДополнительныеРеквизиты'):
            if addinfo.get('Свойство_Key') == "c8c16600-8138-11e5-9f46-e61f135f2c6f":
                check_ma = re.search(r'MA|ma', addinfo.get('Значение'))
                project_type = 'MA-' if check_ma is not None else 'EA-'
                project_number = re.search(r'\d{2,}', addinfo.get('Значение'))
                if project_number is not None:
                    project_name = "{}{}".format(project_type, project_number.group(0))
                    project_url = "{}/{}".format(jira_base, project_name)

        url_user = "{}/Catalog_Пользователи(guid%20'{}')".format(base_url, meeting.get('Организатор'))
        encoded = urllib.parse.urlencode(f).replace('+', '%20')
        url = "{}?{}".format(url_user, encoded)
        response = requests.get(url=url, auth=credentials,
                                allow_redirects=False, verify=False).text

        instigator = json.loads(response).get('Description')
        instigator_email = json.loads(response).get('КонтактнаяИнформация')[0].get('АдресЭП')

        start_time = datetime.strptime(
            meeting.get('ДатаНачала'), '%Y-%m-%dT%H:%M:%S')
        finish_time = datetime.strptime(
            meeting.get('ДатаОкончания'), '%Y-%m-%dT%H:%M:%S')

        meeting_map = {"Name": meeting.get('Description'),
                       "Start": start_time.strftime("%H:%M"),
                       "Finish": finish_time.strftime("%H:%M"),
                       "Instigator": instigator,
                       "Instigator_email": instigator_email,
                       "Project_url": project_url}
        meetings_list.append(meeting_map)
    return meetings_list


def template_letter(meeting):

    template = dedent('''\
               <html><body>
               Привет, {username}.
               <br>
               <br>Сегодня проводилось согласование по проекту <a href="{project_url}">{project_name}</a> в {start_time}.
               <br>
               <br>Как прошло согласование?
               <br><a href="{approve}">Согласовано</a>
               &nbsp&nbsp&nbsp&nbsp&nbsp
               <a href="{don_t_approve}">Не согласовано</a>
               &nbsp&nbsp&nbsp&nbsp&nbsp
               <a href="{don_t_know}">Ни к чему не пришли</a>
               <br>
               <br><b>Согласовано</b> - если совещание прошло эффективно и приняли решение. 
               <br><b>Не согласовано</b> - если все было эффективно, но решение до конца не принято. 
               <br><b>Ни к чему не пришли</b> - если совещание прошло не эффективно и никакого результата нет.
               В этом случае опишите, что на Ваш взгляд пошло не так.
               </html></body>''')

    url = 'http://localhost:8080'
    return template.format(
        username=name(meeting.get('Instigator')),
        project_name=meeting.get('Name'),
        start_time=meeting.get('Start'),
        approve=get_approve(url, meeting, True),
        don_t_approve=get_approve(url, meeting, False),
        don_t_know=get_don_t_know(url, meeting),
        project_url=meeting.get('project_url'))


def get_approve(url, meeting, result):
    return '{url}/add_vote?project={project}&author={name}&result={result}&date={start}&project_url={project_url}'.format(
        url=url,
        project=meeting.get('Name').replace("\"", ""),
        name=meeting.get('Instigator'),
        start=meeting.get('Start'),
        result=result,
        project_url=meeting.get("Project_url"))


def get_don_t_know(url, meeting):
    return '{url}/add_comment?project={project}&author={name}&date={start}&project_url={project_url}'.format(
        url=url,
        project=meeting.get('Name').replace("\"", ""),
        name=meeting.get('Instigator'),
        start=meeting.get('Start'),
        project_url=meeting.get("Project_url"))


def name(author):
    fio = author.split(" ")
    if len(fio) > 1:
        return fio[1]  # Считаем, что имя всегда идет вторым
    else:
        return author['name']


def send_message(from_email, from_name, meeting):

    from_full_name = '{from_name} <{from_email}>'.format(from_name=from_name, from_email=from_email)
    to_email = from_email
    # to_email = meeting.get('Instigator_email')

    mail_coding = 'windows-1251'
    multi_msg = MIMEMultipart()
    multi_msg['From'] = from_full_name
    multi_msg['To'] = to_email
    multi_msg['Subject'] = Header('Как прошло согласование?', mail_coding)

    text_msg = template_letter(meeting)

    msg = MIMEText(text_msg.encode('cp1251'), 'html', mail_coding)
    msg.set_charset(mail_coding)
    multi_msg.attach(msg)

    # Отправка письма
    server = smtplib.SMTP('relay.1c.ru', port=25)
    server.sendmail(from_email, to_email, multi_msg.as_string())
    server.quit()


login = ''
password = ''
from_email = ''
from_name = ''
base_url = ''

for meeting in get_meetings_list(base_url, login, password):
    print(meeting)
    send_message(from_email, from_name, meeting)

