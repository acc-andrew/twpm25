from flask import Flask
from flask import request
app = Flask(__name__)

from json import loads
import urllib.request  # worked ref

Dict={}

def init_pm25():
    global Dict
    with urllib.request.urlopen("https://opendata.epa.gov.tw/webapi/Data/ATM00625/?$skip=0&$top=1000&format=json") as url:
        Dict = loads(url.read().decode())
        print('func init_PM25() is ready.')

@app.route('/getminpm25')
def getminpm25():
    global Dict
    if Dict == {}:
        init_PM25()

    rCounty = Dict[0]['county']
    rSite = Dict[0]['Site']
    value = float(Dict[0]['PM25'])
    new = 0.0
    for i in Dict:
        try:
            new = float(i['PM25'])
        except Exception as e:
            continue

        if new < value:
            rCounty = i['county']
            rSite = i['Site']
            value = new

    outTxt='全台最低 PM2.5 在 {}, {}, {:.2f}'.format(rCounty, rSite, value)
    return outTxt

@app.route('/getmaxpm25')
def getmaxpm25():
    global Dict
    if Dict == {}:
        init_PM25()

    rCounty = Dict[0]['county']
    rSite = Dict[0]['Site']
    value = float(Dict[0]['PM25'])
    new = 0.0
    for i in Dict:
        try:
            new = float(i['PM25'])
        except Exception as e:
            continue

        if new > value:
            rCounty = i['county']
            rSite = i['Site']
            value = new

    outTxt = '全台最高 PM2.5 在 {}, {}, {:.2f}'.format(rCounty, rSite, value)
    return outTxt

def ifSubStringMatch(a,b):
    ret = a.find(b)
    if ret >= 0:
        return True
    else:
        return False


@app.route('/getavecountypm25',methods=['GET'])
def getavecountypm25():
    global Dict

    strCounty = request.args.get('county')
    textIn    = strCounty
    searchtext=strCounty.replace("台", "臺")
    total=0
    lots=0
    for i in Dict:
        if ifSubStringMatch(i['county'], searchtext) == True:
            no = float(i['PM25'])
            total += no
            lots += 1

    if lots == 0:
        lots = 1

    outTxt = '{} 平均 PM2.5 在 {:.2f}'.format(textIn, total/lots)
    return outTxt

@app.route('/getcountrysite',methods=['GET'])
def getcountrysite():
    global Dict
    '''
    textIn = textIn[1:]
    userinp = textIn
    idxNext = textIn.find('#')
    strSite=textIn[idxNext+1:]
    strCountry=textIn[:idxNext]
'''
    strCounty = request.args.get('county')
    userinp   = strCounty
    strCounty=strCounty.replace("台", "臺")

    strSite = request.args.get('site')
    userinp += strSite

    outpm25=0
    lots=0
    for i in Dict:
        if ifSubStringMatch(i['county'], strCounty) == True:
            if ifSubStringMatch(i['Site'], strSite) == True:
                outpm25 = float(i['PM25'])
                break


    if outpm25 == 0:
        outTxt = ' 無此縣市 或 站台'
    else:
        outTxt = '{} PM2.5 是 {:.2f}'.format(userinp, outpm25)

    return outTxt

@app.route('/usage')
def usage():
    outTxt = '網址列輸入 /getminpm25 可得到全台灣 PM2.5 最少的縣市和地區 <br> \
              網址列輸入 /getmaxpm25 可得到全台灣 PM2.5 最嚴重的縣市和地區 <br> \
              輸入 /getavecountypm25?county=縣市，可得到 該縣市內 所有偵測站 平均後的 PM2.5 數值 <br> \
              輸入 /getcountrysite?county=縣市&site=地點，可以提供 該縣市內 在該地點 的 PM2.5 數值'

    return outTxt

if __name__ == '__main__':
    init_pm25()
    app.run()