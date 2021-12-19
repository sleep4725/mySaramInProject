from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options

##
#
##
class ChromeClient:

    @classmethod
    def get_chrome_client(cls)-> Chrome:
        """

        :return:
        """
        # chrome_options = Options()
        # chrome_options.add_argument("headless")

        chrome_client = Chrome("./chromedriver/chromedriver.exe")

        return chrome_client