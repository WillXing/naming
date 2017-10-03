# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import json

class NamingPipeline(object):
    def __init__(self):
        self.file = codecs.open("2017_06_09_single.json", "w", "utf-8")
    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line.decode("unicode_escape"))
        return item
    def spider_closed(self, spider):
        self.file.close()