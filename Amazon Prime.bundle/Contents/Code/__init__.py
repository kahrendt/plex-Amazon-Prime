# -*- coding: utf-8 -*-
import re
import operator
import urllib
import time
import cookielib
from base64 import b64decode

NAME = "Amazon Video on Demand"
ICON = "icon-default.png"
ART = "art-default.jpg"

ASSOC_TAG = "plco09-20"
####################################################################################################

def Start():
	Plugin.AddPrefixHandler("/video/amazonvod", MainMenu, NAME, ICON, ART)

	Plugin.AddViewGroup("List", viewMode="List", mediaType="items")


	MediaContainer.title1 = NAME
	MediaContainer.art = R(ART)
	MediaContainer.viewGroup = "List"

	DirectoryItem.thumb = R(ICON)



	####################################################################################################

def MainMenu():
    dir = MediaContainer(viewMode="List")

    usedSelections={'genre':False, 'network':False}
    
    dir.Append(Function(DirectoryItem(MovieList, "Movies")))

    dir.Append(Function(DirectoryItem(TVList, "TV"), url="/s/ref=sr_nr_n_1?rh=n%3A2625373011%2Cn%3A%212644981011%2Cn%3A%212644982011%2Cn%3A2858778011%2Cp_85%3A2470955011%2Cn%3A2864549011&bbn=2858778011&ie=UTF8&qid=1334413870&rnid=2858778011", usedSelections=usedSelections))

    dir.Append(Function(DirectoryItem(SearchMenu, "Search")))
    
    dir.Append(Function(DirectoryItem(Library, "Your Library")))

    dir.Append(PrefsItem(L('Preferences'), thumb=R(ICON)))
    return dir


def SearchMenu(sender):
    dir = MediaContainer(viewMode="List")
    dir.Append(Function(InputDirectoryItem(Search, "Search Movies", "Search Amazon Prime for Movies", thumb = R(ICON)), tvSearch=False))
    dir.Append(Function(InputDirectoryItem(Search, "Search TV Shows", "Search Amazon Prime for TV Shows", thumb = R(ICON))))
    
    
    return dir


def Search(sender, query, url = None, tvSearch=True):
    string = "/s/ref=sr_nr_n_0?rh=n%3A2625373011%2Cn%3A%212644981011%2Cn%3A%212644982011%2Cn%3A2858778011%2Ck%3A"


    string += urllib.quote_plus(query)
    
    if tvSearch:
        string += "%2Cp_85%3A2470955011%2Cn%3A2864549011&bbn=2858778011&keywords="
    else:
        string += "%2Cp_85%3A2470955011%2Cn%3A2858905011&bbn=2858778011&keywords="
    string += urllib.quote_plus(query)


    if tvSearch:
        return ResultsList(None, url=string, onePage=True)
    else:
        return ResultsList(None, url=string, onePage=True, tvList = False)



def Login():
    x = HTTP.Request('https://www.amazon.com/?tag=%s' % ASSOC_TAG, errors='replace')
    x = HTTP.Request('https://www.amazon.com/gp/sign-in.html?tag=%s' % ASSOC_TAG, errors='replace')
    cookies = HTTP.GetCookiesForURL('https://www.amazon.com/gp/sign-in.html?tag=%s' % ASSOC_TAG)

    sessId = None
    

    
    params = {
        'path': '/gp/homepage.html',
        'useRedirectOnSuccess': '1',
        'protocol': 'https',
        'sessionId': sessId,
        'action': 'sign-in',
        'password': Prefs['password'],
        'email': Prefs['username'],
        'x': '62',
        'y': '11'
    }
    x = HTTP.Request('https://www.amazon.com/gp/flex/sign-in/select.html?ie=UTF8&protocol=https&tag=%s' % ASSOC_TAG,values=params,errors='replace')



    

def Library(sender):
    Login()
    dir = MediaContainer(viewMode="List")
    
    dir.Append(Function(DirectoryItem(LibrarySpecific, "Movies"), movies=True))
    dir.Append(Function(DirectoryItem(LibrarySpecific, "TV"), movies=False))
    
    return dir
    
