## 沪深股票单日行情查询小工具

最先想搞一个股票数据库来着，所以准备开始爬上交所的数据，被一个jsonpcallback搞昏了头，弄了一个多小时，结果发现是真的坑，也就是这个部分

```python
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
```

后来就不高兴全爬下来当数据库了，直接写一个从上交所/深交所查单日行情的小工具算了。

### 数据来源

上交所：http://www.sse.com.cn/assortment/stock/list/info/company/index.shtml?COMPANY_CODE=600008

深交所：https://www.szse.cn/market/trend/index.html?code=000002

### 返回格式

其实是一个pydantic的BaseModel，你可以用.dict()/.json()方法把它变成列表/JSON。

    stock_code: str	# 股票代码
    stock_name: str	# 股票名称
    date: date	# 日期
    open: float	# 开盘价
    high: float	# 最高价
    low: float	# 最低价
    close: float	# 收盘价
    yid: float	# 当日盈亏率
    volumn: float	# 成交股数（万）
    price: float	# 成交金额（万）
    PE: float	# 市盈率

### 使用方法

直接query(stock_code, date)

或者另起一个文件，比如这里的main.py

```python
from tickerlookup import query

# 上交所 600008 首创环保
stock_code = '600008'
date = '2023-01-04'
print(query(stock_code, date).dict())

# 深交所 000002 万科A
stock_code = '000002'
date = '2023-01-04'
print(query(stock_code, date).dict())
```

运行结果：

```json
{'stock_code': '600008', 'stock_name': '首创环保', 'date': datetime.date(2023, 1, 4), 'open': 2.89, 'high': 2.91, 'low': 2.87, 'close': 2.89, 'yid': 0.34722, 'volumn': 4234.94, 'price': 12255.84, 'PE': 9.27414}
{'stock_code': '000002', 'stock_name': '万科Ａ', 'date': datetime.date(2023, 1, 4), 'open': 18.25, 'high': 19.28, 'low': 18.07, 'close': 19.07, 'yid': 4.61, 'volumn': 10871.46, 'price': 206031.74, 'PE': 9.84}
```

