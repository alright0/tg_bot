import re


def clean_html(text):
    replace_closed_tags = re.compile('</.*?>')
    delete_all_tags = re.compile('<.*?>')

    text = re.sub (replace_closed_tags, '\n', text)
    return re.sub(delete_all_tags, '', text)

