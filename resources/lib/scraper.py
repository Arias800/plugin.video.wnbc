# -*- coding: utf-8 -*-
# WNBC Kodi Video Addon
#
from t1mlib import t1mAddon

import re
import xbmcplugin
import xbmcgui
import xbmc
import sys
import requests
import urllib.parse

class myAddon(t1mAddon):

    def getAddonMenu(self, url, ilist):
        a = requests.get('https://friendship.nbc.co/v2/graphql?extensions=%7B%22persistedQuery%22:%7B%22namedHash%22:%22page.v5%22%7D%7D&variables=%7B%22name%22:%22allShows%22,%22type%22:%22PAGE%22,%22userId%22:%22-6407222222222222222%22,%22platform%22:%22web%22,%22device%22:%22web%22,%22timeZone%22:%22America%2FNew_York%22%7D', headers=self.defaultHeaders).json()
        a = a["data"]["page"]["sections"][0]["data"]["items"][0]["data"]["items"]
        mode = 'GE'
        for b in a:
            b = b["data"]
            name = b['title']
            infoList = {'mediatype': 'tvshow',
                        'TVShowTitle': name,
                        'Title': name}
            url = b['urlAlias']
            thumb = b['image']
            fanart = thumb
            contextMenu = [(self.addon.getLocalizedString(30002), 'RunPlugin(%s?mode=%s&url=%s)' % (sys.argv[0], mode, url))]
            ilist = self.addMenuItem(name, 'GE', ilist, url, thumb, fanart, infoList, isFolder=True, cm=contextMenu)
        return(ilist)

    def getAddonEpisodes(self, url, ilist):
        a = requests.get(''.join(['https://friendship.nbc.co/v2/graphql?extensions=%7B%22persistedQuery%22:%7B%22namedHash%22:%22page.v4%22%7D%7D&variables=%7B%22name%22:%22',url,'%22,%22type%22:%22SERIES%22,%22userId%22:%22-6407222222222222222%22,%22platform%22:%22web%22,%22device%22:%22web%22%7D']), headers=self.defaultHeaders).json()
        for b in a['data']['page']['sections']:
            if b['component'] != 'LinksSelectableGroup':
                continue
            for c in b['data']['items']:
                if c['component'] != 'Shelf':
                    continue
                for b in c['data']['items']:
                    b = b['data']
                    if b['programmingType'] != 'Full Episode':
                        continue

                    infoList = {}
                    name = b['secondaryTitle']
                    url = ''.join(['https://link.theplatform.com/s/NnzsPC/media/guid/2410887629/', b['mpxGuid']])
                    print(url)
                    thumb = b['image']
                    fanart = thumb
                    infoList['Title'] = name
                    season = b.get('seasonNumber', False)
                    if season:
                        infoList['Season'] = int(season)
                    episode = b.get('episodeNumber', False)
                    if episode:
                        infoList['Episode'] = int(episode)
                    duration = b.get('duration', False)
                    if duration:
                        infoList['Duration'] = int(duration)
                    infoList['TVShowTitle'] = b.get('seriesShortTitle')
                    infoList['Plot'] = b.get('description')
                    infoList['Studio'] = 'NBC'
                    infoList['mediatype'] = 'episode'
                    ilist = self.addMenuItem(name, 'GV', ilist, url, thumb, fanart, infoList, isFolder=False)
        return(ilist)

    def getAddonVideo(self, url):
        if xbmc.getCondVisibility('system.platform.android'):
            #playready stream with better quality
            url = url + '?policy=43674&player=NBC.com%20Instance%20of%3A%20rational-player-production&formats=m3u,mpeg4&embedded=true&tracking=true'
        else:
            url = url + '?mbr=true&manifest=m3u&switch=HLSServiceSecure'
        liz = xbmcgui.ListItem(path=url)
        liz.setProperty('inputstream', 'inputstream.adaptive')
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)
