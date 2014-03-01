#!/usr/local/bin/python

# !/usr/bin/env python

import gdata.photos.service
import gdata.media
import gdata.geo
import urllib
import os
import sys
import time
import re
import json
from optparse import OptionParser, OptionGroup


# private albums
URL_FOR_PHOTOS 	= '/data/feed/api/user/default/albumid/%s?kind=photo'
URL_FOR_TAGS 	= '/data/feed/api/user/default/albumid/%s/photoid/%s?kind=tag' 
URL_FOR_COMMENTS	= '/data/feed/api/user/default/albumid/%s/photoid/%s?kind=comment'

# public albums
URL_FOR_PUBLIC_PHOTOS 	= '/data/feed/base/user/%s/albumid/%s?kind=photo'

def downloadFile(url, dir_name):
	"""Download the data at URL to the current directory"""
	# figure out a good name for the downloaded file.
	basename = url[url.rindex('/') + 1:] 

	# if still-shot of MVI file, just return
	if basename[0:2] == "MVI":
		return

	url = url.replace(basename, "d/"+basename)

	urllib.urlretrieve(url, dir_name+"/"+basename)

def connectToPicasa(user_id, password):
	gdClient = gdata.photos.service.PhotosService()

	# if password is given, we can access private albums
	if password:
		gdClient.email = user_id
		gdClient.password = password
		gdClient.source = 'api-sample-google-com'
		gdClient.ProgrammaticLogin()

	return gdClient

def getAlbum(gdClient, loginId):
	return gdClient.GetUserFeed(user = loginId)

def getPhoto(albums, password, download, oldest_date = ""):
	for album in albums.entry:
		downloadCount = 0

		if oldest_date != "":
			ttt = re.findall("\d{4}-\d{2}-\d{2}", album.published.text)
			album_date = re.sub("\-", "", ttt[0])

			if eval(album_date) < eval(oldest_date):
				continue

		print 'Album: %-30s (%3s) %s' % (album.title.text, album.numphotos.text\
			, album.published.text.replace("T", " "))
		#, album.updated.text)

		if download == False:
			continue
			
		if not os.path.exists(album.title.text) :
			os.mkdir(album.title.text)

		if password:
			photos = gdClient.GetFeed(URL_FOR_PHOTOS % (album.gphoto_id.text))
		else:
			photos = gdClient.GetFeed(URL_FOR_PUBLIC_PHOTOS % (loginId, album.gphoto_id.text))

		for photo in photos.entry:
			downloadFile(photo.content.src, album.title.text)
			downloadCount += 1

			sys.stdout.write("\t%d/%s  %.1f %%\r" %(downloadCount, album.numphotos.text, 100.0*downloadCount/eval(album.numphotos.text)))
			sys.stdout.flush()

		print ""
		

if __name__ == '__main__':
	usage = "usage: %prog [-d] [-t YYYYMMDD]"
	parser = OptionParser(usage=usage)
	parser.add_option("-d", dest="download", default=False, action="store_true", help="download")
	parser.add_option("-t", dest="oldest_date", default="", action="store", help="oldest date to download")

	(options, args) = parser.parse_args()

	config = json.loads(open('config.json').read())
	loginId = config['id']
	password = config['password']

	gdClient = connectToPicasa(loginId, password)

	albums = getAlbum(gdClient, loginId)

	if options.oldest_date != "" and len(options.oldest_date) == 8:
		getPhoto(albums, password, options.download, options.oldest_date)
	else:
		getPhoto(albums, password, options.download)

	
