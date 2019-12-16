#!/usr/bin/python3
# -*- coding: utf-8 -*-
import cherrypy
import pymongo
import datetime


def add_vote_to_log(filename, project, author, value, comment, date, stage, task_id):
    text = "{project};{author};{value};{comment};{date};{stage};{task_id}".format(
        project=project, author=author, value=value, comment=comment, date=date, stage=stage, task_id=task_id)
    with open(filename, 'a', encoding='utf-8') as file:
        file.write(text + '\n')


def add_vote_to_db(project, task_id, author, email, value, comment, date, stage):
    client = pymongo.MongoClient("", )
    db = client.tasker
    date_str = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    exist_vote = db.votes.find_one({'date': date_str})
    if exist_vote is None:
        db.votes.insert_one({
            'task': project,
            'author': author,
            'value': value,
            'comment': comment,
            'date': date_str,
            'task_id': task_id,
            'email': email,
            'stage': stage
            })


def html_form():
    return """<html>
          <head>Опишите, что пошло не так в согласовании</head>
          <body>
            <br>
            Это позволит сделать процессы согласования лучше!
            <br>
            <form method="get" action="add_vote">
              <input type="hidden" name="author" value="{author}">
              <input type="hidden" name="email" value="{email}">
              <input type="hidden" value="{project}" name="project">
              <input type="hidden" value="{project_url}" name="project_url">
              <input type="hidden" value="{stage}" name="stage">
              <input type="hidden" value="{task_id}" name="task_id">
              <div>
              Проект: <a href="{project_url}">{project}</a>
              <input type="hidden" value="{date}" name="date">
              </div>
              <p><p>
              <div>
              Комментарий:<input type="text" value="" name="comment" placeholder="Что пошло не так?" size=100/>
              <br>
              <button type="submit">Отправить в лог</button>
              </div>
            </form>
          </body>
        </html>"""


class VoteCollector(object):

    @cherrypy.expose
    def add_vote(self, project, author, date, comment='None', result='None', project_url='', stage='', task_id='', email=''):
        add_vote_to_log('log.txt', project, author, result, comment, date, stage, task_id)
        add_vote_to_db(project, task_id, author, email, result, comment, date, stage)
        return '''<h1 style="color: #5e9ca0;"><span style="color: #000000;">Спасибо, голос учтен!</span></h1>
        <p>Опишите результаты согласования здесь - <a href="{project_url}">{project}</a>&nbsp;</p>'''.format(
            project=project, project_url=project_url)

    @cherrypy.expose
    def add_comment(self, project='', author='', date='', project_url='', stage='', task_id='', email=''):
        return html_form().format(project=project,
                                  author=author,
                                  date=date,
                                  project_url=project_url,
                                  stage=stage,
                                  task_id=task_id,
                                  email=email)


if __name__ == '__main__':
    cherrypy.quickstart(VoteCollector(), config='server.cfg')
