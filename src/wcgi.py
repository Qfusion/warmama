#!/usr/bin/env python3

"""
Created on 27.3.2011
@author: hc
"""

###################
#
# Imports

from builtins import object
import os
import web
import config
import warmama
from warmama import safeint


###################
#
# Constants

###################
#
# Globals

###################
#
# Helpers

def getIP():
	IP = web.ctx.ip
	if IP in config.proxy_addr:
		IP = web.ctx.env.get("HTTP_X_FORWARDED_FOR", IP)
		IP = IP.split(',')[0]
	return IP

###################
#
# Classes

class index(object) :
	def GET(self):
		return 'Hello World! (GET)'
	def POST(self):
		return 'Hello World! (POST)'

class slogin(object) :
	def POST(self):
		input = web.input()
		port = safeint( input.get( 'port', '0' ) )
		authkey = input.get('authkey', '')
		hostname = input.get('hostname', '')
		demos_baseurl = input.get('demos_baseurl', '')
		
		r = warmama.warmama.ServerLogin(authkey, getIP(), port, hostname, demos_baseurl)
		web.header('Content-Type', 'application/json')
		return r
	
	def GET(self):
		return self.POST()
	
class slogout(object) :
	def POST(self):
		input = web.input()
		ssession = safeint( input.get( 'ssession', '0' ) )
		
		r = warmama.warmama.ServerLogout(ssession, getIP())
		web.header('Content-Type', 'application/json')
		return r
	
	def GET(self):
		return self.POST()

class scc(object) :
	def POST(self) :
		input = web.input()
		ssession = safeint( input.get( 'ssession', '0' ) )
		csession = safeint( input.get( 'csession', '0' ) )
		cticket = safeint( input.get( 'cticket', '0' ) )
		cip = input.get( 'cip', '' )
		
		r = warmama.warmama.ServerClientConnect(ssession, csession, cticket, cip)
		web.header('Content-Type', 'application/json')
		return r
	
	def GET(self):
		return self.POST()
	
class scd(object) :
	def POST(self):
		input = web.input()
		ssession = safeint( input.get( 'ssession', '0' ) )
		csession = safeint( input.get( 'csession', '0' ) )
		gameon = safeint( input.get( 'gameon', '0' ) )
		
		r = warmama.warmama.ServerClientDisconnect(ssession, csession, gameon)
		web.header('Content-Type', 'application/json')
		return r
	
	def GET(self):
		return self.POST()
	
class shb(object) :
	def POST(self):
		input = web.input()
		ssession = safeint( input.get( 'ssession', '0' ) )
		
		r = warmama.warmama.Heartbeat(ssession, getIP(), 'server')
		web.header('Content-Type', 'application/json')
		return r
	
class smr(object) :
	def POST(self):
		input = web.input()
		
		ssession = safeint( input.get( 'ssession', '0' ) )
		report = input.get( 'data', '' )
		
		r = warmama.warmama.MatchReport(ssession, report, getIP())
		web.header('Content-Type', 'application/json')
		return r

class smuuid(object) :
	def POST(self):
		input = web.input()
		ssession = safeint( input.get( 'ssession', '0' ) )
		
		r = warmama.warmama.MatchUUID(ssession, getIP())
		web.header('Content-Type', 'application/json')
		return r

# JUST PUTTING THIS IN HERE.. RAW DATA ACCESS IN POST
# def POST(self) :
# 	data = web.data()

### client requests
class clogin(object) :
	def POST(self):
		input = web.input()
		
		login = input.get( 'login', '' ).strip(' \t\n\r')
		pw = input.get( 'passwd', '' ).strip(' \t\n\r')
		handle = safeint( input.get( 'handle', '' ) )
		
		r = warmama.warmama.ClientLogin(login, pw, handle, getIP())
		web.header('Content-Type', 'application/json')
		return r
	
	def GET(self):
		return self.POST()

class clogout(object) :
	def POST(self):
		input = web.input()
		csession = safeint( input.get( 'csession', '0' ) )
		
		r = warmama.warmama.ClientLogout(csession, getIP())
		web.header('Content-Type', 'application/json')
		return r
	
	def GET(self):
		return self.POST()
	
class ccc(object) :
	def POST(self):
		input = web.input()
		csession = safeint( input.get( 'csession', '0' ) )
		saddr = input.get( 'saddr', '' )
		
		r = warmama.warmama.ClientConnect(csession, saddr)
		web.header('Content-Type', 'application/json')
		return r

class chb(object) :
	def POST(self):
		input = web.input()
		csession = safeint( input.get( 'csession', '0' ) )
		
		r = warmama.warmama.Heartbeat(csession, getIP(), 'client')
		web.header('Content-Type', 'application/json')
		return r
	
#####################

class auth(object) :
	def POST(self):
		input = web.input()
		
		handle = safeint( input.get( 'handle', '0' ) )
		secret = input.get( 'digest', '' )
		valid = safeint( input.get( 'valid', '0') )
		profile_url = input.get( 'profile_url', '' ).strip(' \t\n\r')
		profile_url_rml = input.get( 'profile_url_rml', '' ).strip(' \t\n\r')
		steam_id = input.get( 'steam_id', '' ).strip(' \t\n\r')

		r = warmama.warmama.ClientAuthenticate(handle, secret, valid, profile_url, profile_url_rml, steam_id)
		web.header('Content-Type', 'text/plain')
		return r
	
	def GET(self):
		return self.POST()
	
#####################

urls = (
	# server
	'/slogin', 'slogin',
	'/slogout', 'slogout',
	'/scc', 'scc',
	'/scd', 'scd',
	'/smr', 'smr',
	'/shb', 'shb',
	'/smuuid', 'smuuid',
	
	# client
	'/clogin', 'clogin',
	'/clogout', 'clogout',
	'/ccc', 'ccc',
	'/chb', 'chb',
	
	'/auth', 'auth'
)

if config.cgi_mode == 'local' :
	app = web.application(urls, globals())
elif config.cgi_mode == 'wsgi' :
	app = web.application(urls, globals(), autoreload=False)
elif config.cgi_mode == 'fcgi' :
	# something's wrong with FCGI here..
	app = web.application(urls, globals())
	web.wsgi.runwsgi = lambda func, addr=None: web.wsgi.runfcgi(func, addr)
	
if __name__ == "__main__":
	app.run()
elif config.cgi_mode == 'wsgi' :
	# wsgi
	application = app.wsgifunc()
