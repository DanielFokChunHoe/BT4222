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
        return curYr_dict
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
        #get the mths for the cur yr #previous yr need to parse the pdf directly #might add it in the loop above
        #using 2022 directly, change if necessary
        yrs[2022] = getCurrentYr()

        #prob need add a catch clause here if the fed release the report in december of the same yr or before the january meeting
        #reports_sites = [i if #current year check# in for i in reports_sites[0]]
        return yrs

    def readOldPDF():
        pass
        #using self.years
    def readCurPDF():
        pass

    def bindData():
        #loop through the dict and bind into 1 df
        return self.rbindData



