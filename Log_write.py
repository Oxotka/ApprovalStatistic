
def add_vote(filename, project, author, value, comment):
    text = "{project};{author};{value};{comment}".format(project=project, author=author, value=value, comment=comment)
    with open(filename, 'a') as file:
        file.write(text + '\n')


add_vote('log.txt', 'EA-9677', 'arin', 'true', '')
add_vote('log.txt', 'EA-9677', 'arin', 'false', '')
add_vote('log.txt', 'EA-9677', 'arin', 'bad', 'because!!')
