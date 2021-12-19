import time
import requests
from bs4 import BeautifulSoup

from selenium.webdriver.common.by import By
from chromeClient.chromeWeb import ChromeClient
from urlConfig.urlHeader import UrlHeader
from elasticClient.es import ElasticClient
from exceptionHandler.requestError import *

from urllib.parse import urlencode
from urllib.parse import urlsplit

from elasticsearch.helpers import bulk

##
#
##
class SaramIn(UrlHeader):

    def __init__(self, search_word):
        UrlHeader.__init__(self)
        self.chrome_client = ChromeClient.get_chrome_client()
        self.url = "https://www.saramin.co.kr/zf_user/search"
        self.search_word = search_word
        self.params = urlencode({
            "search_area": "main",
            "search_done": "y",
            "search_optional_item": "n",
            "searchType": "default_popular",
            "searchword": f"{self.search_word}"
        })
        self.es_client = ElasticClient.ret_es_client()
        self.es_bulk_list = []
        self.es_saramin_index = "saramin"

    def get_data_templates(self)-> dict:
        """

        :return:
        """
        return {
            "_index": self.es_saramin_index,
            "_source": {
                "title": "",  # type keyword
                "corp_name": "", # type keyword
                "job_sector": [],
                "page": 0, # type integer
                "search_word": self.search_word
            }
        }

    def es_bulk_insert(self):
        """

        :return:
        """
        try:

            bulk(client= self.es_client, actions= self.es_bulk_list)
        except:
            pass

    def get_data(self):
        """

        :return:
        """
        self.chrome_client.get(self.url + "?" + self.params)
        time.sleep(10)

        self.chrome_client.find_element(By.CLASS_NAME, "view_more.track_event").click()
        time.sleep(3)
        current_url = urlsplit(self.chrome_client.current_url)
        page = 1
        while True:
            url_query = current_url.query.replace('recruitPage=2', f'recruitPage={page}')

            saramin_url = "https://www.saramin.co.kr" + current_url.path + "?" + url_query
            response = requests.get(saramin_url, headers= self.headers)
            if response.status_code == 200:
                bs_object = BeautifulSoup(response.text, "html.parser")
                is_content = bs_object.find("div", {"class": "content"})
                if is_content:
                    content = bs_object.select_one("div#content")
                    result = content.find("div", {"class": "info_no_result"})
                    if not result:
                        item_recruit = bs_object.select_one("div.content").select("div.item_recruit")
                        for r in item_recruit:
                            data_templates = self.get_data_templates()

                            data_templates["_source"]["page"] = page # 웹 페이지

                            try:
                                title = r.select_one("div.area_job > h2.job_tit > a").attrs["title"]
                                data_templates["_source"]["title"] = title #
                            except:
                                pass

                            try:
                                corp_name = r.select_one("div.area_corp > strong.corp_name > a").attrs["title"]
                                data_templates["_source"]["corp_name"] = corp_name # 회사이름름
                            except:
                               pass

                            try:
                                job_sector = [a.text for a in r.select_one("div.job_sector").select("a")]
                                data_templates["_source"]["job_sector"].extend(job_sector)
                            except:
                                pass

                            self.es_bulk_list.append(data_templates)

                        if self.es_bulk_list:
                            self.es_bulk_insert()
                            self.es_bulk_list.clear()

                        print("{page} 적재 완료".format(page=page))

                    else:
                        break
                else:
                    raise LastPage
            else:
                raise RequestError

            # ==================
            # page
            page += 1

    def __del__(self):
        try:
            self.es_cljient.transport.close()
        except:
            pass

        try:
            self.chrome_client.quit()
        except:
            pass

if __name__ == "__main__":
    o = SaramIn(search_word="flask")
    o.get_data()