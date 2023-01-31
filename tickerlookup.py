import requests, random, re, json
from datetime import datetime, date
from chinese_calendar import is_workday
from pydantic import BaseModel

class StockInfo(BaseModel):
    stock_code: str
    stock_name: str
    date: date
    open: float
    high: float
    low: float
    close: float
    yid: float
    volumn: float
    price: float
    PE: float

class Error(BaseModel):
    Error: str

class SSEQuery(object):
    def __init__(self):
        self.url = 'http://query.sse.com.cn/commonQuery.do'
        self.headers = {
            'Host': 'query.sse.com.cn',
            'Referer': 'http://www.sse.com.cn/',
        }

    def get_jsonp(self):
        return f'jsonpCallback{int(random.random()*(10000000+1))}'

    def get_timestamp(self):
        return str(int(datetime.timestamp(datetime.now()) * 1000))

    def start_request(self, stock_code, date):
        jsonp = self.get_jsonp()
        timestamp = self.get_timestamp()
        url = self.url
        headers = self.headers
        data = {
            'jsonCallBack': jsonp,
            'sqlId': 'COMMON_SSE_CP_GPJCTPZ_GPLB_CJGK_MRGK_C',
            'SEC_CODE': stock_code,
            'TX_DATE': date,
            'TX_DATE_MON': '',
            'TX_DATE_YEAR': '',
            '_': timestamp,
        }
        return requests.post(url, data=data, headers=headers)

    def parse_jsonp(self, r):
        return json.loads(re.search(r'jsonpCallback\d+\((.*?)\)', r.text).group(1))['result'][0]

    def check_date(self, date):
        if not is_workday(datetime.date(datetime.strptime(date, '%Y-%m-%d'))):
            return False
        if datetime.date(datetime.strptime(date, '%Y-%m-%d')).weekday()>4:
            return False
        return date

    def format_dict(self, data):
        return {
            'stock_code': data['SEC_CODE'],
            'stock_name': data['SEC_NAME'],
            'open': data['OPEN_PRICE'],
            'high': data['HIGH_PRICE'],
            'low': data['LOW_PRICE'],
            'close': data['CLOSE_PRICE'],
            'yid': data['CHANGE_RATE'],
            'volumn': data['TRADE_VOL'],
            'price': data['TRADE_AMT'],
            'PE': data['PE_RATE'],
        }

    def query(self, stock_code, date):
        date = self.check_date(date)
        if not date:
            return Error(**{'Error':'非交易日！'})
        r = self.start_request(stock_code, date)
        data = self.parse_jsonp(r)
        data = self.format_dict(data)
        data.update({'date': date})
        return StockInfo(**data)

class SZSEQuery(object):
    def __init__(self):
        self.url = 'http://www.szse.cn/api/report/ShowReport/data'

    def check_date(self, date):
        if not is_workday(datetime.date(datetime.strptime(date, '%Y-%m-%d'))):
            return False
        if datetime.date(datetime.strptime(date, '%Y-%m-%d')).weekday()>4:
            return False
        return date

    def start_request(self, stock_code, date):
        data = {
            'SHOWTYPE': 'JSON',
            'CATALOGID': '1815_stock',
            'TABKEY': 'tab1',
            'txtDMorJC': str(stock_code),
            'txtBeginDate': date,
            'txtEndDate': date,
            'radioClass': '00%2C20%2C30%2CC6%2CC7%2CGE%2C14',
            'txtSite': 'all',
            'random': random.random(),
        }
        return requests.get(self.url, data)

    def format_dict(self, data):
        return {
            'stock_code': data['zqdm'],
            'stock_name': data['zqjc'].replace('&nbsp;',''),
            'open': data['ks'],
            'high': data['zg'],
            'low': data['zd'],
            'close': data['ss'],
            'yid': data['sdf'],
            'volumn': data['cjgs'].replace(',' ,''),
            'price': data['cjje'].replace(',' ,''),
            'PE': data['syl1'],
        }

    def query(self, stock_code, date):
        date = self.check_date(date)
        if not date:
            return Error(**{'Error':'非交易日！'})
        r = self.start_request(stock_code, date)
        data = self.format_dict(r.json()[0]['data'][0])
        data.update({'date': date})
        return StockInfo(**data)

def query(stock_code, date):
    try:
        if stock_code[:1] in ['0', ['3']]:
            szsequery = SZSEQuery()
            return szsequery.query(stock_code, date)
        else:
            ssequery = SSEQuery()
            return ssequery.query(stock_code, date)
    except:
        try:
            szsequery = SZSEQuery()
            return szsequery.query(stock_code, date)
        except:
            return Error(**{"Error": "查询失败！"})