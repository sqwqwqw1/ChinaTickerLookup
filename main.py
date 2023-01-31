from tickerlookup import query

# 上交所 600008 首创环保
stock_code = '600008'
date = '2023-01-04'
print(query(stock_code, date).dict())

# 深交所 000002 万科A
stock_code = '000002'
date = '2023-01-04'
print(query(stock_code, date).dict())