def LibrarySpecific(sender, movies=True):
    pageList = HTTP.Request("https://www.amazon.com/gp/video/library")
    if movies:
        pageList = HTTP.Request("https://www.amazon.com/gp/video/library/movie?show=all")
    else:
        pageList = HTTP.Request("https://www.amazon.com/gp/video/library/tv?show=all")
    
    element = HTML.ElementFromString(pageList.content)
    
    purchasedList = element.xpath('//*[@class="lib-item"]')
    videos = list()
    seasons = list()
    
    for i in range(0, len(purchasedList)):
        asin = purchasedList[i].xpath('//@asin')[0]
        imageLink = purchasedList[i].xpath('//div/a/img/@src')[0]
        title = purchasedList[i].xpath('//*[@class="title"]/a/text()')[0]
        
        if purchasedList[i].xpath('//div/@type')[0] == "movie":    
            videos.append((title, asin, imageLink))
        else:
            seasons.append((title, asin, imageLink))
        

    dir = MediaContainer(viewMode="List")
    
    for i in range(0, len(videos)):
        dir.Append(
                WebVideoItem(
                url="http://www.amazon.com/gp/video/streaming/mini-mode.html?asin=" + videos[i][1],
                title = videos[i][0],
                thumb=Callback(Thumb, url=videos[i][2] )
                )
            )
    
    for i in range(0, len(seasons)):
        dir.Append(Function(DirectoryItem(TVIndividualSeason, title=seasons[i][0], thumb=Callback(Thumb, url=seasons[i][2] )), url="https://www.amazon.com/gp/product/" + seasons[i][1]))

    return dir
    

    



def MovieList(sender, url=None, usedSelections = None):
    dir = MediaContainer(viewMode="List")

    dir.Append(Function(InputDirectoryItem(Search, "Search Movies", "Search Amazon Prime for Movies", thumb = R(ICON)), tvSearch=False))

    return dir


    
def TVList(sender, url=None, usedSelections = None):

    
    dir = MediaContainer(viewMode="List")
    
    shownUnorganized = False
    
    tvPage = HTML.ElementFromURL("http://www.amazon.com" + url)
    
    links = tvPage.xpath("//div[@id='refinements']//h2[. = 'TV Show']/following-sibling::ul[1 = count(preceding-sibling::h2[1] | ../h2[. = 'TV Show'])]/li/a/@href")    

    if (len(links) > 0):
        tvShowsLink = links[len(links)-1]
        
        if "sr_sa_p_lbr_tv_series_brow" in tvShowsLink:
            dir.Append(Function(DirectoryItem(TVShows, "Shows"), url=tvShowsLink))
        else:
            dir.Append(Function(DirectoryItem(TVShowsNotNice, "Shows"), url=url))

    else:
        dir.Append(Function(DirectoryItem(ResultsList, "All TV Shows (Unorganized)"), url=url, onePage=True))
        shownUnorganized = True
        
            
    if not usedSelections['genre']:
        links = tvPage.xpath("//div[@id='refinements']//h2[. = 'Genre']/following-sibling::ul[1 = count(preceding-sibling::h2[1] | ../h2[. = 'Genre'])]/li/a/@href")
        if len(links) > 0:
            genresLink = links[len(links)-1]
        
            if "sr_sa_p_n_theme_browse-bin" in genresLink:
                dir.Append(Function(DirectoryItem(TVSubCategories, "Genres"), url=genresLink, category="Genre", usedSelections=usedSelections ))
            else:
                dir.Append(Function(DirectoryItem(TVNotNiceSubCategories, "Genres"), url=url, category="Genre", usedSelections=usedSelections ))
            
            
            
    if not usedSelections['network']:
        links = tvPage.xpath("//div[@id='refinements']//h2[. = 'Content Provider']/following-sibling::ul[1 = count(preceding-sibling::h2[1] | ../h2[. = 'Content Provider'])]/li/a/@href")
        if len(links) > 0:
            networksLink = links[len(links)-1]

            if "sr_sa_p_studio" in networksLink:
                dir.Append(Function(DirectoryItem(TVSubCategories, "Networks"), url=networksLink, category="Content Provider", usedSelections=usedSelections ))
            else:
                dir.Append(Function(DirectoryItem(TVNotNiceSubCategories, "Networks"), url=url, category="Content Provider", usedSelections=usedSelections ))    
    

    if not shownUnorganized:
        dir.Append(Function(DirectoryItem(ResultsList, "All TV Shows (Unorganized)"), url=url, onePage=True))

        
        
   
        
    return dir
    
    
    
        



