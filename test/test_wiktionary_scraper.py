import src.wiktionary_scraper as ws
import unittest


class TestWiktionaryScraper(unittest.TestCase):
    def test_get_pronunciations_from_wiktionary_english(self):
        scraper = ws.Scraper('english')
        scraper.pronunciations_from_wiktionary_english('python')
        self.assertEqual(set(scraper.pronunciations['python']), {'/ˈpaɪθən/', '/ˈpaɪθɑːn/'})

    def test_get_pronunciations_from_wiktionary_french(self):
        scraper = ws.Scraper('french')
        scraper.pronunciations_from_wiktionary_french('python')
        self.assertEqual(set(scraper.pronunciations['python']), {'pi.tɔ̃'})

    def test_get_pronunciations_from_wiktionary_italian(self):
        scraper = ws.Scraper('italian')
        scraper.pronunciations_from_wiktionary_italian('precipitevolissimevolmente')
        self.assertEqual(set(scraper.pronunciations['precipitevolissimevolmente']),
                         {'//pre.ʧi.pi.te.voˌli.ssi.me.volˈmen.te//'})


if __name__ == '__main__':
    unittest.main()
