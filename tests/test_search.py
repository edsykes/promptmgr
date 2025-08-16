import unittest
from promptmgr.search import search_prompts
from promptmgr.models import Prompt

class SearchTests(unittest.TestCase):
    def setUp(self):
        self.prompts = [
            Prompt(id='1', name='Hello', description='', tags=['greet'], content='hello world'),
            Prompt(id='2', name='Bye', description='', tags=['farewell'], content='goodbye'),
            Prompt(id='3', name='Help', description='', tags=['assist'], content='help me'),
        ]

    def test_wildcard_search(self):
        results = search_prompts(self.prompts, 'H*', field='name', method='wildcard')
        self.assertEqual([p.id for p in results], ['1', '3'])

    def test_regex_search(self):
        results = search_prompts(self.prompts, r'^B.*', field='name', method='regex')
        self.assertEqual([p.id for p in results], ['2'])

    def test_fuzzy_search(self):
        results = search_prompts(self.prompts, 'helo', field='content', method='fuzzy')
        self.assertIn('1', [p.id for p in results])
