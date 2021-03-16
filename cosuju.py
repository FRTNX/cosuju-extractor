# coding=utf-8
# Copyright 2020 The TensorFlow Datasets Authors and the HuggingFace Datasets Authors.
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Lint as: python3
"""COSUJU: The Stanford Question Answering Dataset."""

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
        super(CourtSufuConfig, self).__init__(**kwargs)


class Cosuju(datasets.GeneratorBasedBuilder):
    """COSUJU: The Court Summaries and Judgements Dataset. Version 1.1."""

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
                    'update_time': datasets.Value('string'),
                    'summary_document': datasets.features.Sequence(
                        {
                            'filename': datasets.Value('string'),
                            'file_url': datasets.Value('sring'),
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
                    yield id_, {
                    'id': data['id'],
                    'title': data['title'],,
                    'url': data['url'],
                    'year': data['year'],
                    'update_time': data['update_time'],
                    'summary_document': {
                        'filename': data['summary_document']['filename'],
                        'file_url': data['summary_document']['file'],
                        'file_content': data['summary_document']['file_content']
                    },
                    'judgement_document': {
                       'filename': data['judgement_document']['filename'],
                        'file_url': data['judgement_document']['file'],
                        'file_content': data['judgement_document']['file_content']
                    }
                }