def TVSubCategories(sender, url=None, category=None, usedSelections=None):
    if category=='Content Provider':
        usedSelections['network'] = True
        
    if category=='Genre':
        usedSelections['genre'] = True
    
    
    tvGenrePage = HTML.ElementFromURL("http://www.amazon.com" + url)
    
    listOfGenresLinks = tvGenrePage.xpath("//*[@class='c3_ref refList']//a/@href")
    listOfGenres = tvGenrePage.xpath("//*[@class='c3_ref refList']//a")
    listOfGenresNames = listOfGenres[0].xpath("//*[@class='refinementLink']/text()")
    
    
    dir = MediaContainer(viewMode="list")
    
    for i in range(0, len(listOfGenresLinks)):
        dir.Append(Function(DirectoryItem(TVList, title=listOfGenresNames[i]), usedSelections=usedSelections, url=listOfGenresLinks[i]))
    
    return dir



def TVNotNiceSubCategories(sender, url=None, category=None, usedSelections=None):
    if category=='Content Provider':
        usedSelections['network'] = True
        
    if category=='Genre':
        usedSelections['genre'] = True


    tvGenrePage = HTML.ElementFromURL("http://www.amazon.com" + url)
    
    genreList = tvGenrePage.xpath("//div[@id='refinements']//h2[. = '" + category + "']/following-sibling::ul[1 = count(preceding-sibling::h2[1] | ../h2[. = '" + category + "'])]//*[@class='refinementLink']/text()")
    
    genreLinks = tvGenrePage.xpath("//div[@id='refinements']//h2[. = '" + category + "']/following-sibling::ul[1 = count(preceding-sibling::h2[1] | ../h2[. = '" + category + "'])]/li/a/@href")
    
    pairs = list()
    
    
    for i in range(0, len(genreList)):
        pairs.append((genreList[i], genreLinks[i]))
        
    sortedPairs = sorted(pairs, key=operator.itemgetter(0))
              
    dir = MediaContainer(viewMode="list")
        
    for i in range(0, len(genreList)):
        dir.Append(Function(DirectoryItem(TVList, title=sortedPairs[i][0]), usedSelection=usedSelection, url=sortedPairs[i][1]))
    
    return dir

    
    
    
    
    
    

def TVShows(sender, url=None):
    tvShowPage = HTML.ElementFromURL("http://www.amazon.com" + url)
    
    listOfShowsLinks = tvShowPage.xpath("//*[@class='c3_ref refList']//a/@href")
    listOfShows = tvShowPage.xpath("//*[@class='c3_ref refList']//a")
    
    dir = MediaContainer(viewMode="list")
    
    if len(listOfShows) > 0:
        listOfShowsNames = listOfShows[0].xpath("//*[@class='refinementLink']/text()")
    

        
    
        for i in range(0, len(listOfShowsLinks)):
            dir.Append(Function(DirectoryItem(ResultsList, title=listOfShowsNames[i]), url=listOfShowsLinks[i], sort=True))
    
    return dir
    


def TVShowsNotNice(sender, url=None):
    tvGenrePage = HTML.ElementFromURL("http://www.amazon.com" + url)
    
    showList = tvGenrePage.xpath("//div[@id='refinements']//h2[. = '" + "TV Show" + "']/following-sibling::ul[1 = count(preceding-sibling::h2[1] | ../h2[. = '" + "TV Show" + "'])]//*[@class='refinementLink']/text()")
    
    showLinks = tvGenrePage.xpath("//div[@id='refinements']//h2[. = '" + "TV Show" + "']/following-sibling::ul[1 = count(preceding-sibling::h2[1] | ../h2[. = '" + "TV Show" + "'])]/li/a/@href")
    
    pairs = list()
    
    
    for i in range(0, len(showList)):
        pairs.append((showList[i], showLinks[i]))
        
    sortedPairs = sorted(pairs, key=operator.itemgetter(0))
              
    dir = MediaContainer(viewMode="list")
        
    for i in range(0, len(showList)):
        dir.Append(Function(DirectoryItem(TVList, title=sortedPairs[i][0]), url=sortedPairs[i][1]))
    
    return dir



