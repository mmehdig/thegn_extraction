from word_generation import generate_sets_of_words

import urllib.parse
import scrapy
from scrapy.http import Request, FormRequest
from scrapy.crawler import CrawlerProcess


def split_in_batches(set_data, batch_size):
    list_data = list(set_data)
    l = len(list_data)
    n = int(l/batch_size)
    return [list_data[i*batch_size:(i+1)*batch_size] for i in range(n+1)]

def make_url_from_query(queries):
    safe_string = urllib.parse.quote_plus(f'["{"|".join(queries)}"]')
    return f'http://clarino.uib.no/menota/concordance?query={safe_string}&corpus=menota&query-mode=advanced&lemma-query=off'

logfile = 'menota_outputfile.tsv'
with open(logfile, 'w') as f:
    f.write(f"word\ttitle\turl\n")
    f.close()

class MenotaSpider(scrapy.Spider):
    name="database"
    start_urls = [
        make_url_from_query(query)
        for set_of_words in generate_sets_of_words()
        for query in split_in_batches(set_of_words, 100)
    ]
    _cpos_to_word = dict()

    def parse(self, response):
        session_id = response.css("#pageForm > #session-id").xpath('@value').get()
        query = response.css("#queryString").css("::text").get()
        data = {
            'session-id': session_id,
            'query': query,
            'shown-attributes': 'cpos',
        }
        return FormRequest(f'https://clarino.uib.no/menota/concordance', formdata=data, callback=self.parse_hits)

    def parse_hits(self, response):
        for hits in response.css("#pageForm > div:nth-child(11) > span:nth-child(3)"):
            hits = hits.css("::text").get()
            if hits == "No hit.":
                yield None
            else:
                session_id = response.css("#pageForm > #session-id").xpath('@value').get()
                yield Request(f'http://clarino.uib.no/menota/concordance.tsv?session-id={session_id}', callback=self.parse_tsv)

    def parse_tsv(self, response):
        for line in response.text.split("\n"):
            if len(line) == 0 or line[0] == "#":
                continue
            else:
                cpos, word = line.split("\t")
                self._cpos_to_word[cpos] = word
                url = f"https://clarino.uib.no/menota/document-element?cpos={cpos}&corpus=menota"
                yield Request(url, callback=self.parse_context)

    def parse_context(self, response):
        url = response.url
        cpos = response.css("#documentElementForm > input[type=hidden]:nth-child(3)").xpath('@value').get()
        word = self._cpos_to_word[cpos]
        title = ""
        for _title in response.css('span.subtitle'):
            title = _title.css("::text").get()
        with open(logfile, 'a') as f:
            f.write(f"{word}\t{title}\t{url}\n")
            f.close()
        yield None

process = CrawlerProcess()
process.crawl(MenotaSpider)
process.start()
