#!/usr/bin/env python3

"""
Created on 17.1.2014
@author: vic
"""

###################
#
# Imports

import config
import database

import IPy as ipy
import json
import string
import errno
import re
import urllib
import urllib2
import sys
import traceback

import traceback

import time
import Queue
import threading

###################
#
# Constants

###################
#
# Globals

###################
#
# Helpers


###################
#
# Classes
class SteamStatsThread(threading.Thread):
	def __init__(self, steamHandler, queue):
		threading.Thread.__init__(self)
		self.queue = queue
		self.steamHandler = steamHandler
		self.mm = steamHandler.mm
		self.dbHandler = database.DatabaseWrapper(self.mm,
			config.db_host, config.db_port, config.db_user, config.db_passwd, config.db_name, config.db_engine, config.db_charset)

	def run(self):
		while True:
			try:
				# grabs player from queue
				player = None
				player = self.queue.get()

				# grab stats for the player
				stats = self.dbHandler.GetSteamStatsForPlayer(player)

				# submits the stats to Steam for given player
				steamID = self.dbHandler.GetSteamIDForPlayer(player)
				self.steamHandler.SubmitClientStats(steamID, stats)

				# signals to queue job is done
				self.queue.task_done()
			except Exception as e:
				exc_type, exc_value, exc_traceback = sys.exc_info()
				self.mm.log("Caught exception %s" % repr(traceback.format_exception(exc_type, exc_value, exc_traceback)))

class SteamDatamineThread(threading.Thread):
	def __init__(self, steamHandler, queue):
		threading.Thread.__init__(self)
		self.queue = queue
		self.mm = steamHandler.mm
		self.dbHandler = database.DatabaseWrapper(self.mm,
			config.db_host, config.db_port, config.db_user, config.db_passwd, config.db_name, config.db_engine, config.db_charset )

	def run(self):
		while True:
			try:
				players = self.dbHandler.GetDirtySteamPlayers()
				if players is not None :
					for player in players :
						self.queue.put(player)
				self.queue.join()
			except Exception as e:
				exc_type, exc_value, exc_traceback = sys.exc_info()
				self.mm.log("Caught exception %s" % repr(traceback.format_exception(exc_type, exc_value, exc_traceback)))
			finally:
				time.sleep(3)

class SteamHandler(object):	
	def __init__(self, mm):
		self.mm = mm
		self.appid = config.steam_appid
		self.base_url = config.steam_web_api_base_url
		self.publisher_key = config.steam_web_api_publisher_key
		self.api_version = config.steam_web_api_version

		# queued updates for ext parties
		self.extQueue = Queue.Queue()

		# datamining thread for steam
		t = SteamDatamineThread(self, self.extQueue)
		t.setDaemon(True)
		t.start()

		# worker threads that post updates to ext parties (steam)
		for i in range(5):
			t = SteamStatsThread(self, self.extQueue)
			t.setDaemon(True)
			t.start()
	
	def ClientLogin( self, id, ticket ):
		try :
			# create the url object
			data = urllib.urlencode( { 'key' : self.publisher_key,
				'appid' : self.appid,
				'ticket' : ticket.encode('hex')
			} )
			
			url = "%s/ISteamUserAuth/AuthenticateUserTicket/v%s/" % ( self.base_url, self.api_version );
			req = urllib2.urlopen( "%s?%s" % ( url, data ) )
			resp_text = req.read()
			
			# print( "**** AUTHTICKET RESPONSE: %s" % resp_text )
			self.mm.log( "**** AUTHTICKET RESPONSE: %s" % resp_text )
			req.close()
			
			auth = json.loads( resp_text )
			if auth is None :
				return False
			if not "response" in auth :
				return False
			response = auth['response']
			if not "params" in response :
				return False
			params = response['params']
			if not "result" in params :
				return False
			if params['result'] != 'OK' :
				return False
			if params['steamid'] != id :
				return False
			if params['vacbanned'] or params['publisherbanned'] :
				return False
			return True

		except urllib2.HTTPError as e :
			# print( "Steam::ClientLogin: Failed to fetch %s" % url )
			self.mm.log( "Steam::ClientLogin: Failed to fetch %s, code: %i" % (url, e.code) )
			return False
		except urllib2.URLError as e :
			# print( "Steam::ClientLogin: Failed to fetch %s" % url )
			self.mm.log( "Steam::ClientLoginSteam: Failed to fetch %s, reason: %s" % (url, e.reason) )
			return False

	def GetProfile( self, steam_ids ):
		try : 
			# create the url object
			data = urllib.urlencode( { 'key' : self.publisher_key,
				'steamids' : steam_ids,
			} )
			url = "%s/ISteamUser/GetPlayerSummaries/v%s/" % ( self.base_url, '0002' );
			
			req = urllib2.urlopen( "%s?%s" % ( url, data ) )
			resp_text = req.read()
			
			req.close()
			return resp_text
			
		except Exception as e :
			self.mm.log( "Steam::ClientAwardTest exception %s" % e)
			self.mm.log( "Traceback: %s" % traceback.format_exc())
			return json.dumps({'response':{'success':'false'}});

	def SubmitClientStats( self, id, stats ):
		try : 
			# create the url object
			urlargs = { 'key' : self.publisher_key,
				'appid' : self.appid,
				'steamid' : id,
			}
			
			count = 0
			for name in stats.keys() :
			    key = "name[%i]" % count
			    urlargs[key] = name
			    key = "value[%i]" % count
			    urlargs[key] = stats[name][0]
			    count = count + 1
			urlargs['count'] = count

			self.mm.log("%s" % urlargs)

			data = urllib.urlencode( urlargs )
			url = "%s/ISteamUserStats/SetUserStatsForGame/v%s/" % ( self.base_url, self.api_version );
			req = urllib2.urlopen( url, data )
			resp_text = req.read()
			
			#print( "**** SetUserStatsForGame RESPONSE: %s" % resp_text )
			self.mm.log( "**** SetUserStatsForGame RESPONSE: %s" % resp_text )
			req.close()
			
			self.SubmitClientLeaderboardScores(id, stats)
			
			return True
			
		except Exception as e :
			#self.mm.log( "Steam::ClientAwardTest exception %s" % e)
			#self.mm.log( "Traceback: %s" % traceback.format_exc())
			return False
			
	def SubmitClientLeaderboardScores( self, id, stats ):
		# submit leaderboard scores
		for name in stats.keys() :
			value = stats[name][0]
			leaderboard_id = stats[name][1]
			if not leaderboard_id:
				continue
				
			urlargs = { 'key' : self.publisher_key,
				'appid' : self.appid,
				'steamid' : id,
				'leaderboardid' : leaderboard_id,
				'score' : value,
				'scoremethod' : 'ForceUpdate',
			}
				
			data = urllib.urlencode( urlargs )
			url = "%s/ISteamLeaderboards/SetLeaderboardScore/v0001/" % ( self.base_url );
			req = urllib2.urlopen( url, data )
			resp_text = req.read()
				
			#print( "**** SetLeaderboardScore RESPONSE: %s" % resp_text )
			self.mm.log( "**** SetLeaderboardScore RESPONSE: %s" % resp_text )
			req.close()

####################################
