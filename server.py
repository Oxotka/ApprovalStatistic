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
              <div>
              Проект:<input readonly="readonly" value="{project}" name="project" size=50>
              <input type="hidden" value="{date}" name="date">
              </div>
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
    def add_vote(self, project, author, date, comment='None', result='None'):
        add_vote_to_log('log.txt', project, author, result, comment, date)
        return 'Спасибо, голос учтен!'

    @cherrypy.expose
    def add_comment(self, project='', author='', date=''):
        return html_form().format(project=project, author=author, date=date)


if __name__ == '__main__':
    cherrypy.quickstart(VoteCollector(), config='server.cfg')
