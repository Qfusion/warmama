#!/usr/bin/env python3

'''
Created on 7.2.2011
Warmama
@author: Christian Holmberg 2011

@license:
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

# cgi_mode = 'local'
cgi_mode = 'wsgi'
# cgi_mode = 'fcgi'

report_dir = '/var/log/warmama/reports'
logfile_name = '/var/log/warmama/warmama.log'
logfile_append = True	# or False

proxy_addr = ["127.0.0.1", "::1"]

# database configuration
db_type = 'mysql'
db_host = 'localhost'
db_port = 3306
db_name = 'warmama'
db_user = 'root'
db_passwd = 'root'
db_engine = 'INNODB'
db_charset = 'utf8'
db_debug_print = False

# URL to send the authentication request
# getauth_url = 'http://localhost:6000/getauth'	# local to local
getauth_url = 'http://www-dev.warsow.net:1337/mmauth'	# external to external

# this URL is given as a parameter to above request
# it is the URL the auth-server has to respond to
auth_response_url = 'http://mm-dev.warsow.net/auth'

# alpha-testing phase, store all anon-players as registered users
alpha_phase = 0

steam_appid = ''
steam_web_api_base_url = 'https://partner.steam-api.com'
steam_web_api_version = ''
steam_web_api_publisher_key = ''

# constants
USER_SERVER = 0
USER_CLIENT = 1
USER_NUM = 2

# in seconds
TICKET_EXPIRATION = 60.0

