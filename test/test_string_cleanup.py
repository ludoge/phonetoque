import yaml
import src.string_cleanup as sc
import unittest


class TestStringCleanup(unittest.TestCase):
    def setUp(self):
        with open('../scripts/script_config.yml', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

    def test_remove_stop_chars(self):
        cleanup = sc.StringCleanup(self.config)
        self.assertEqual(cleanup.remove_stop_chars(cleanup.stop_chars), '')

    def test_simplify_separators(self):
        cleanup = sc.StringCleanup(self.config)
        self.assertEqual(cleanup.simplify_separators('--a--b-cde-fg-h---'), 'a-b-cde-fg-h')


if __name__ == '__main__':
    unittest.main()
