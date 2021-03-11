import os

import requests
import textract
import pprint

import json
import time
from bs4 import BeautifulSoup

pp = pprint.PrettyPrinter(indent=4)

DELAY_PER_REQUEST = 2 # seconds


def get_document(document_url, filename, year):
    req = requests.get(document_url, stream=True)
    chunk_size = 2000

    with open(f'docs/{year}/{filename}', 'wb') as fd:
        for chunk in req.iter_content(chunk_size):
            fd.write(chunk)

    textract.process(f'docs/{year}/{filename}').decode('ascii')


def get_decision_documents(base_url, soup, year):
    summary_document, judgement_document = [None, None]

    links = [link.get('href') for link in soup.find_all('a')]

    summary_endpoint = [link for link in links if link.endswith('media.pdf')]
    judgement_endpoint = [link for link in links if link.endswith('.pdf') and 'media' not in link]

    if len(summary_endpoint) == 0:
        summary_endpoint = [link for link in links if link.endswith('media.rtf')]

    if len(judgement_endpoint) == 0:
        judgement_endpoint = [link for link in links if link.endswith('.rtf') and 'media' not in link]

    summary_file_url = base_url + summary_endpoint[0][20:] if len(summary_endpoint) > 0 else ''
    judgement_file_url = base_url + judgement_endpoint[0][20:] if len(judgement_endpoint) > 0 else ''

    if (summary_file_url):
        summary_filename = summary_file_url[41:]
        summary_document = {
            'filename': summary_filename,
            'file_url': summary_file_url,
            'file_content': get_document(summary_file_url, summary_filename, year)
        }

    if (judgement_file_url):
        judgement_filename = judgement_file_url[41:]
        judgement_document = {
            'filename': judgement_filename,
            'file_url': judgement_file_url,
            'file_content': get_document(judgement_file_url, judgement_filename, year)
        }

    return [summary_document, judgement_document]


def get_ml_data():
    data = {}
    for year in [x for x in range(1995, 1998)]: # adjust as required
        if not os.path.exists(f'docs/{year}'):
            os.mkdir(f'docs/{year}') # expected later

        base_url = f'http://www.saflii.org/za/cases/ZACC/{year}/'
        req = requests.get(base_url)
        soup = BeautifulSoup(req.text, 'html.parser')

        links = [link.get('href') for link in soup.find_all('a')]
        court_decision_urls = [base_url + link[8:] for link in links if link.startswith('../') and link.endswith('.html')]

        data[str(year)] = []
        # time.sleep(DELAY_PER_REQUEST)

        for decision_url in court_decision_urls:
            req = requests.get(decision_url)
            decision_soup = BeautifulSoup(req.text, 'html.parser')
            summary_document, judgement_document = get_decision_documents(base_url, decision_soup, year)

            data[str(year)].append({
                'title': decision_soup.title.text,
                'url': decision_url,
                'summary_document': summary_document,
                'judgement_document': judgement_document
            })

            print(data)
            # time.sleep(DELAY_PER_REQUEST)

            break # we just need sample data for now

    with open('data.json', 'w') as f:
       f.write(json.dumps(data))

    return data


if __name__ == '__main__':
    get_ml_data()