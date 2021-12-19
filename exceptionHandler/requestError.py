class RequestError(Exception):

    def __init__(self):
        super().__init__("requests error")

class LastPage(Exception):

    def __init__(self):
        super().__init__("마지막 페이지 입니다.")

class ElasticHealthError(Exception):

    def __init__(self):
        super().__init__("elastic health error")