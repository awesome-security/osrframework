# -*- coding: cp1252 -*-
#
##################################################################################
#
#    Copyright 2015 Félix Brezo and Yaiza Rubio (i3visio, contacto@i3visio.com)
#
#    This file is part of OSRFramework. You can redistribute it and/or modify
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
import os
import random
import re
import sys
import urllib
import urllib2

import osrframework.utils.browser as browser
from osrframework.utils.credentials import Credential
import osrframework.utils.general as general
import osrframework.entify as entify

# logging imports
import logging

class Platform():
    ''' 
        <Platform> class.
    '''
    def __init__(self):
        ''' 
            Constructor without parameters...
        '''
        pass    
    def __init__(self, pName, tags):
        ''' 
            Constructor with parameters. This method permits the developer to instantiate dinamically Platform objects.
        '''
        self.platformName = pName
        # These tags will be the one used to label this platform
        self.tags = tags

        ########################
        # Defining valid modes #
        ########################
        self.isValidMode = {}        
        self.isValidMode["phonefy"] = False
        self.isValidMode["usufy"] = False
        self.isValidMode["searchfy"] = False      
        
        ######################################
        # Search URL for the different modes #
        ######################################
        # Strings with the URL for each and every mode
        self.url = {}        
        #self.url["phonefy"] = "http://anyurl.com//phone/" + "<phonefy>"
        #self.url["usufy"] = "http://anyurl.com/user/" + "<usufy>"
        #self.url["searchfy"] = "http://anyurl.com/search/" + "<searchfy>"       

        ######################################
        # Whether the user needs credentials #
        ######################################
        self.needsCredentials = {}        
        self.needsCredentials["phonefy"] = False
        self.needsCredentials["usufy"] = False
        self.needsCredentials["searchfy"] = False 
        
        ###################
        # Valid queries #
        ###################
        # Strings that will imply that the query number is not appearing
        self.validQuery = {}
        # The regular expression '.*' will match any query.
        self.validQuery["phonefy"] = re.compile(".*")
        self.validQuery["usufy"] = re.compile(".*")   
        self.validQuery["searchfy"] = re.compile(".*")
        
        ###################
        # Not_found clues #
        ###################
        # Strings that will imply that the query number is not appearing
        self.notFoundText = {}
        #self.notFoundText["phonefy"] = []
        #self.notFoundText["usufy"] = []   
        #self.notFoundText["searchfy"] = []        
        
        #########################
        # Fields to be searched #
        #########################
        self.fieldsRegExp = {}
        
        # Definition of regular expressions to be searched in phonefy mode
        #self.fieldsRegExp["phonefy"] = {}
        # Example of fields:
        #self.fieldsRegExp["phonefy"]["i3visio.location"] = ""
        
        # Definition of regular expressions to be searched in usufy mode
        #self.fieldsRegExp["usufy"] = {}
        # Example of fields:
        #self.fieldsRegExp["usufy"]["i3visio.location"] = ""
        
        # Definition of regular expressions to be searched in searchfy mode
        #self.fieldsRegExp["searchfy"] = {}
        # Example of fields:
        #self.fieldsRegExp["searchfy"]["i3visio.location"] = ""        
        
    def createURL(self, word, mode="phonefy"):
        ''' 
            Method to create the URL replacing the word in the appropriate URL.
            
            :param word:   Word to be searched.
            :param mode:    Mode to be executed.
            
            :return:    The URL to be queried.
        '''
        try:
            return self.url[mode].replace("<"+mode+">", word.replace(' ', '+'))
        except:
            pass
            # TO-DO: BaseURLNotFoundExceptionThrow base URL not found for the mode.

        
    def getInfo(self, query=None, process = False, mode="phonefy"):
        ''' 
            Method that checks the presence of a given query and recovers the first list of complains.

            :param query:   Query to verify.
            :param proces:  Calling the processing function.
            :param mode:    Mode to be executed.            

            :return:    Python structure for the html processed.
        '''
        # Defining variables for this process
        results = []
        data = ""
        if not self.modeIsValid(mode=mode):
            # TO-DO: InvalidModeException
            return json.dumps(results)
        # Creating the query URL for that mode
        qURL = self.createURL(word=query, mode=mode)        
        i3Browser = browser.Browser()            
        try:
            # check if it needs creds
            if self.needsCredentials[mode]:
                authenticated = self._getAuthenticated(i3Browser)
                if authenticated:
                    # Accessing the resources
                    data = i3Browser.recoverURL(qURL)
            else:
                # Accessing the resources
                data = i3Browser.recoverURL(qURL)
        except:
            # No information was found, then we return a null entity
            # TO-DO: i3BrowserException         
            return json.dumps(results)            

        # Verifying if the platform exists
        if self.somethingFound(data, mode=mode):

            if mode == "phonefy":
                r = {}
                r["type"] = "i3visio.phone"
                r["value"] = self.platformName + " - " + query
                r["attributes"] = []      

                # Appending platform URI
                aux = {}
                aux["type"] = "i3visio.uri"
                aux["value"] = qURL
                aux["attributes"] = []           
                r["attributes"].append(aux)   
                
                # Appending platform name
                aux = {}
                aux["type"] = "i3visio.platform"
                aux["value"] = self.platformName
                aux["attributes"] = []
                r["attributes"].append(aux)
                              
                # Iterating if requested to extract more entities from the URI
                if process:                               
                    # This function returns a json text!
                    r["attributes"] += json.loads(self.processData(data=data, mode=mode))
                # Appending the result to results: in this case only one profile will be grabbed
                results.append(r)    
                                                          
            elif mode == "usufy":
                r = {}            
                r["type"] = "i3visio.profile"
                r["value"] = self.platformName + " - " + query                
                r["attributes"] = []   
                
                # Appending platform URI
                aux = {}
                aux["type"] = "i3visio.uri"
                aux["value"] = qURL
                aux["attributes"] = []           
                r["attributes"].append(aux)  
                # Appending the alias
                aux = {}
                aux["type"] = "i3visio.alias"
                aux["value"] = query
                aux["attributes"] = []           
                r["attributes"].append(aux)                    
                # Appending platform name
                aux = {}
                aux["type"] = "i3visio.platform"
                aux["value"] = self.platformName
                aux["attributes"] = []
                r["attributes"].append(aux)
                
              
                # Iterating if requested to extract more entities from the URI
                if process:                               
                    # This function returns a json text!
                    r["attributes"] += json.loads(self.processData(data=data, mode=mode))
            
                # Appending the result to results: in this case only one profile will be grabbed
                results.append(r)                
                                              
            elif mode == "searchfy":
                # Recovering all the found aliases...
                ids = re.findall(self.searchfyAliasRegexp, data, re.DOTALL)
                
                for i in ids:
                    r = {}            
                    r["type"] = "i3visio.profile"
                    r["value"] = self.platformName + " - " + i            
                    r["attributes"] = []   
                    
                    # Appending platform URI
                    aux = {}
                    aux["type"] = "i3visio.uri"
                    # Creating a usufy URI...
                    aux["value"] = self.createURL(word=i, mode="usufy")
                    aux["attributes"] = []           
                    r["attributes"].append(aux)  
                    # Appending the alias
                    aux = {}
                    aux["type"] = "i3visio.alias"
                    aux["value"] = i
                    aux["attributes"] = []           
                    r["attributes"].append(aux)                      
                    # Appending platform name
                    aux = {}
                    aux["type"] = "i3visio.platform"
                    aux["value"] = self.platformName
                    aux["attributes"] = []
                    r["attributes"].append(aux)
                    # Appending the query performed to grab this items
                    aux = {}
                    aux["type"] = "i3visio.search"
                    aux["value"] = query
                    aux["attributes"] = []
                    r["attributes"].append(aux)
                    
                    # TO-DO:
                    # Perform additional procesing
                    # Iterating the requested profiles to extract more entities from the URI would be slow!
                    if process:                               
                        # This function returns a json text in usufy format for the returned objects.
                        r["attributes"] += json.loads(self.processData(data=data, mode="usufy"))                    
                    # Appending the result to results: in this case only one profile will be grabbed
                    results.append(r)  
        return json.dumps(results)

    def modeIsValid(self, mode):
        ''' 
            Verification of whether the mode is a correct option to be used.
            
            :param mode:    Mode to be executed.            
            
            :return:    True if the mode exists in the three main folders.
        '''
        if mode in self.isValidMode.keys():
            if mode in self.isValidMode.keys():
                return True
        return False
        
    def processData(self, uri=None, data = None, mode=None):
        ''' 
            Method to process and extract the entities of a URL of this type.
           
            :param uri: The URI of this platform to be processed.
            :param data: The information from which the info will be extracted. This way, info will not be downloaded twice.
            :param mode:    Mode to be executed.            
                        
            :return:    A list of the entities found.
        '''
        if data == None:
            # Accessing the resource
            data = i3Browser.recoverURL(uri)        
        else:
            return json.dumps({})
        info = []

        # Searchfy needs an special treatment to recover the results
        if mode != "searchfy":
            # Iterating through all the type of fields
            for field in self.fieldsRegExp[mode].keys():
                # Recovering the RegularExpression
                try:
                    # Using the old approach of "Start" + "End"
                    regexp = self.fieldsRegExp[mode][field]["start"]+"([^\)]+)"+self.fieldsRegExp[mode][field]["end"]
                    
                    tmp = re.findall(regexp, data)
                    
                    # Now we are performing an operation just in case the "end" tag is found  in the results, which would mean that the tag selected matches something longer in the data.
                    values = []
                    for t in tmp:
                        if self.fieldsRegExp[mode][field]["end"] in t:

                            values.append(t.split(self.fieldsRegExp[mode][field]["end"])[0])
                        else:
                            values.append(t)
                            
                except:
                    # Using the compact approach if start and end tags do not exist.
                    regexp = self.fieldsRegExp[mode][field]
                    
                    values = re.findall(regexp, data)
                
                for val in values:
                    aux = {}
                    aux["type"] = field
                    aux["value"] = val
                    aux["attributes"] = []                
                    if aux not in info:
                        info.append(aux)        
        # Searchfy results        
        else:
            # Grabbing the results for the search
            resultText = re.findall(searchfyAliasRegexp, data)
            # Analysing each and every result to parse it...        
            for res in resultText:
                r = {}
                r["type"] = "i3visio.uri"
                r["value"] = ""
                r["attributes"] = []
                # Iterating through all the type of fields
                for field in self.fieldsRegExp[mode].keys():
                    # Building the regular expression if the format is a "start" and "end" approach... Easier to understand but less compact.
                    try:
                        # Using the old approach of "Start" + "End"
                        regexp = self.fieldsRegExp[mode][field]["start"]+"([^\)]+)"+self.fieldsRegExp[mode][field]["end"]
                        
                        # Parsing the result for the text
                        tmp = re.findall(regexp, res)
                        
                        # Now we are performing an operation just in case the "end" tag is found  in the results, which would mean that the tag selected matches something longer in the data.
                        values = []
                        for t in tmp:
                            if self.fieldsRegExp[mode][field]["end"] in t:

                                values.append(t.split(self.fieldsRegExp[mode][field]["end"])[0])
                            else:
                                values.append(t)
                    # In the case of a compact approach being used. This would happen if start and end tags do not exist, but the expected behaviour is the same.
                    except:
                        regexp = self.fieldsRegExp[mode][field]
                        
                        values = re.findall(regexp, data)
                    
                    if field == "i3visio.uri":
                        for val in values:
                            r["value"] =  val
                    else:
                        for val in values:
                            aux = {}
                            aux["type"] = field
                            aux["value"] = val
                            aux["attributes"] = []                
                            if aux not in r["attributes"]:
                                r["attributes"].append(aux)               
                                #print json.dumps(r["attributes"], indent =2)
                info.append(r)
        return json.dumps(info)
    
    def somethingFound(self,data,mode="phonefy"):
        ''' 
            Verifying if something was found.
            
            :param data:    Data where the self.notFoundText will be searched.
            :param mode:    Mode to be executed.            
            
            :return: Returns True if exists.
        '''
        #try:
        for text in self.notFoundText[mode]:
            if text in data:
                return False
        return True
        #except:
        #    pass
        #    # TO-DO: Throw notFoundText not found for this mode.        
            
    def __str__(self):
        ''' 
            Function to represent the text when printing the object
            
            :return:    self.platformName
        '''
        try:
            return self.parameterName        
        except:
            return self.platformName    

    def _getAuthenticated(self, browser):
        ''' 
            Getting authenticated. This method will be overwritten.
            
            :param browser: The browser in which the user will be authenticated.
        '''
        # check if we have creds
        if len(self.creds) > 0:
            # choosing a cred
            c = random.choice(self.creds)
            # adding the credential
            browser.setNewPassword(url, c.user, c.password)
            return True
        else:
            logger.debug("No credentials have been added and this platform needs them.")
            return False
        
    def _isValidQuery(self, query, mode="phonefy"):
        '''    
            Method to verify if a given query is processable by the platform. The system looks for the forbidden characters in self.Forbidden list.
            
            :param query:
            :param mode:    To be chosen amongst phonefy, usufy and searchfy.
            :return:    True | False
        '''
        # Verifying if the mode supports such a query
        if  self.validQuery[mode].match(query):
            return True                
        else:
            return False
            
           
  