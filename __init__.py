import numpy, pandas, time, urllib
np, pd = numpy, pandas

_base_url = "http://hq.sinajs.cn/list="
# ---
#              最新价              ??         买价         卖价       最高价      最低价  行情时间
_outer_att = ["price","fetch_datetime","buy_price","sell_price","high_price","low_price","time",
              "yestoday_close","today_open","inventory","buyNum_change","sellNum_change","date","name"]
#                      昨结算       开盘价      持仓量        买量变化         卖量变化   日期   品名
# ---
#               品名     ??         开盘价       最高价      最低价          昨收价        买价          卖价   最新价
_inner_att = ["name","state","today_open","high_price","low_price","yestoday_close","buy_price","sell_price","price",
"settle","yestoday_settle","buy_number","sell_number","inventory","turnover",'short_exchange','short_name',"date"]
# 结算价           昨结价         买量          卖量        持仓     成交量       交易所简称     品名简称    日期
# ---

def datetime_str(): return time.strftime("%Y-%m-%d %H:%M:%S %a")

def get_an_outer(url):
    '获取一个外盘品种的即时报价. 入口参数为品种代码(如hf_C), 或URL'
    if url[:4].upper() != "HTTP": url = _base_url+url
    prc_lst = str(urllib.request.urlopen(url).read().decode("GB2312")).split('"')[1].split(',')[:len(_outer_att)]
    dct0 = {att:val for att,val in zip(_outer_att,prc_lst)}
    dct = {}
    for att in ["yestoday_close","today_open","price","buy_price","sell_price","high_price","low_price","inventory"]:
        dct[att] = float(dct0[att])
    dct["date"] = dct0["date"]
    dct["time"] = dct0["time"]
    dct['fetch_datetime'] = datetime_str()[:19]
    return dct

def get_an_inner(url):
    '获取一个内盘品种的即时报价. 入口参数为品种代码(如C0), 或URL'
    if url[:4].upper() != "HTTP": url = _base_url+url
    prc_lst = str(urllib.request.urlopen(url).read().decode("GB2312")).split('"')[1].split(',')[:len(_inner_att)]
    dct0 = {att:val for att,val in zip(_inner_att,prc_lst)}
    dct = {}
    for att in ["yestoday_close","today_open","price","buy_price","sell_price","high_price","low_price","inventory","turnover"]:
        dct[att] = float(dct0[att]) # an extra turnover is returned here...
    dct["date"] = dct0["date"]
    dct['time'] = datetime_str()[11:19] #""
    dct['fetch_datetime'] = datetime_str()[:19]
    return dct

def get_inner_turnovers(codes): return [get_an_inner(code)['turnover'] for code in codes]

def get_the_major(prefix):
    '获取主力合约. 入口参数为合约前缀, 如玉米为C'
    d = datetime_str()
    y, m = d[2:4], d[5:7]
    if m == '01':
        d1, d2, d3 = y+"01", y+"05", y+"09"
    elif int(m) <= 5:
        d1, d2, d3 = y+"05", y+"09", "%02d"%(1+int(y))+"01"
    elif int(m) <= 9:
        d1, d2, d3 = y+"09", "%02d"%(1+int(y))+"01", "%02d"%(1+int(y))+"05"
    else:
        d1, d2, d3 = "%02d"%(1+int(y))+"01", "%02d"%(1+int(y))+"05", "%02d"%(1+int(y))+"09"
    codes = [prefix+d for d in [d1, d2, d3]]
    turns = get_inner_turnovers(codes)
    idx = np.argmax(turns)
    return codes[idx]
