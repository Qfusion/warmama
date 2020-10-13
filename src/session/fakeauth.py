#!/usr/bin/env python3

'''
Created on 11.4.2011

@author: hc
'''
from __future__ import print_function
from __future__ import unicode_literals

from future import standard_library
standard_library.install_aliases()
from builtins import object
import web
import urllib.request, urllib.parse, urllib.error

##########################

def safeint( s ):
	try :
		return int(s)
	except:
		return 0
	
##########################

class getauth(object):
	def POST(self):
		input = web.input()
		# login = input.get( 'login', '' )
		# passwd = input.get( 'passwd', '' )
		handle = input.get( 'handle', '0' )
		secret = input.get( 'digest', '' )
		
		url = input.get( 'url', '' )
		
		# create a POST request sending validation
		data = urllib.parse.urlencode( {  'handle' : handle,
									'digest' : secret,
									'valid' : '1' } )
		
		try :
			opener = urllib.request.build_opener()
			opener.addheaders = [('User-agent', 'Warmama/1.0')]
			response = opener.open(url, data).read()
		except:
			print("getauth: failed to open url %s" % url)
		
		return ''

##########################

urls = ( '/getauth', 'getauth' )

app = web.application(urls, globals())

if __name__ == "__main__":
	app.run()

