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


DELAY_PER_REQUEST = 0 # seconds


# mitigates sentence segmentation
def get_pdf_text(document_path):
    output_string = StringIO()

    with open(document_path, 'rb') as in_file:
        pdf_parser = PDFParser(in_file)
        pdf_docunent = PDFDocument(pdf_parser)
        resource_mgr = PDFResourceManager()
        device = TextConverter(resource_mgr, output_string, laparams=LAParams())
        interpreter = PDFPageInterpreter(resource_mgr, device)

        for page in PDFPage.create_pages(pdf_docunent):
            interpreter.process_page(page)

    return output_string.getvalue()


def get_document(document_url, filename, year):
    file_path = f'docs/{year}/{filename}'

    if not os.path.exists(file_path):
        req = requests.get(document_url, stream=True)
        chunk_size = 2000

        with open(file_path, 'wb') as pdf_file:
            for chunk in req.iter_content(chunk_size):
                pdf_file.write(chunk)
    else:
        print(f'Document already exists: {file_path}')


    if filename.endswith('.pdf'):
        return get_pdf_text(file_path)

    document_text = textract.process(file_path)
    return document_text.decode(chardet.detect(document_text)['encoding'])


def get_decision_documents(base_url, soup, year):
    summary_document, judgement_document = [None, None]

    links = [link.get('href') for link in soup.find_all('a')]

    # remove error throwing None values
    filtered_links = [link for link in links if link != None]

    summary_endpoint = [link for link in filtered_links if link.endswith('media.pdf')]
    judgement_endpoint = [link for link in filtered_links if link.endswith('.pdf') and 'media' not in link]

    if len(summary_endpoint) == 0:
        summary_endpoint = [link for link in filtered_links if link.endswith('media.rtf')]

    if len(judgement_endpoint) == 0:
        judgement_endpoint = [link for link in filtered_links if link.endswith('.rtf') and 'media' not in link]

    summary_file_url = base_url + summary_endpoint[0][20:] if len(summary_endpoint) > 0 else ''
    judgement_file_url = base_url + judgement_endpoint[0][20:] if len(judgement_endpoint) > 0 else ''

    if (summary_file_url):
        summary_filename = f'summary-for-case-{summary_file_url[41:]}'.replace('media.pdf', '.pdf')
        summary_document = {
            'filename': summary_filename,
            'file_url': summary_file_url,
            'file_content': get_document(summary_file_url, summary_filename, year)
        }

    if (judgement_file_url):
        judgement_filename = f'judgement-for-case-{judgement_file_url[41:]}'
        judgement_document = {
            'filename': judgement_filename,
            'file_url': judgement_file_url,
            'file_content': get_document(judgement_file_url, judgement_filename, year)
        }

    return [summary_document, judgement_document]


def get_ml_data():
    data = {}
    for year in [x for x in range(1995, 2023)]: # adjust as required
        print(f'Beginning extraction for {year}')
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
            try:
                print(f'Extracting documents for {decision_url}')
                req = requests.get(decision_url)
                decision_soup = BeautifulSoup(req.text, 'html.parser')
                summary_document, judgement_document = get_decision_documents(base_url, decision_soup, year)

                data[str(year)].append({
                    'title': decision_soup.title.text,
                    'url': decision_url,
                    'summary_document': summary_document,
                    'judgement_document': judgement_document
                })

                print(f'Extracted documents for {decision_url}')
                time.sleep(DELAY_PER_REQUEST)

            except Exception as e:
                print(e)
                pass

    with open('data.json', 'w') as f:
       f.write(json.dumps(data))

    return data


if __name__ == '__main__':
    get_ml_data()