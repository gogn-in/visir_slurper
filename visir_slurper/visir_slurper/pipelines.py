# -*- coding: utf-8 -*-

from dateutil import parser
import logging
import gzip
import os
from visir_slurper.settings import DATA_DIR
from scrapy.utils.serialize import ScrapyJSONEncoder
import json


logger = logging.getLogger(__name__)

_encoder = ScrapyJSONEncoder()


# TODO: Refactor these two together and use a settings flag

class VisirSlurperSaveArticleByDate(object):
    def __init__(self):
        pass

    def process_item(self, item, spider):
        date_parsed = parser.parse(item["date_published"])
        directory = os.path.join(DATA_DIR,
                                 date_parsed.strftime("%Y"),
                                 date_parsed.strftime("%m"),
                                 date_parsed.strftime("%d")
                                 )
        json_filename = os.path.join(directory, item["id"] + ".json")
        txt_filename = os.path.join(directory, item["id"] + ".txt")
        raw_filename = os.path.join(directory, item["id"] + "-html.gz")
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(txt_filename, "w") as f:
            f.write(item["article_text"].encode("utf-8"))
        with gzip.open(raw_filename, "w") as f:
            f.write(item["body"].encode("utf-8"))
        # store the article_text
        article_text = item["article_text"]
        # store the body
        body = item["body"]
        # pop article text and body from the item so as to no write it to the json
        item.pop("article_text", None)
        item.pop("body", None)
        with open(json_filename, "w") as f:
            f.write(_encoder.encode(item))
        item["article_text"] = article_text
        item["body"] = body
        logger.info("Saved {}".format(item["headline"].encode("utf-8")))
        return item


class VisirSlurperSaveAuthorArticles(object):
    def process_item(self, item, spider):
        author = item['author']
        filename = author.replace(" ", "_") + ".json"
        directory = os.path.join(DATA_DIR,
                                 "authors")
        filename = os.path.join(directory, filename)
        if not os.path.exists(directory):
            os.makedirs(directory)
        if os.path.exists(filename):
            with open(filename, "r") as f:
                data = json.loads(f.read())
                ids = data['articles']
                ids.append(item["id"])
                data['articles'] = ids
            with open(filename, "w") as f:
                f.write(_encoder.encode(data))
        else:
            data = {}
            with open(filename, "w") as f:
                ids = []
                ids.append(item["id"])
                data['articles'] = ids
                data['author'] = item['author']
                f.write(_encoder.encode(data))
        return item

    def close_spider(self, spider):
        # Uncomment to save a zipped archive of the data folder on exit
        # import shutil
        # import datetime
        # zip_filename = os.path.join(DATA_DIR, str(datetime.datetime.now().strftime("%Y-%d-%m-%H-%M")))
        # shutil.make_archive(zip_filename, "zip", DATA_DIR)
        # logger.info("Zipped data to %s" % zip_filename)
        pass
