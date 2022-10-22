from urllib import request
import re
import requests, PyPDF2
from io import BytesIO
import datetime
import urllib.request

class TweetDataGetter():

    def __init__(self):
        pass

class FOMC():
    def __init__(self):
        self.mainSite = "https://www.federalreserve.gov"
        self.years = getAllYears #storing the individual years in dict
        #self.rbindData = bindData 
    def getLinks(url):
        headers={'User-Agent':user_agent,} 
        req = request.Request(url,None,headers) #The assembled request
        response = request.urlopen(req)
        return re.findall(r"""<\s*a\s*href=["']([^=]+)["']""", response.read().decode("utf-8"))
        #need run else 404 error

    def getCurrentYr():
        #turns out this appears in a different site so adding a separate function
        url = self.mainSite + "/monetarypolicy/fomccalendars.htm"
        urllist = [i for i in getLinks(url) if ".pdf" and "files/fomcminutes" in i]

        curYr_dict = {}
        for i in urllist:
            date = re.findall('[0-9]+', os.path.basename(i))[0]
            if date[:4] == "2022":
                curYr_dict[int(date[4:6])] = mainSite + "/" + i
        return readCurPDF(curYr_dict)

    def readCurPDF(curYr_dict):
        #loop through all the url in curYr_Dict
        for i in curYr_dict.items():
            curYr_dict[i[0]] = parsePDFcurYr(i[1], i[0])
        return curYr_dict

    def parsePDFcurYr(url, month):
        rq = requests.get(url)
        pdf = pdfplumber.open(BytesIO(rq.content))
        pgs = ""
        #skipping pg 1 since it always is the names of the parties involved 
        #in retrospect, the name may affect outcome?
        for i in range(2,len(pdf.pages)): #range(startPg, endPg) future update
            page = pdf.pages[i]
            #done because pdf is split in 2 halves, and to bypass merged words issue
            left = page.crop((0, 0.1 * float(page.height), 0.5 * float(page.width), 1 * float(page.height)))
            right = page.crop((0.5 * float(page.width), 0.1 * float(page.height), page.width, 1 * float(page.height)))
            pgs += left.extract_text().replace("\n", " ") + " " + right.extract_text().replace("\n"," ")   

        pgs = pgs.replace("- ","")
        pgs = " ".join(pgs.split())

        if month == 1 or month == 2: #2 due to scheduling differences
            temp = []
            pgs = pgs[pgs.find("AUTHORIZATION FOR DOMESTIC OPEN MARKET OPERATIONS"):]
        else:
            pgs = pgs[pgs.find("Developments in Financial Markets and Open Market Operations"):]
        return pgs.rsplit('Voting for this action', 1)[0]
        #returns a dict with month as key, text as value, url is removed

    def getAllYears():
        #go to site and get the links for each of the previous years available
        url = self.mainSite + "/publications/annual-report.htm"

        urllist = [i for i in getLinks(url) if ".pdf" in i][:-1]
        reports_sites = [i if "federalreserve.gov/" in i else mainSite + i for i in urllist]
        reports_sites = set(reports_sites)

        #filters the html to get the yr. stored as nested dict, yrs [#year][#1 entry called sites]
        yrs = {}
        for i in reports_sites:
            try:
                yr = re.findall('[0-9]+', os.path.basename(i))[0]
            except:
                yr = re.findall('[0-9]+',i)[0]
            if len(yr) == 2:
                yr = "19" + yr if int(yr) > 94 else "20" + yr
            yrs[int(yr)] = {"site" : i}
        #using 2022 directly, change if necessary
        yrs[2022] = getCurrentYr()

        #prob need add a catch clause here if the fed release the report in december of the same yr or before the january meeting
        #reports_sites = [i if #current year check# in for i in reports_sites[0]]
        return yrs

    def readOldPDF():
        pass
        #using self.years

    def bindData():
        #loop through the dict and bind into 1 df
        return self.rbindData



