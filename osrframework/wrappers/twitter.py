# !/usr/bin/python
# -*- coding: cp1252 -*-
#
##################################################################################
#
#    Copyright 2015 Félix Brezo and Yaiza Rubio (i3visio, contacto@i3visio.com)
#
#    This program is part of OSRFramework. You can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##################################################################################

import argparse
import json
import re
import sys
import urllib2

import osrframework.utils.browser as browser
from osrframework.utils.platforms import Platform

class Twitter(Platform):
    """ 
        A <Platform> object for Twitter.
    """
    def __init__(self):
        '''
            Constructor...
        '''
        self.platformName = "Twitter"   
        # These tags will be the one used to label this platform
        self.tags = ["contact", "opinions", "social"]
        
        ########################
        # Defining valid modes #
        ########################
        self.isValidMode = {}        
        self.isValidMode["phonefy"] = False
        self.isValidMode["usufy"] = True
        self.isValidMode["searchfy"] = True
        
        ######################################
        # Search URL for the different modes #
        ######################################
        # Strings with the URL for each and every mode
        self.url = {}        
        #self.url["phonefy"] = "http://anyurl.com//phone/" + "<phonefy>"
        self.url["usufy"] = "http://twitter.com/" + "<usufy>"
        self.url["searchfy"] = "https://twitter.com/search?q=" + "<searchfy>"       

        ######################################
        # Whether the user needs credentials #
        ######################################
        self.needsCredentials = {}        
        #self.needsCredentials["phonefy"] = False
        self.needsCredentials["usufy"] = False
        self.needsCredentials["searchfy"] = False 
        
        ###################
        # Valid queries #
        ###################
        # Strings that will imply that the query number is not appearing
        self.validQuery = {}
        # The regular expression '.*' will match any query.
        #self.validQuery["phonefy"] = re.compile(".*")
        self.validQuery["usufy"] = re.compile("[a-zA-Z0-9_]+")   
        self.validQuery["searchfy"] = re.compile(".*")
        
        ###################
        # Not_found clues #
        ###################
        # Strings that will imply that the query number is not appearing
        self.notFoundText = {}
        #self.notFoundText["phonefy"] = []
        self.notFoundText["usufy"] = ["<form class=\"search-404\""]   
        self.notFoundText["searchfy"] = []        
        
        #########################
        # Fields to be searched #
        #########################
        self.fieldsRegExp = {}
        
        # Definition of regular expressions to be searched in phonefy mode
        #self.fieldsRegExp["phonefy"] = {}
        # Example of fields:
        #self.fieldsRegExp["phonefy"]["i3visio.location"] = ""
        
        # Definition of regular expressions to be searched in usufy mode
        self.fieldsRegExp["usufy"] = {}
        # Examples (do NOT forget to escape the quoting marks inside any string: \"):
        self.fieldsRegExp["usufy"]["@data-protected"] = {"start": "data-protected=\"", "end": "\">\n      <span class=\"UserActions"}
        self.fieldsRegExp["usufy"]["i3visio.fullname"] = {"start": "\" data-name=\"", "end": "\" data-protected"}
        #self.fieldsRegExp["usufy"]["ProfileHeaderCard-bio"] = {"start": "<p class=\"ProfileHeaderCard-bio u-dir\"\n    \n    dir=\"ltr\">", "end": "</p>"}
        self.fieldsRegExp["usufy"]["i3visio.location"] = {"start": "<span class=\"ProfileHeaderCard-locationText u-dir\" dir=\"ltr\">", "end": "</span>\n      </div>\n\n    <div class=\"ProfileHeaderCard-url \">\n"}
        self.fieldsRegExp["usufy"]["i3visio.date"] = {"start": "<span class=\"ProfileHeaderCard-joinDateText js-tooltip u-dir\" dir=\"ltr\" title=\"", "end": "\">Se uni"}
        self.fieldsRegExp["usufy"]["i3visio.uri"] = {"start": "<span class=\"ProfileHeaderCard-urlText u-dir\" dir=\"ltr\"><a class=\"u-textUserColor\" target=\"_blank\" rel=\"me nofollow\" href=\"[^\"]*\" title=\"", "end": "\">"}
        self.fieldsRegExp["usufy"]["PhotoRail-headingText"] = {"start": "class=\"js-nav\">\n                \n                ", "end": "             </a>"}
        
        # Definition of regular expressions to be searched in searchfy mode
        self.fieldsRegExp["searchfy"] = {}
        # Example of fields:
        self.fieldsRegExp["searchfy"]["i3visio.location"] = ""        
        
        ################
        # Fields found #
        ################
        # This attribute will be feeded when running the program.
        self.foundFields = {}

