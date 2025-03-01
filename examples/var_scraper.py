# Grab tables of variables from the SDK docs
#
# This script scrapes variable tables from the SDK documentation.
#
import scrapy
import scrapy.exporters
import unicodedata
import json
from scrapy.crawler import CrawlerProcess
from prepvars import prepvars

base_urls = [
    # main list of links
    'https://docs.flightsimulator.com/html/Programming_Tools/SimVars/Simulation_Variables.htm',
    # not linked explicitly elsewhere
    'https://docs.flightsimulator.com/html/Programming_Tools/SimVars/Event_IDs/Aircraft_Electrical_Events.htm'
]


def normtext(s):
    return unicodedata.normalize('NFKC', s) if s else ''


def jointext(xs):
    return ''.join(map(normtext, xs.getall())).strip()


class PostProcessExporter(scrapy.exporters.BaseItemExporter):
    def __init__(self, file, **kwargs):
        super().__init__(dont_fail=True, **kwargs)
        self.file = file
        self.items = []

    def start_exporting(self):
        pass

    def export_item(self, item):
        self.items.append(item)

    def finish_exporting(self):
        raw = dict()
        for item in sorted(self.items, key=lambda d: (d['page'], d['index'])):
            typ = item['type']
            del item['type']
            del item['index']
            raw.setdefault(typ, []).append(item)
        output = prepvars(raw)
        s = json.dumps(output, indent=4).encode('utf-8')
        self.file.write(s)


class SimConnectSpider(scrapy.Spider):
    name = "SimConnectSDK"

    custom_settings = {
        'FEED_EXPORTERS': {'json': PostProcessExporter},
        'LOG_LEVEL': 'ERROR'  # Suppress logs by default
    }

    def start_requests(self):
        for url in base_urls:
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        def alltext(elt):
            if elt:
                return jointext(elt.xpath('.//text()'))
            else:
                return None

        def parse_row(row, simvar):
            tds = row.xpath('td')
            ncol = len(tds)
            if ncol < 2:
                return None
            labels = ['name', 'description', 'multiplayer', 'units', 'settable']
            vs = [
                     jointext(tds[0].xpath('.//text()'))
                 ] + [
                     alltext(td) for td in tds[1:(ncol - 1 if simvar else ncol)]
                 ]
            if simvar:
                vs.append(tds.xpath('span[@class="checkmark"]/span/@class').get() == 'checkmark_circle')
                if ncol < 5:
                    labels = labels[:ncol - 2] + labels[-2:]
            return dict(zip(labels, vs))

        urls = response.xpath('//div//ul/li/a/@href').getall()
        for url in urls:
            yield scrapy.Request(url=response.urljoin(url), callback=self.parse)

        page = normtext(response.xpath('//h2/text()').get()).strip()
        context = {
            'url': response.url,
            'page': page,
            'type': page.split()[-1].replace('IDs', 'EVENTS')
        }
        i = 0
        for tbl in response.xpath('//table'):
            section = tbl.xpath('preceding-sibling::h4[1]') or tbl.xpath('preceding-sibling::h3[1]')
            context['section'] = normtext(section.xpath('text()').get())
            simvar = tbl.xpath('tbody/tr/th/text()').get().strip().lower() == 'simulation variable'
            for row in tbl.xpath('tbody/tr'):
                d = parse_row(row, simvar)
                if d:
                    d.update(context, index=i)
                    i += 1
                    yield d


if __name__ == "__main__":
    # Output file for scraped data
    output_file = "scvars.json"

    process = CrawlerProcess(settings={
        "FEEDS": {
            output_file: {"format": "json"},
        }
    })

    process.crawl(SimConnectSpider)
    process.start()
