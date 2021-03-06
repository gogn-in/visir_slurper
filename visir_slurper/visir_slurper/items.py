# -*- coding: utf-8 -*-

import scrapy


class VisirSlurperItem(scrapy.Item):
    url = scrapy.Field()
    article_text = scrapy.Field()
    author = scrapy.Field()
    possible_authors = scrapy.Field()
    date_published = scrapy.Field()
    headline = scrapy.Field()
    description = scrapy.Field()
    body = scrapy.Field()
    id = scrapy.Field()
    category = scrapy.Field()
