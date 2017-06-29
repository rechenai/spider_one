# -*- coding: utf-8 -*-
import re
import scrapy
import datetime
from scrapy.http import Request
from urllib import parse
from scrapy.loader import ItemLoader

from Article.items import caoliuArticleItem

from Article.utils.common import get_md5


class CaoliuSpider(scrapy.Spider):
    name = 'first'
    allowed_domains = ['...']
    start_urls = ['...']

    def parse(self, response):
        """
        1 获取文章列表中的url 并交给解析函数进行具体字段的解析
        2 获取下一页的url交给scrapy进行下载，下载完成后借给parse
        """

        post_urls = response.css(".t_one h3 a::attr(href)").extract()
        for post_url in post_urls:
            url = re.match("(.*/).*", response.url)
            p_url = url.group(1)
            d_url = parse.urljoin(p_url, post_url)
            yield Request(url=d_url, callback=self.parse_detail)

        # 下一页url
        next_url = response.css(".pages a:nth-last-child(2)::attr(href)").extract_first()
        if next_url:
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)



    def parse_detail(self, response):
        # 解析文字详情
        article_item = caoliuArticleItem()

        urladdr = response.url
        title = response.css('h4::text').extract_first()
        time = response.css('.tipad::text').extract()[4].strip()
        match_time = re.match(".*(\d{4}-\d{2}-\d{2}).*", time).group(1)
        if match_time:
            time = match_time
        else:
            time = ''
        article_item["title"] = title
        try:
            time = datetime.datetime.strptime(time, "%Y/%m/%d").date()
        except Exception as e:
            time = datetime.datetime.now().date()
        article_item["time"] = time
        article_item["url"] = urladdr
        article_item["url_object_id"] = get_md5(urladdr)


        # 通过itemloader加载item
        # item_loader = ItemLoader(item=caoliuArticleItem(), response=response)
        # item_loader.add_css()
        # item_loader.add_value()
        #
        # article_item= item_loader.load_item()
        yield article_item
