# -*- coding: utf-8 -*-

import logging
import scrapy
from bs4 import BeautifulSoup
from visir_slurper.items import VisirSlurperItem
import re

logger = logging.getLogger(__name__)

BASE_OVERVIEW_URL = "http://www.visir.is/section/{}"
BASE_URL = "http://www.visir.is"

CATS = ["FRETTIR01",                    # fréttir - innlent
        "FRETTIR02",                    # fréttir - erlent
        "FRETTIR08",                    # fréttir - bílar
        "VIDSKIPTI06",                  # viðskipti - innlent
        "VIDSKIPTI07",                  # viðskipti - erlent
        "VIDSKIPTI03",                  # viðskipti - kynningar
        "IDROTTIR0102",                 # íþróttir - enski boltinn
        "IDROTTIR02",                   # íþróttir - handbolti]
        "IDROTTIR03",                   # íþróttir - körfubolti
        "IDROTTIR0101",                 # íþróttir - íslenski boltinn
        "IDROTTIR01",                   # íþróttir - fótbolti
        "IDROTTIR05",                   # íþróttir - golf
        "IDROTTIR&template=newslist",   # íþróttir - aðrar íþróttir
        "IDROTTIR04",                   # íþróttir - formúla 1
        "IDROTTIR06",                   # íþróttir - veiði
        "LIFID01",                      # lífið
        "LIFID02",                      # lífið - tónlist
        "LIFID03",                      # lífið - bíó og sjónvarp
        "LIFID04",                      # lífið - tíska og hönnun
        "LIFID05",                      # lífið - gagnrýni
        "LIFID08",                      # lífið - menning
        "LIFID09",                      # lífið - heilsuvísir
        "LIFID12",                      # lífið - leikjavísir
        # "LIFID13",                      # lífið - matarvísir
        "LIFID19",                      # lífið - kynningar

        ]

CATS = ["LIFID13"]


class VisirNewsArticleSpide(scrapy.Spider):
    name = "visir_news_article_spider"
    allowed_domains = ["visir.is"]
    start_urls = [BASE_OVERVIEW_URL.format(x) for x in CATS]

    def parse(self, response):
        logger.info("Parsing {}".format(response.url))
        # Parse with Beautifoulsoup. It is slower than lxml, but it
        # doesn"t matter since visir.is is so sloooooooow anyway
        soup = BeautifulSoup(response.body, "html.parser")
        middle_section = soup.find(class_="x6 ml0")
        links = middle_section.find_all("h3")
        if links:
            logger.debug("len links {}".format(len(links)))
            for link in links:
                detail_url = BASE_URL + link.a["href"]
                request = scrapy.Request(detail_url,
                                         callback=self.parse_article_contents)
                # use the url as a deltafetch key
                request.meta["deltafetch_key"] = str(detail_url.encode("iso-8859-1"))
                # debugging skip
                yield request
            # Find the next page
            paging_url = soup.find(class_="paging").find("a")
            paging_url = BASE_URL + paging_url["href"]
            logger.debug("Next: {}".format(paging_url))
            request = scrapy.Request(paging_url,
                                    callback=self.parse)
            yield request
        else:
            # If no articles were found then we are done
            logger.info("Nothing found for {}".format(response.url))
            cat = response.url.split("/")[-1:][0].split("?")[0]
            logger.info("We are done with category: {}".format(cat))

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

    def clean_items(self, item):
        temp = VisirSlurperItem()
        for k, v in item.items():
            temp[k.strip()] = v.strip()
        return temp

    def parse_article_contents(self, response):
        """
        Parse a news article
        """
        soup = BeautifulSoup(response.body, "html.parser")
        # Drop scripts
        [s.extract() for s in soup("script")]
        item = VisirSlurperItem()
        id = response.url.split("/")[-1:][0]
        item["id"] = id
        item["url"] = response.url
        try:
            date_published = soup.find(attrs={"itemprop": "datePublished"})["content"]
            headline = soup.find(attrs={"itemprop": "headline"}).text
        except (AttributeError, TypeError):
            # Don"t care about articles without dates or headlines
            return
        description = soup.find(attrs={"itemprop": "description"})["content"]
        default_author = u"unknown"
        try:
            # Multiple authors is messed up in visir.is markup
            # This handles that
            author = soup.find_all(attrs={"itemprop": "author"})
            if author:
                author = " og ".join([x.text.strip() for x in author]).strip()
            else:
                # Some articles have the author in the text for the meta class
                # <div class="meta">Jónas Sen skrifar</div>
                author = soup.find(class_="meta")
                if author:
                    author = author.text.strip().replace(" skrifar", "")
                else:
                    author = default_author
        except AttributeError:
            # If no author then assign 'unknown'
            author = default_author
        category = soup.find(class_=re.compile("source-t")).text

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
        item['category'] = category
        item["body"] = response.body.decode("iso-8859-1")
        # strip
        item = self.clean_items(item)
        yield item
