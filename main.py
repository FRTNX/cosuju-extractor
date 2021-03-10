import requests
import time
import pprint
from bs4 import BeautifulSoup

pp = pprint.PrettyPrinter(indent=4)

DELAY_PER_REQUEST = 2 # seconds

def get_ml_data():
    data = {}
    for year in [x for x in range(1995, 1996)]: # adjust as required
        url = f'http://www.saflii.org/za/cases/ZACC/{year}/'
        req = requests.get(url)
        soup = BeautifulSoup(req.text, 'html.parser')

        links = [link.get('href') for link in soup.find_all('a')]
        court_decision_urls = [url + link[8:] for link in links if link.startswith('../') and link.endswith('.html')]

        data[str(year)] = []
        # time.sleep(DELAY_PER_REQUEST)

        for decision_url in court_decision_urls:
            req = requests.get(decision_url)
            decision_soup = BeautifulSoup(req.text, 'html.parser')
            summary_url, judgement_url = find_document_urls(url, decision_soup)

            data[str(year)].append({
                'title': decision_soup.title,
                'url': decision_url,
                'summary_document_url': summary_url,
                'judgement_document_url': judgement_url
            })

            pp.pprint(data)
            # time.sleep(DELAY_PER_REQUEST)

    return data


def find_document_urls(base_url, soup):
    links = [link.get('href') for link in soup.find_all('a')]

    summary_url = [link for link in links if link.endswith('media.pdf')]
    judgement_url = [link for link in links if link.endswith('.pdf') and 'media' not in link]

    if len(summary_url) == 0:
        summary_url = [link for link in links if link.endswith('media.rtf')]

    if len(judgement_url) == 0:
        judgement_url = [link for link in links if link.endswith('.rtf') and 'media' not in link]

    summary_url = base_url + summary_url[0][20:] if len(summary_url) > 0 else ''
    judgement_url = base_url + judgement_url[0][20:] if len(judgement_url) > 0 else ''

    return [summary_url, judgement_url]


if __name__ == '__main__':
    get_ml_data()
