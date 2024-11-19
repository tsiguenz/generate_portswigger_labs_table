#!/usr/bin/env python3

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
            is_solved = elem("span")[-1].text.strip() == "Solved"
            labs[current_category].append((name, url, level, is_solved))
    return labs


# def render_markdown_one_table(labs):
#     print("Render markdown...")
#     content = "# PORTSWIGGER LABS\n\n"
#     content += "|Category|Name|Level|Status|\n"
#     content += "|--------|----|-----|------|\n"
#     for category, labs_of_category in labs.items():
#         for lab in labs_of_category:
#             url = lab[1]
#             name = f"[{lab[0]}]({url})"
#             level = lab[2]
#             status = "✅" if lab[3] else "❌"
#             content += f"|{category}|{name}|{level}|{status}|\n"
#     return content


def get_stats(labs):
    stats = {}
    total_solved = 0
    total_nb_labs = 0
    for category, labs_by_cat in labs.items():
        # lab[3] is is_solved
        nb_solved = len([lab[3] for lab in labs_by_cat if lab[3]])
        nb_labs = len(labs_by_cat)
        total_solved += nb_solved
        total_nb_labs += nb_labs
        stats[category] = (nb_solved, nb_labs)
    stats["total"] = (total_solved, total_nb_labs)
    return stats


def render_markdown_one_table_by_category(labs):
    print("Render markdown...")
    stats = get_stats(labs)
    content = "# PORTSWIGGER LABS"
    content += f" ({stats["total"][0]}/{stats["total"][1]})\n\n"
    for category, labs_of_category in labs.items():
        content += f"## {category}"
        content += f" ({stats[category][0]}/{stats[category][1]})\n\n"
        content += "|Name|Level|Status|\n"
        content += "|----|-----|------|\n"
        for lab in labs_of_category:
            url = lab[1]
            name = f"[{lab[0]}]({url})"
            level = lab[2]
            status = "✅" if lab[3] else "❌"
            content += f"|{name}|{level}|{status}|\n"
        content += "\n"
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
        markdown = render_markdown_one_table_by_category(labs)
        write_content_to_file(markdown, sys.argv[3])
    except Exception as e:
        print(e)
        usage()
