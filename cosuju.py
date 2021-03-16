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
"""COSUFU: The Stanford Question Answering Dataset."""

from __future__ import absolute_import, division, print_function

import json

import datasets


logger = datasets.logging.get_logger(__name__)


_CITATION = """\
@InProceedings{huggingface:dataset,
title = {CoSuFu 500+ Court Judegements and Summaries for Machine Text Summarization},
authors={Busani Ndlovu, Luke Jordan
},
year={2021}
}
"""

_DESCRIPTION = """\
Court Summaries and Judgements (CoSuJu) is a reading comprehension \
dataset
"""

_URL = 'https://github.com/FRTNX/ml-data-scraper/dataset'
_URLS = {
    'train': _URL + 'mini-train-v1.0.json'
}


class CosufuConfig(datasets.BuilderConfig):
    """BuilderConfig for COSUFU."""

    def __init__(self, **kwargs):
        """BuilderConfig for COSUFU.
        Args:
          **kwargs: keyword arguments forwarded to super.
        """
        super(CosufuConfig, self).__init__(**kwargs)


class Cosufu(datasets.GeneratorBasedBuilder):
    """COSUFU: The Court Summaries and Judgements Dataset. Version 1.1."""

    BUILDER_CONFIGS = [
        CosufuConfig(
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
                            'file_url': datasets.Value('sring'),
                            'file_content': datasets.Value('string')
                        }
                    ),
                }
            ),
            # No default supervised_keys (as we have to pass both question
            # and context as input).
            supervised_keys=None,
            homepage='https://github.com/FRTNX/',
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
        with open(filepath, encoding='utf-8') as f:
            cosufu = json.load(f)
            for article in cosufu['data']:
                title = article.get('title', '').strip()
                for paragraph in article['paragraphs']:
                    context = paragraph['context'].strip()
                    for qa in paragraph['qas']:
                        question = qa['question'].strip()
                        id_ = qa['id']

                        answer_starts = [answer['answer_start'] for answer in qa['answers']]
                        answers = [answer['text'].strip() for answer in qa['answers']]

                        # Features currently used are 'context', 'question', and 'answers'.
                        # Others are extracted here for the ease of future expansions.
                        yield id_, {
                            'title': title,
                            'context': context,
                            'question': question,
                            'id': id_,
                            'answers': {
                                'answer_start': answer_starts,
                                'text': answers,
                            },
                        }
