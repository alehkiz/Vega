from bs4 import BeautifulSoup

def process_html(text):
    html = BeautifulSoup(text, 'html.parser')

    # add class blockquote to a html
    # TODO enhancement a way implement a iterate
    [x.attrs.__setitem__('class', 'blockquote') for x in html.findAll('blockquote')]

    return html


def replace_newline_with_br(text:str):
    return text.replace('\n', '<br>')
    