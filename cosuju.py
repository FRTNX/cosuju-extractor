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

_URL = 'https://github.com/FRTNX/ml-data-scraper/dataset'
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

    BUILDER_CONFIGS = [
        CosujuConfig(
            name='plain_text',
            version=datasets.Version('1.0.0', ''),
            description='Plain text',
        ),
    ]

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
                    'summary_document': datasets.features.Sequence(
                        {
                            'filename': datasets.Value('string'),
                            'file_url': datasets.Value('string'),
                            'file_content': datasets.Value('string')
                        }
                    ),
                    'judgement_document': datasets.features.Sequence(
                        {
                            'filename': datasets.Value('string'),
                            'file_url': datasets.Value('string'),
                            'file_content': datasets.Value('string')
                        }
                    ),
                }
            ),
            supervised_keys=None,
            homepage='https://github.com/FRTNX/ml-data-scraper',
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
        with open(filepath, encoding="utf-8") as f:
            for id_, row in enumerate(f):
                data = json.loads(row)
                result = {
                    'id': data['id'],
                    'title': data['title'],
                    'url': data['url'],
                    'year': data['year'],
                    'update_date': data['update_date']
                }

                # as some court decisions have no summaries, may filter these out in future
                for prop in ['summary_document', 'judgement_document']:
                    if data[prop]:
                        result[prop] = data[prop]
                    else:
                        result[prop] = { 'filename': '', 'file_url': '', 'file_content': '' }
                    
                yield id_, result
