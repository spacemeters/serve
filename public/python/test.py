#test.py
hostingURL = "http://200.61.170.210:8080/"

from spacemeters import *
def wgetData(urls,host):
    for url in urls:
        folder = url[len(host):url.rfind('/')+1]
        print(folder)
        wget(url, dir = folder)

simNames = ['spectraplot/1.5_1.7/CH4,x=0.000001,T=253K,P=0.53atm,L=1000000cm,simNum0.csv']
simNames.append('spectraplot/1.5_1.7/CH4,x=0.000001,T=253K,P=0.53atm,L=1000000cm,simNum1.csv')
simNames.append('spectraplot/1.5_1.7/CH4,x=0.000001,T=253K,P=0.53atm,L=1000000cm,simNum2.csv')
simNames.append('spectraplot/1.5_1.7/CH4,x=0.000001,T=253K,P=0.53atm,L=1000000cm,simNum3.csv')
simNames.append('spectraplot/1.5_1.7/CH4,x=0.000001,T=253K,P=0.53atm,L=1000000cm,simNum4.csv')
simNames.append('spectraplot/1.5_1.7/CH4,x=0.000001,T=253K,P=0.53atm,L=1000000cm,simNum5.csv')
simNames.append('spectraplot/1.5_1.7/CH4,x=0.000001,T=253K,P=0.53atm,L=1000000cm,simNum6.csv')
simNames.append('spectraplot/1.5_1.7/CH4,x=0.000001,T=253K,P=0.53atm,L=1000000cm,simNum7.csv')

url = 'http://200.61.170.210:8080/spectraplot/1.5_1.7/CH4,x=0.000001,T=253K,P=0.53atm,L=1000000cm,simNum7.csv'
print(url[len(hostingURL):url.rfind('/')+1])
# wgetData(simNames)