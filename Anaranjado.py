#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @MMerianus 2017 - Anaranjado.py

import requests
import urllib
import re
from urlparse import urlparse
import argparse
import sys
import datetime
import os


RED   = "\033[1;31m"  
YELLOW   = "\033[0;33m"
ORANGE   = "\033[0;33m"
RESET = "\033[0;0m"
BOLD    = "\033[;1m"
BANNER = """
                                                                                          
       ``                                               :o`                 oh.           
      .dN:                     ``                       :+`                 dM:           
      oMMh   `/-`-++.    `.//-`yd::/:.    `-//-``/.`:+/`.do    `-//-`      -NMh`/yyhs:`   
     :NhmN.  -MmyNyMd  `+dmshMydMNysyy. .odmsdMs+MhdmyMs-Nd  .oddsdMo  ./yydMMdsNo-:sMo   
    .mN:sMs+o/MMN/`dN`/md/``yM+dMo    `+md/``dM:+MMm-.Nd.dm.+md/``dM: +mh/-:mMNNd`  .Md   
   -dMmhdMNs/:MMy  yMhMo` .yMM-dM:   `yNo` -hMM.+MM+ `dN.hNmN+` -hMM`:Nh`  `dNsMh   -My   
   +Ms.``hM: -MN:  sMMm.-smyyM+dM:   -Md.:yNyhM:+Mm`  dN-yMMh.:ymyhM::Nh.`:hMN/Nm. .hN:   
   mm`   :m+ `yy`  oMhhhho- .y+/s.   `+hhho. -h/-ho .-dM-hMyhhyo. -h/ :yhhhsdN-:yhhhh:    
   .`     `        `/` `                `        `  /mNs/mm. `          ``` ``   ```      
                                                     .+yyo.                               
                                                                                          
"""

DESCRIPTION = """
Anaranjado is a scraping tool that identifies URLs within JavaScript files.
"""
AGENT = {'User-agent': 'Anaranjado'}

class AppURLopener(urllib.FancyURLopener):
    version = "Anaranjado"

def infoMessage(text):
	if os.name == 'nt':
		print '[i]- '+text
	else:
		printColoredMessage(YELLOW,'[i]- '+text)

def errorMessage(text):
	if os.name == 'nt':
		print '\n[!]- '+text
	else:
		printColoredMessage(RED,'\n[!]- '+text)

def printColoredMessage(color, message):
	sys.stdout.write(color)
	print message
	sys.stdout.write(RESET)

def getUrl(url):
	urllib._urlopener = AppURLopener()
	url = urlparse(url)
	
	return urllib.urlopen(url.geturl())

def scrapJSFiles(url):
	reg = r"^(?:https?:\/\/)?(?:[\da-z\.-]+)\.(?:[a-z\.]{2,6})([\/\w \.-]*)*\/?$"
	match = re.search(reg, url)
	if match or 'localhost' in url:
		url = urlparse(url)
		response = requests.get(url.geturl(), headers = AGENT)
		regex = r"(?:[^\"|\'])+\.js(?=[\W])"
		matches = re.finditer(regex, response.text)
		jsDomainFiles = {}
		jsNonDomainFiles = {}	
		
		ammount = 0
		for match in matches:
			if match:
				ammount+=1
				infoMessage('JavaScript files detected. Grabbing data, please wait...')
				jsFile = match.group().replace('\\','')
				if url.netloc in jsFile:		#Fix this, as the file could start without the same domain
					jsDomainFiles[jsFile] = 'Same Domain JS Files'
				else: #JS Files outside the domain name
					if 'www' not in jsFile or not jsFile.startswith('http'):
						jsDomainFiles[url.geturl()+jsFile] = 'Same Domain JS Files' #add the file to the list, it is from the same domain
					else:
						jsNonDomainFiles[jsFile] = 'Different Domain JS Files'
		if ammount == 0:
			infoMessage('No JavaScript files were found..')
			return {},{}
		else:
			return jsDomainFiles,jsNonDomainFiles	
	else:
		errorMessage('Please provide a valid URL to start..\n')


def depurate(line):
	char = ',;)(<>"\'@'
	return line.translate(None,char)

def FindHrefSrc(line):
	reg = r"(?:(?:href|src|action)\=(?:\"|\'))(.*?)(?:\"|\')"
	re.compile(reg)
	matches = re.findall(reg, line)
	if matches:
		urls = []
		for match in matches:
			if not match.startswith("#"):
				if not 'javascript' in match:
					match = match.replace('\n','')
					if match:
						urls.append(match)
		return urls


def FindHttpFtp(line): 
	reg = r"(?=https?://|ftp://)([^\s\"\'\)\>]+)" 
	re.compile(reg)
	matches = re.findall(reg, line)
	if matches:
		urls = []
		for match in matches:
			urls.append(match.replace('\n',''))
		return urls


def FindSinglePages(line):
	extensions = ['asp','js','aspx','axd','asx','asmx','ashx','cfm','yaws','Flash','swf','html','htm','xhtml','jhtml','jsp','jspx','wss',
'do','action','pl','php','php4','php3','phtml','py','rb','rhtml','shtml','xml','svg','cgi',
'dll','txt','bkp','sql','cfg','doc','docx','xls','xlsx','pdf','csv','swf','wsdl']
	for ext in extensions:
		if HasExt(line,ext):
			reg = r"(?:[\/|\w|\/|\.|\-|\\|\$])+\."+ext+".+?(?=\(|\-|\"|\'|\<|\>|\/|\s)"
			re.compile(reg)
			matches = re.findall(reg, line)
			if matches:
				urls = []
				for match in matches:
					if not '$' in match:
						if not match.endswith("("):
							urls.append(match.replace('\n',''))
				return urls

