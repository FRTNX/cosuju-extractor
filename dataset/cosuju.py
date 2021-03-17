# coding=utf-8

"""COSUJU: The Court Summaries and Judgements Dataset."""

from __future__ import absolute_import, division, print_function

import json

import datasets


logger = datasets.logging.get_logger(__name__)


_CITATION = """\
@InProceedings{huggingface:dataset,
title   = {CoSuJu 500+ Court Judegements and Summaries for Machine Text Summarization},
authors = {Busani Ndlovu, Luke Jordan},
year    = {2021}
}
"""

# TODO: Complete description
_DESCRIPTION = """\
Court Summaries and Judgements (CoSuJu)
"""

# Redundant but may useful in future.
_URL = 'https://github.com/FRTNX/ml-data-scraper/blob/main/dataset/'
_URLS = {
    'train': _URL + 'mini-train-v1.0.json'
}


class CosujuConfig(datasets.BuilderConfig):
    """BuilderConfig for COSUJU."""

    def __init__(self, **kwargs):
        """BuilderConfig for COSUJU.
        Args:
          **kwargs: keyword arguments forwarded to super.
        """
        super(CosujuConfig, self).__init__(**kwargs)


class Cosuju(datasets.GeneratorBasedBuilder):
    """COSUJU: The Court Summaries and Judgements Dataset. Version 1.0.0"""

    VERSION = datasets.Version("1.0.0")

    # Allows configuration to be chosen at run time
    # data = datasets.load_dataset('my_dataset', 'include_no_summary')
    # data = datasets.load_dataset('my_dataset', 'exclude_no_summary')
    BUILDER_CONFIGS = [
        datasets.BuilderConfig(name="include_no_summary", version=VERSION, description="Includes rows with no summary documents"),
        datasets.BuilderConfig(name="exclude_no_summary", version=VERSION, description="Excludes rows with no summary documents"),
    ]

    DEFAULT_CONFIG_NAME = 'exclude_no_summary'

    def _info(self):
        return datasets.DatasetInfo(
            description=_DESCRIPTION,
            features=datasets.Features(
                {
                    'id': datasets.Value('string'),
                    'title': datasets.Value('string'),
                    'url': datasets.Value('string'),
                    'year': datasets.Value('string'),
                    'update_date': datasets.Value('string'),
                    'summary_document': {
                            'filename': datasets.Value('string'),
                            'file_url': datasets.Value('string'),
                            'file_content': datasets.Value('string')
                        },
                    'judgement_document': {
                        'filename': datasets.Value('string'),
                        'file_url': datasets.Value('string'),
                        'file_content': datasets.Value('string')
                    },
            }
            ),
            supervised_keys=None,
            homepage='https://huggingface.co/datasets/FRTNX/cosuju',
            citation=_CITATION,
        )

    def _split_generators(self, dl_manager):
        downloaded_files = dl_manager.download_and_extract(_URLS)

        return [
            datasets.SplitGenerator(name=datasets.Split.TRAIN, gen_kwargs={'filepath': downloaded_files['train']}),
        ]

    def _generate_examples(self, filepath):
        """This function returns the examples in the raw (text) form."""
        logger.info('generating examples from = %s', filepath)
        with open('train-v1.0.json', 'r') as f:
            cosuju = json.loads(f.read())
            for row in cosuju['data']:
                if self.config.name == 'exclude_no_summary':
                    if not row['summary_document']:
                        continue

                    if type(row['summary_document']) == dict and \
                        row['summary_document']['file_content'] == '':
                        continue

                id_ = row['id']
                result = {
                    'id': row['id'],
                    'title': row['title'],
                    'url': row['url'],
                    'year': row['year'],
                    'update_date': row['update_date']
                }

                # This is to keep things feature compliant
                for prop in ['summary_document', 'judgement_document']:
                    if row[prop]:
                        result[prop] = row[prop]
                    else:
                        result[prop] = { 'filename': '', 'file_url': '', 'file_content': '' }
                    
                yield id_, result
