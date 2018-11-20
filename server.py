#!/usr/bin/python3
# -*- coding: utf-8 -*-
import cherrypy


def add_vote_to_log(filename, project, author, value, comment, date):
    text = "{project};{author};{value};{comment};{date}".format(
        project=project, author=author, value=value, comment=comment, date=date)
    with open(filename, 'a') as file:
        file.write(text + '\n')


def html_form():
    return """<html>
          <head>Опишите, что пошло не так в согласовании</head>
          <body>
            <br>
            Это позволит сделать процессы согласования лучше!
            <br>
            <form method="get" action="add_vote">
              <input type="hidden" name="author" value="{author}">
              <input type="hidden" value="{project}" name="project">
              <input type="hidden" value="{project_url}" name="project_url">
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
    def add_vote(self, project, author, date, comment='None', result='None', project_url=''):
        add_vote_to_log('log.txt', project, author, result, comment, date)
        return '''<h1 style="color: #5e9ca0;"><span style="color: #000000;">Спасибо, голос учтен!</span></h1>
        <p>Опишите результаты согласования здесь - <a href="{project_url}">{project}</a>&nbsp;</p>'''.format(
            project=project, project_url=project_url)

    @cherrypy.expose
    def add_comment(self, project='', author='', date='', project_url=''):
        return html_form().format(project=project, author=author, date=date, project_url=project_url)


if __name__ == '__main__':
    cherrypy.quickstart(VoteCollector(), config='server.cfg')
