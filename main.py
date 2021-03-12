import os
import json
import time

import chardet
import requests
import textract

from bs4 import BeautifulSoup

from io import StringIO

from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser


DELAY_PER_REQUEST = 1 # seconds


# mitigates sentence segmentation
def get_pdf_text(document_path):
    output_string = StringIO()
    with open(document_path, 'rb') as in_file:
        parser = PDFParser(in_file)
        doc = PDFDocument(parser)
        rsrcmgr = PDFResourceManager()
        device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for page in PDFPage.create_pages(doc):
            interpreter.process_page(page)

    return output_string.getvalue()


def get_document(document_url, filename, year):
    req = requests.get(document_url, stream=True)
    chunk_size = 2000

    with open(f'docs/{year}/{filename}', 'wb') as fd:
        for chunk in req.iter_content(chunk_size):
            fd.write(chunk)

    document_text = textract.process(f'docs/{year}/{filename}')

    if filename.endswith('.pdf'):
        return get_pdf_text(f'docs/{year}/{filename}')

    return document_text.decode(chardet.detect(document_text)['encoding'])


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
    for year in [x for x in range(1995, 1996)]: # adjust as required
        if not os.path.exists(f'docs/{year}'):
            os.mkdir(f'docs/{year}') # expected later

        data[str(year)] = []

        base_url = f'http://www.saflii.org/za/cases/ZACC/{year}/'
        req = requests.get(base_url)
        soup = BeautifulSoup(req.text, 'html.parser')

        links = [link.get('href') for link in soup.find_all('a')]
        court_decision_urls = [base_url + link[8:] for link in links if link.startswith('../') and link.endswith('.html')]
        
        time.sleep(DELAY_PER_REQUEST)

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

            time.sleep(DELAY_PER_REQUEST)
            break # we just need sample data for now

    with open('data.json', 'w') as f:
       f.write(json.dumps(data))

    return data


if __name__ == '__main__':
    get_ml_data()