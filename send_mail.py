#!/usr/bin/python3
# -*- coding: utf-8 -*-

import requests


def send_mail(project, author, result):
    requests.get('http://localhost:8080/add_vote?pr={project}&author={author}&result={result}'.format(
        project=project, author=author, result=result))


send_mail('EA-9677', 'tasha', True)
send_mail('EA-1231', 'pchel', False)
