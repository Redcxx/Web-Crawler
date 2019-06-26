# -*- coding: utf-8 -*-
import scrapy, re
from scrapy import Request


class JobsSpider(scrapy.Spider):
    name = 'jobs'
    allowed_domains = ['craigslist.org']
    start_urls = ['https://newyork.craigslist.org/search/egr']

    def parse(self, response):
        jobs = response.xpath('//p[@class="result-info"]')
        for job in jobs:
            title = job.xpath('a/text()').getall()[0]
            address = job.xpath('span[@class="result-meta"]/span[@class="result-hood"]/text()').get("")[2:-1]
            rel_url = job.xpath('a/@href').get()
            desc_url = response.urljoin(rel_url)
            meta = {'title':title, 'address': address}
            yield Request(desc_url, meta=meta, callback=self.get_desc)
        next_rel_url = response.xpath('//a[@class="button next"]/@href').get()
        next_abs_url = response.urljoin(next_rel_url)
        yield Request(next_abs_url, callback=self.parse)

    def get_desc(self, response):
        title = response.meta.get('title')
        address = response.meta.get('address')
        info = {'title': title, 'address': address}
        desc = response.xpath('//*[@id=\'postingbody\']/text()').getall()
        info['description'] = ''.join(line for line in desc).strip()
        attrs = response.xpath('//p[@class=\'attrgroup\']/span//text()').getall()
        attrs = iter([re.sub('(:.*)', '', attr) for attr in attrs])
        for heading, content in zip(attrs, attrs):
            info[heading] = content
        yield info
