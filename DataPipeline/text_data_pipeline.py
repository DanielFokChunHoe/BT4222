from urllib import request
import re
from io import BytesIO
import datetime
import requests, pdfplumber
from urllib import request
import pandas as pd


class TweetDataGetter():

    def __init__(self):
        pass

#note that within the strings, " was changed to  _quote_
class FOMC():
    def __init__(self):
        self.mainSite = "https://www.federalreserve.gov"
        self.yrs = self.getAllYears() #storing the individual years in dict
        self.rbindData = bindData()

    def yrChunk(yrs,links):
        years = set([re.findall('[0-9]+', os.path.basename(i))[0][:4] for i in links])
        for i in years:
            temp = [j for j in links if i in j]
            curYr = {}
            for j in temp:
                date = re.findall('[0-9]+', os.path.basename(j))[0]
                #actually from here can call the function if done
                curYr[int(date[4:6])] = parseHTML(j,date)
            yrs[int(i)] = curYr
        return yrs

    def miniTweaks(self, yrs):
        yrs[2010][8] = yrs[2010][8].rsplit("Return to text",1)[0]
        yrs[2020][3] = yrs[2020][3].rsplit("Voting",1)[0]
        return(yrs)

    def parseHTML(self, site, date):
        pgs = requests.get(site, auth=('user', 'pass'))
        pgs = str(BeautifulSoup(pgs.text, 'lxml'))
        pgs = re.sub(r"<.*?>|\xad|amp;|\xa0", "", pgs)
        pgs = re.sub(r"â\x80\x91|â\x80\x94|x92|x94|\n|\r|\t", " ", pgs)
        pgs = re.sub(r' +', ' ', pgs)
        pgs = re.sub('"',"_quote_",pgs)
        
        if 'Votes for:' in pgs:
            pgs = pgs.rsplit('Votes for:', 1)[0]
        elif "Votes for this action:" in pgs:
            pgs = pgs.rsplit('Votes for this action:', 1)[0]
        else:
            pgs = pgs.rsplit("Voting for this action", 1)[0]
        
        #this one is more or less
        if int(date) > 20120101:
            if int(date[4:6]) == 1 or int(date[4:6]) == 2: #2 due to scheduling differences
                pgs = pgs[pgs.find("AUTHORIZATION FOR DOMESTIC OPEN MARKET OPERATIONS"):]
            else:
                if "Developments in Financial Markets" in pgs:
                    pgs = pgs[pgs.find("Developments in Financial Markets"):]
                else:
                    pgs = pgs[pgs.find("Discussion of Financial Markets and Open Market Operations"):]
            return pgs.rsplit(' for this action:', 1)[0]
        
        elif int(date) < 20071031:
            if int(date[4:6]) == 1 or int(date[4:6]) == 2: #2 due to scheduling differences
                if date == "19950201":
                    pgs = pgs[pgs.find("The Committee then turned to a discussion of the"):] 
                else:
                    pgs = pgs[pgs.find("Authorization for Domestic Open Market Operations"):]
            else:
                try:
                    if date == '20070628':
                        pgs = pgs[pgs.find("The information reviewed"):]
                    elif "The Committee then turned to a discussion of the" in pgs:
                        pgs = pgs[pgs.find("The Committee then turned to a discussion of the"):]  
                    else: #if "the Committee ratified these transactions." in pgs:
                        pgs = pgs.split("By unanimous vote, the Committee ratified these transactions.",1)[1]
                except:
                    print(pgs)
            if ' for this action:' not in pgs:
                if 'Votes for:' not in pgs:
                    return pgs.rsplit("It was agreed that the next meeting",1)[0]
            return pgs
        else:
            if int(date[4:6]) == 1 or int(date[4:6]) == 2: #2 due to scheduling differences
                pgs = pgs[pgs.find("AUTHORIZATION FOR DOMESTIC OPEN MARKET OPERATIONS"):]
            else:
                try:
                    if int(date[:4]) < 2009:
                        if "By unanimous vote, the Committee ratified these transactions." in pgs:
                            pgs = pgs.split("By unanimous vote, the Committee ratified these transactions.",1)[1]
                    else:
                        pgs = pgs[pgs.find("Developments in Financial Markets"):]
                except:
                    print(pgs)
            return pgs

    def getAllYears(self): 
        yrs = {}      
        site = self.mainSite + "/monetarypolicy/fomccalendars.htm"
        r = requests.get(site, auth=('user', 'pass'))
        links = re.findall(r"""<\s*a\s*href=["']([^=]+)["']""", r.text)
        links = [self.mainSite + i for i in links if ".htm" and "monetarypolicy/fomcminutes" in i]

        #get the smallest yr from main
        startYr = int(min([re.findall('[0-9]+', os.path.basename(i))[0][:4] for i in links]))
        yrs = yrChunk(yrs, links)

        #93 the website change
        for i in range(1993,startYr):
            site = "https://www.federalreserve.gov/monetarypolicy/fomchistorical" + str(i) + ".htm"
            r = requests.get(site, auth=('user', 'pass'))
            links = re.findall(r"""<\s*a\s*href=["']([^=]+)["']""", r.text)
            links = [self.mainSite + i for i in links if ".htm" in i]

            #07' oct, website changed
            #12, website changed #same url though
            if i < 2007:
                links = [i for i in links if "fomc/minutes/" in i.lower()]
            elif i == 2007:
                link1 = [i for i in links if "fomc/minutes/" in i.lower()]
                links = link1 + [i for i in links if "monetarypolicy/fomcminutes" in i.lower()]
            else:
                links = [i for i in links if "monetarypolicy/fomcminutes" in i.lower()]
            links = [i for i in links if "#" not in i] #some have hash
            yrs = yrChunk(yrs, links)
            
            return miniTweaks(yrs)

    def bindData(self):
        self.rbindData =  pd.DataFrame.from_dict({
            "years": [i for i in self.yrs.keys() for j in self.yrs[i].keys()], 
            "months": [j for i in self.yrs.keys() for j in self.yrs[i].keys()],
            "text": [j[1] for i in self.yrs.keys() for j in self.yrs[i].items()]})