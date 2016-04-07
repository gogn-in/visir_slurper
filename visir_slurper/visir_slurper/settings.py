# -*- coding: utf-8 -*-

# Scrapy settings for visir_slurper project

import os

BOT_NAME = 'visir_slurper'
SPIDER_MODULES = ['visir_slurper.spiders']
NEWSPIDER_MODULE = 'visir_slurper.spiders'
TELNETCONSOLE_ENABLED = False
USER_AGENT_LIST = "user_agents.txt"
LOG_LEVEL = "INFO"
DATA_DIR = "data"

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY=3
# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 32
# CONCURRENT_REQUESTS_PER_IP=16

# Disable cookies (enabled by default)
# COOKIES_ENABLED=False

SPIDER_MIDDLEWARES = {
                    'visir_slurper.middlewares.deltafetch.DeltaFetch': 100,
                     }

DELTAFETCH_ENABLED = True
DELTAFETCH_DIR = os.path.abspath(os.path.dirname(__file__)).replace('\\', '/')
DELTAFETCH_RESET = False

DOWNLOADER_MIDDLEWARES = {
    'random_useragent.RandomUserAgentMiddleware': 400
    }


ITEM_PIPELINES = {
    'visir_slurper.pipelines.VisirSlurperSaveArticleByDate': 300,
    'visir_slurper.pipelines.VisirSlurperSaveAuthorArticles': 350,
}
