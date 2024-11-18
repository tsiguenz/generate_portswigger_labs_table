#!/bin/python3

import sys
import requests
from bs4 import BeautifulSoup, Tag

def usage():
    print("Usage: python3 generate_portswigger_labs_table.py <SessionId> <Authenticated_UserVerificationId> <output file>")
    print("The arguments are the respective cookies in your browser when you are authenticated.")

def get_all_labs_html_from_portswigger():
    print("Get all labs in html from portswigger...")
    sessionId = sys.argv[1]
    authenticated_UserVerificationId = sys.argv[2]
    cookies = {
        'SessionId': sessionId,
        'Authenticated_UserVerificationId': authenticated_UserVerificationId,
    }
    return requests.get(portswigger_url + '/web-security/all-labs', cookies=cookies)


def get_labs_dict_from_soup(soup):
    print("Get labs dict from html...")
    all_labs_div = soup.find(id="all-labs")
    all_labs = all_labs_div.children
    current_category = ""
    labs = {}
    for elem in all_labs:
        if not isinstance(elem, Tag):
            continue
        if elem.name == "h2":
            current_category = elem.string
            labs[current_category] = []
        if elem.name == "div":
            name = elem.div.a.text.strip()
            url = portswigger_url + elem.div.a.attrs['href'].strip()
            level = elem.div.span.text.strip()
            status = elem("span")[-1].text.strip()
            labs[current_category].append((name, url, level, status))
    return labs


def render_markdown(labs):
    print("Render markdown...")
    content = "# PORTSWIGGER LABS\n\n"
    content += "|Category|Name|Level|Status|\n"
    content += "|--------|----|-----|------|\n"
    for category, labs_of_category in labs.items():
        for lab in labs_of_category:
            url = lab[1]
            name = f"[{lab[0]}]({url})"
            level = lab[2]
            solved = lab[3]
            content += f"|{category}|{name}|{level}|{solved}|\n"
    return content


def write_content_to_file(content, filename):
    print(f"Write content to file \"{filename}\"...")
    with open(filename, 'w') as f:
        f.write(content)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        usage()
        exit(1)
    portswigger_url = "https://portswigger.net"
    output_filename = sys.argv[3]
    try:
        response = get_all_labs_html_from_portswigger()
        soup = BeautifulSoup(response.text, "html.parser")
        labs = get_labs_dict_from_soup(soup)
        markdown = render_markdown(labs)
        write_content_to_file(markdown, sys.argv[3])
    except Exception as e:
        print(e)
        usage()
