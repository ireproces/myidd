# Remove all HTML tags from a given string

import re

def clean_html(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    cleantext = cleantext.replace('\n', ' ').replace('\r', ' ')
    cleantext = cleantext.strip()
    return cleantext