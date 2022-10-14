import urllib.requests
import re

class TweetDataGetter():

    def __init__(self):
        pass

class FOMC():
    def __init__(self):
        self.url = "https://www.federalreserve.gov/publications/annual-report.htm"
        self.yrs = {} #storing the individual years in dict
        self.rbindData = "" 

    def getAllYears():
        #go to site and get the links for each of the previous years available
        headers={'User-Agent':user_agent,} 
        request=urllib.request.Request(url,None,headers) #The assembled request

        response = urllib.request.urlopen(request)
        urllist = re.findall(r"""<\s*a\s*href=["']([^=]+)["']""", response.read().decode("utf-8"))
        urllist = [i for i in urllist if ".pdf" in i][:-1]
        reports_sites = [i if "federalreserve.gov/" in i else 'https://www.federalreserve.gov' + i for i in urllist]

        report_sites.append(getCurrentYr)

        #prob need add a catch clause here if the fed release the report in december of the same yr or before the january meeting
        #reports_sites = [i if #current year check# in for i in reports_sites[0]]
        return reports_sites  

    def getCurrentYr():
        #turns out this appears in a different site so adding a separate function
        return 

    #TBD
    def getData():
        FOMCLinks = getAllYears
        #using number of links to loop to the sites
        for i in FOMCLinks:
            #self.yrs[i] = urllib.request( #new url +  i if possible) #storing in the dictionary

        #return self.yrs

    def bindData():
        #for i in self.yrs():
            #bind the dictionary
            #rbindData #df form
        return self.rbindData



