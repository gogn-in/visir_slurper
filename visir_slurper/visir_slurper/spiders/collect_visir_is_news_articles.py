# -*- coding: utf-8 -*-

import logging
import scrapy
from bs4 import BeautifulSoup
from visir_slurper.items import VisirSlurperItem

logger = logging.getLogger(__name__)

BASE_URL = "http://www.visir.is/section/FRETTIR?page={}"


class VisirNewsArticleSpide(scrapy.Spider):
    name = "visir_news_article_spider"
    allowed_domains = ["visir.is"]

    def start_requests(self):
        # TODO: make this a setting or a recursive crawl
        # Currently we go back 200 overview pages but they are
        # at least 1400
        range_ids = [x for x in range(0, 200)]
        for page in range_ids:
            request = self.make_requests_from_url(
                        BASE_URL.format(page)
                            )
            yield request

    def parse(self, response):
        logger.info("Parsing {}".format(response.url))
        # Parse with Beautifoulsoup. It is slower than lxml, but it
        # doesn"t matter since visir.is is so sloooooooow anyway
        soup = BeautifulSoup(response.body, "html.parser")
        middle_section = soup.find(class_="x6 ml0")
        for link in middle_section.find_all("h3"):
            detail_url = "http://visir.is" + link.a["href"]
            request = scrapy.Request(detail_url,
                                     callback=self.parse_article_contents)
            # use the url as a deltafetch key
            request.meta["deltafetch_key"] = str(detail_url.encode("iso-8859-1"))
            yield request

    def text_with_newlines(self, elem):
        """
        Extract text from an element converting br to newlines
        """
        text = ""
        for e in elem.recursiveChildGenerator():
            if isinstance(e, basestring):
                text += e
            elif e.name == "br":
                text += "\n"
        return "\n".join([x for x in text.splitlines() if x.strip()])

    def parse_article_contents(self, response):
        """
        Parse a news article
        """
        soup = BeautifulSoup(response.body, "html.parser")
        # Drop scripts
        [s.extract() for s in soup("script")]
        item = VisirSlurperItem()
        item["url"] = response.url
        try:
            date_published = soup.find(attrs={"itemprop": "datePublished"})["content"]
            headline = soup.find(attrs={"itemprop": "headline"}).text
        except AttributeError:
            # Don"t care about articles without dates or headlines
            return
        description = soup.find(attrs={"itemprop": "description"})["content"]
        try:
            # Multiple authors is messed up in visir.is markup
            # This handles that
            author = soup.find_all(attrs={"itemprop": "author"})
            author = " ".join([x.text.strip() for x in author]).strip()
        except AttributeError:
            # If no author then leave it an empty string, we assign it later
            # in the export pipelines.
            author = u""
        # drop cruft
        crufts = ["meta",
                  "mob-share",
                  "imgtext",
                  "fb-post",
                  "twitter-tweet",
                  "art-embed"
                  ]
        for k in crufts:
            tags = soup.find_all(class_=k)
            for tag in tags:
                tag.extract()
        # Extract the text
        text = soup.find(attrs={"itemprop": "articleBody"})
        text = self.text_with_newlines(text)
        text = headline + "\n" + description + "\n" + text
        item["date_published"] = date_published
        item["headline"] = headline
        item["author"] = author
        item["article_text"] = text
        item["description"] = description
        item["body"] = response.body.decode("Windows-1252")
        yield item
