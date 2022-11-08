from urllib import request
import re
from io import BytesIO
import datetime
import requests, pdfplumber
from urllib import request
import pandas as pd
import nltk
nltk.download('stopwords')
nltk.download('wordnet')
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer 
from nltk.stem.snowball import SnowballStemmer
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tokenize import sent_tokenize, word_tokenize
import matplotlib.pyplot as plt
import numpy as np
from nltk.sentiment import SentimentIntensityAnalyzer
%matplotlib notebook

class TweetDataGetter():

    def __init__(self):
        pass

#note that initialisation will take time
class FOMC():
    def __init__(self):
        self.mainSite = "https://www.federalreserve.gov"
        self.yrs = self.getAllYears() #storing the individual years in dict
        self.rbindData = self.bindData()

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

    def parseHTML(self, site, date):
        pgs = requests.get(site, auth=('user', 'pass'))
        pgs = str(BeautifulSoup(pgs.text, 'lxml'))
        pgs = re.sub(r"<.*?>|\xad|amp;|\xa0", "", pgs)
        pgs = re.sub(r"â\x80\x91|â\x80\x94|x92|x94|21â\x80\x9322|\n|\r|\t", " ", pgs)
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
            return yrs

    #breaking each report down to individual sentences
    def clearing(txt):
        temp = re.split("\.\s",txt)
        temp = [re.sub('\si$|\sii$|\siii$|\siv$|\sv$|\svi$|\svii$|\sviii$|\six$|\sx$|\sxi$|\sxii$|\sxv$',"",i) for i in temp]
        temp = [re.sub('--'," ",i) for i in temp]
        temp = [re.sub(r'[()]|\'|\,',"",i) for i in temp]
        temp = [re.split("[:]|[;]",i)[0] for i in temp]
        return([i for i in temp if len(i)>4])

    def bindData(self):
        main =  pd.DataFrame.from_dict({
            "years": [i for i in self.yrs.keys() for j in self.yrs[i].keys()], 
            "months": [j for i in self.yrs.keys() for j in self.yrs[i].keys()],
            "text": [j[1] for i in self.yrs.keys() for j in self.yrs[i].items()]})
        for i in range(len(main)):
            main['text'][i] = clearing(main['text'][i])
        self.rbindData = main
        self.process()
        return main

    def text_clean(corpus, keep_list):
        cleaned_corpus = pd.Series()
        for row in corpus:
            qs = []
            for word in row.split():
                if word not in keep_list:
                    p1 = re.sub(pattern='[^a-zA-Z0-9]',repl=' ',string=word)
                    p1 = p1.lower()
                    qs.append(p1)
                else : qs.append(word)
            cleaned_corpus = cleaned_corpus.append(pd.Series(' '.join(qs)))
        return cleaned_corpus

    def lemmatize(corpus):
        lem = WordNetLemmatizer()
        corpus = [[lem.lemmatize(x, pos = 'v') for x in x] for x in corpus]
        return corpus

    def stopwords_removal(corpus):
        fedNames = ['mr',"phillips","treasury",'yellen','minehan','rivlin','stern',"messrs",'corrigan','meyer','jordan',
                'broaddus','laware','mcteer','mcdonough','pianalto','poole','fisher','evans','vote',"kelley",
                'gramlich','ms','duke','moskow','mullins','bies', 'lindsey', 'olson', 'stewart', 'angell', 
                    'greenspan','mses','melzer','bernanke','hoenig','ferguson','geithner','absent','blinder',
                    'boehne', 'kohn', 'keehn', 'meyers', 'santomero', 'kroszner', 'oltman', 'mishkin']
        monthName = ["january",'february',"march",'april','may','june','july','august','september',"october",
                    'november',"december"]
        weirdOccurances = ['u','k']
        yrName = [str(i) for i in range(1993,2030)]
        stop = stopwords.words('english') + fedNames + monthName + yrName + weirdOccurances
        corpus = [[x for x in x.split(" ") if x not in stop] for x in corpus]
        return corpus

    def preprocess(corpus, keep_list, cleaning = True, lemmatization = False, remove_stopwords = True):    
        if cleaning == True:
            corpus = text_clean(corpus, keep_list)
        if remove_stopwords == True:
            corpus = stopwords_removal(corpus)
        else :
            corpus = [[x for x in x.split(" ")] for x in corpus]
        if lemmatization == True:
            corpus = lemmatize(corpus)
        corpus = [' '.join(x) for x in corpus]        
        return corpus

    def getWordDist(self, s_a):
        #merge text then tokenize?
        chunck = ''
        for i in s_a['text']:
            if i.isalpha():
                chunck += " " + i
            
        words: list[str] = word_tokenize(chunck)
        return nltk.FreqDist(words)    

    def process(self):
        mainls, dateinfo = [],[]
    
        for i in range(len(self.rbindData)):
            temp = [re.sub(r'\-\s|\'|\"','', j) for j in self.rbindData['text'][i]]
            mainls += temp
            dateinfo += [str(self.rbindData['years'][i]) + "-" + str(self.rbindData['months'][i]) for j in range(len(self.rbindData['text'][i]))]

        #s_a aka sentiment_analysis
        s_a = pd.DataFrame({"dm": dateinfo,"text":mainls})
        processedTxt = preprocess(s_a['text'], keep_list = [],lemmatization = True)
        s_a['text'] = processedTxt
        self.wordDist = self.getWordDist(s_a.copy())
        self.allSentiment = self.getTotalSentiment(s_a.copy())
        self.getMonthlySentiment()

    def mostCommonWords(self):
        return [i[0] for i in self.wordDist.most_common(100)]

    def totalSentimentHistogram(self):
        plt.hist([i for i in self.allSentiment['compound']], bins=50)
        plt.show()

    def getTotalSentiment(self, s_a):
        sia = SentimentIntensityAnalyzer()
        s_a['sentiment'] = [sia.polarity_scores(i) for i in s_a['text']]
        s_a['compound'] = [i['compound'] for i in s_a['sentiment']]
        return s_a.drop(['sentiment'], axis=1)

    def monthlySentimentGraph(self):
        avgResults = self.monthlySentiment.copy()
        plt.rcParams["figure.figsize"] = (9,4)
        plt.plot(avgResults["dm"],avgResults["compound"], c = 'g')
        plt.show()

    def getMonthlySentiment(self):
        avgResults = self.allSentiment.copy()
        avgResults = avgResults.drop(['text'], axis=1)
        self.monthlySentiment = avgResults.groupby(['dm'],as_index = False).mean()
        
    def saveOut(self):
        self.rbindData.to_csv("scrapedData.csv",index=False)


        
#main calls, assuming final = FOMC()
#final.allSentiment
#final.monthlySentiment
#final.wordDist
#final.mostCommonWords()
#final.totalSentimentHistogram()
#final.monthlySentimentGraph()
#final.rbindData