def ResultsList(sender, url = None, onePage=False, tvList = True, sort=False):     
    
    dir = MediaContainer(viewMode="list")

    seasonsPage = HTML.ElementFromURL("http://www.amazon.com" + url)
    seasons = list()
    
    newURL = ""
    
    if (len(seasonsPage.xpath('//*[@class="pagnNext"]')) > 0) and not onePage:
        nextLoopQuit = False
    else:
        nextLoopQuit = True

    
    while True:
        if len(seasonsPage.xpath("//*[@id='atfResults' or @id='btfResults']")) > 0:
            listOfSeasons = seasonsPage.xpath("//*[@id='atfResults' or @id='btfResults']")[0]
    
            listOfSeasonsNames = listOfSeasons.xpath('//*[@class="title"]/a/text()')
            listOfSeasonsLinks = listOfSeasons.xpath('//*[@class="title"]/a/@href')
            listOfSeasonsImages = listOfSeasons.xpath('//*[@class="image"]/a/img/@src')
            
            Log(listOfSeasonsLinks[0].partition('/ref=sr_')[0].rpartition('/dp/')[2])

            for i in range(0, len(listOfSeasonsNames)):
                seasons.append((listOfSeasonsNames[i], listOfSeasonsLinks[i], listOfSeasonsImages[i], listOfSeasonsLinks[i].partition('/ref=sr_')[0].rpartition('/dp/')[2]))

           
            try:
                newURL = seasonsPage.xpath('//*[@id="pagnNextLink"]')[0].xpath('@href')[0]        
            except:
                break
                
            if nextLoopQuit:
                break
        
            
            seasonsPage = HTML.ElementFromURL("http://www.amazon.com" + newURL) 
            
            if (len(seasonsPage.xpath('//*[@class="pagnNext"]')) > 0):
                nextLoopQuit = False
            else:
                nextLoopQuit = True
        else:
            return MessageContainer("Sorry, no results.", "")
    
    sortedSeasonPairs = seasons
    
    if sort:
        sortedSeasonPairs = sorted(seasons, key=operator.itemgetter(0))


    if tvList:
        for i in range(0, len(sortedSeasonPairs)):
            dir.Append(Function(DirectoryItem(TVIndividualSeason, title=sortedSeasonPairs[i][0], thumb=Callback(Thumb, url=sortedSeasonPairs[i][2] )), url=sortedSeasonPairs[i][1]))
    else:
        for i in range(0, len(sortedSeasonPairs)):
            dir.Append(
            WebVideoItem(
                url="http://www.amazon.com/gp/video/streaming/mini-mode.html?asin=" + sortedSeasonPairs[i][3],
                title = sortedSeasonPairs[i][0],
                thumb=Callback(Thumb, url=sortedSeasonPairs[i][2] )
                )
            )
            

    if onePage and len(newURL) > 0:
        dir.Append(Function(DirectoryItem(ResultsList, title="Next Page"), url=newURL, onePage = True))

    return dir
    
    
def TVIndividualSeason(sender, url = None):
    episodesPage = HTML.ElementFromURL(url)
    
    listOfEpisodesTable = episodesPage.xpath('//*[@class="episodeRow" or @class="episodeRow current"]')
    
    listOfEpisodesTitles = list()
    listOfEpisodesASIN = list()
    listOfEpisodesSummaries = list()
    
    for i in range(0, len(listOfEpisodesTable)):
        listOfEpisodesTitles.append(listOfEpisodesTable[i].xpath('td/div/text()')[0])
        listOfEpisodesASIN.append(listOfEpisodesTable[i].xpath('@asin')[0])
        listOfEpisodesSummaries.append(listOfEpisodesTable[i].xpath('td/div/text()')[1])

    dir = MediaContainer(viewMode="list")
    
    for i in range(0, len(listOfEpisodesTable)):
        dir.Append(
            WebVideoItem(
                url="http://www.amazon.com/gp/video/streaming/mini-mode.html?asin=" + listOfEpisodesASIN[i],
                title = listOfEpisodesTitles[i],
                summary = listOfEpisodesSummaries[i]
                )
            )
    
    
    return dir
    
def Thumb(url):
    try:
        data = HTTP.Request(url, cacheTime = CACHE_1MONTH).content
        return DataObject(data, 'image/jpeg')
    except:
        return Redirect(R(ICON))
