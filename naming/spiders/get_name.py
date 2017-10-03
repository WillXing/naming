# -- coding: UTF-8 -- 
import scrapy
import re
import datetime
import time

#==debug==#
import logging
from scrapy.shell import inspect_response

class NamingSpider(scrapy.Spider):
    basic_url = "http://m.meimingteng.com/m/qiming.aspx"
    name = "naming"
    xing = "黄刘"
    gender = 0
    birthDateTime = datetime.datetime(2017, 6, 9, 9, 20);
    mins = 0
    hType = 1

    basicParam = None
    page = 1

    firstPageResponse = None
    
    def start_requests(self):
        self.logger.log(logging.DEBUG, "****************** START ******************")
        yield scrapy.Request(self.basic_url, callback=self.parse, dont_filter = True)

    def parse(self, response):
        self.logger.log(logging.DEBUG, "****************** PARSE ******************")
        self.firstPageResponse = response
        # viewStage = response.css("form > #__VIEWSTATE::attr(value)").extract()
        # viewStageGenerator = response.css("form > #__VIEWSTATEGENERATOR::attr(value)").extract()
        yield scrapy.FormRequest.from_response(
            response,
            formdata={"ctl00$ContentPlaceHolder1$tbXing": self.xing, 
            "ctl00$ContentPlaceHolder1$tbBirth": self.birthDateTime.strftime("%Y-%m-%d %H:%M"),
            "ctl00$ContentPlaceHolder1$hiddType": str(self.hType)},
            callback=self.init_basic_param_and_start,
            dont_filter = True
        )
    
    def init_basic_param_and_start(self, response):
        pattern = re.compile(r"\"Params=(.*?)\"")
        params = response.xpath("//script[contains(.,'AJAXPagingClick')]/text()").re(pattern)
        haveParam = len(params) > 0
        
        if not haveParam:
            self.logger.log(logging.WARNING, "!!!!!!!!!!!!!!!!!!!!!!!!No Param!!!!!!!!!!!!!!!!!!!!")
            time.sleep(10)
            yield scrapy.Request(self.basic_url, callback=self.parse, dont_filter = True)
        else:
            self.basicParam = "Params=" + response.xpath("//script[contains(.,'AJAXPagingClick')]/text()").re(pattern)[0] + "&ajaxp=1&Page="
            pageParam = self.basicParam + str(self.page)
            yield scrapy.Request("http://m.meimingteng.com/m/qiming.aspx?" + pageParam, self.show_name)

    def show_name(self, response):
        capthchaOnPage = len(response.css('#captchacharacters').extract()) > 0
        if capthchaOnPage:
            self.logger.log(logging.WARNING, "!!!!!!!!!!!!!!!!!!!!!!!!Captcha found!!!!!!!!!!!!!!!!!!!!")
            self.logger.log(logging.WARNING, "!!!!!!!!!!!!!!!!!!!!!!!!Sleep!!!!!!!!!!!!!!!!!!!!")
            inspect_response(response, self)
            time.sleep(5)
        else:
            nameItemList = response.css(".baby_name_item")

            for nameItem in nameItemList:
                name = nameItem.css("li>a>font::text").extract()[0]
                detail = re.sub(r"<.*?>", " ", response.css("#divExp"+name).extract()[0].encode('utf-8'))
                yield {
                    "birthDateTime": self.birthDateTime.strftime("%Y-%m-%d %H:%M"),
                    "name": name.encode('utf-8'),
                    "wuxing": nameItem.css("li>a>font>font::text").extract()[0].encode('utf-8'),
                    "detail": detail
                }

        if self.page < 3:
            if not capthchaOnPage:
                self.page = self.page + 1

            nextPageParam = self.basicParam + str(self.page)
            yield scrapy.Request("http://m.meimingteng.com/m/qiming.aspx?" + nextPageParam, self.show_name)
            return
        elif self.birthDateTime.hour < 18:

            time.sleep(5)

            if not capthchaOnPage:
                self.birthDateTime = self.birthDateTime + datetime.timedelta(0, 60)

            self.logger.log(logging.DEBUG, "****************** min < 60 ******************")
            self.page = 1
            yield scrapy.Request(self.basic_url, callback=self.parse, dont_filter = True)
            return
        else:
            return
