import os
import tempfile
import time
import unittest
from promptmgr.storage import save_prompt, load_prompt
from promptmgr.models import Prompt

class StorageTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.filepath = os.path.join(self.tmpdir.name, 'example.md')
        self.prompt = Prompt(id='1', name='Test', description='desc', tags=['t1'], content='hello world')

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_save_and_load_prompt(self):
        save_prompt(self.prompt, self.filepath)
        loaded = load_prompt(self.filepath)
        self.assertEqual(loaded.content.strip(), 'hello world')
        self.assertEqual(loaded.metadata['id'], '1')
        self.assertEqual(loaded.metadata['tags'], ['t1'])

    def test_version_is_appended_on_save(self):
        save_prompt(self.prompt, self.filepath)
        self.prompt.content = 'new content'
        time.sleep(0.01)
        save_prompt(self.prompt, self.filepath)
        with open(self.filepath, 'r', encoding='utf-8') as f:
            data = f.read()
        self.assertIn('new content', data.split('\n---\n')[1])
        self.assertIn('hello world', data)
        # ensure previous version stored below
        self.assertGreater(data.rfind('hello world'), data.find('new content'))