def FindSinglePagesWithoutQuotes(line):
	reg = r"(?=[\/]|<).\w+(?:>|\/>)"
	matches = re.findall(reg, line)
	if not matches: 
		reg = r"(?=[\/]).\w+(?:[\/]|[\?|\&|\=|\s|\.]|\w)+"
		re.compile(reg)
		matches = re.findall(reg, line)
		if matches:
			urls = []
			for match in matches:
				urls.append(match.replace('\n',''))
			return urls

def HasForbiddenExtensions(line):
	extensions = ['png','gif','jpg','ico']
	for ext in extensions:
		if HasExt(line,ext):
			return True
	return False

def HasExt(line,ext):
	reg = r"(?:\."+ext+")(?:\W|$)"
	matches = re.findall(reg, line)
	if matches:
		return True
	return False


def harvestUrls(javascriptUrls):
	print '\n'
	infoMessage('Starting JavaScript file parsing...')

	arrCrawledLinks = {}
	arrForbiddenCrawledLinks = {}				# DEVELOP THIS MODULE ##########
	
	for jsUrl in javascriptUrls:
		if not jsUrl.startswith("http"):
			infoMessage('Cannot scrap the file: '+jsUrl)
			continue
			
		infoMessage('Parsing data from: '+jsUrl)
		#jsUrl = urlparse(jsUrl)
		#response = urllib.urlopen(jsUrl.geturl())
		response = getUrl(jsUrl)		
			
		for line in response:
			line = urllib.unquote(line)
			#line = line.replace(' ','')
			urls = FindHttpFtp(line) 
			if urls:
				for url in urls:
					if HasForbiddenExtensions(line):
						arrForbiddenCrawledLinks[url] = 'From: '+ jsUrl
					else:
						arrCrawledLinks[url] = 'From: ' + jsUrl
				continue

			urls = FindSinglePages(line)
			if urls:#remember to create the statistical module
				for url in urls:
					if HasForbiddenExtensions(line):
						arrForbiddenCrawledLinks[url] = 'From: ' + jsUrl
					else:
						arrCrawledLinks[url] = 'From: ' + jsUrl
				continue

			urls = FindHrefSrc(line)
			if urls:#remember to create the statistical module
				for url in urls:
					if HasForbiddenExtensions(line):
						arrForbiddenCrawledLinks[url] = 'From: ' + jsUrl
					else:
						arrCrawledLinks[url] = 'From: ' + jsUrl
				continue
	print '\n'
	if arrCrawledLinks:
		infoMessage('Hey! This is good, some links were found within JavaScript Files:')
		for x in arrCrawledLinks:
			print x + ' ' + arrCrawledLinks[x]
	else:
		infoMessage('Sorry!; No links were found during the scrap work.. But, keep trying!')

def singleJsScraping(url):
	crawled = {}
	crawled[url] = url
	harvestUrls(crawled)

def jsScraping(url, mode):
	crawled = {}
	jsDomainFiles,jsNonDomainFiles = scrapJSFiles(url)
	
	if not jsDomainFiles:
		if not jsNonDomainFiles:
			return
		
	if mode == 'S':
		if jsDomainFiles:
			infoMessage('Same domain JavaScript files:')
			for jsUrls in jsDomainFiles:
				print jsUrls
			crawled = jsDomainFiles
			del jsDomainFiles
	if mode == 'D':
		if jsNonDomainFiles:
			infoMessage('Different domain JavaScript files:')
			for jsUrls in jsNonDomainFiles:
				print jsUrls
			crawled = jsNonDomainFiles
			del jsNonDomainFiles
	if mode == 'B':
		if jsDomainFiles or jsNonDomainFiles:
			infoMessage('All JavaScript files:')
		if jsDomainFiles:
			for jsUrls in jsDomainFiles:
				print jsUrls
		if jsNonDomainFiles:
			for jsUrls in jsNonDomainFiles:
				print jsUrls
		if jsDomainFiles:
			crawled = dict(jsDomainFiles)
			if jsNonDomainFiles:		
				crawled.update(jsNonDomainFiles)
		else:
			if jsNonDomainFiles:
				crawled = dict(jsNonDomainFiles)
	harvestUrls(crawled)


def warmingUp():
	sys.stdout.write(RED)
	parser = argparse.ArgumentParser(description=DESCRIPTION)
	parser.add_argument("--url", help="URL to start scraping JavaScript files. Each .js file will be then parsed to retrieve all stored links. Example: Anaranjado.py --url http://www.testURL.com/")
	parser.add_argument("--jsUrl", nargs=1,help="A single JavaScript Url to scrap for links. Example: Anaranjado.py --jsUrl http://www.testURL.com/myJsFile.js")
	parser.add_argument("--mode", nargs=1, default='B', help="[S] Shows JavaScript files stored at the same domain. [D] Shows JavaScript files stored at a different domain. [B] for both (DEFAULT).")
	
	return parser.parse_args()


if __name__ == "__main__":
	print BANNER
	#start = datetime.datetime.now()
	args = warmingUp()
	sys.stdout.write(RESET)
	if not args.jsUrl:
		if not args.url:
			print 'Maybe you need help. You can try with \'Anaranjado.py -h\'..\n'
		else:
			print infoMessage('Welcome buddy! Please be patient while the hard work is done..')

	if args.jsUrl:
		singleJsScraping(args.jsUrl[0])
	
	if args.url:
		jsScraping(args.url,args.mode[0])
		
	#end = datetime.datetime.now()
	#print (end-start).total_seconds()
		
