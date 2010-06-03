#!/usr/bin/env python
#
#vim:set et sts=4 sw=4:
#
# Flies Python Client
#
# Copyright (c) 2010 Jian Ni <jni@gmail.com>
# Copyright (c) 2010 Red Hat, Inc.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330,
# Boston, MA  02111-1307  USA

import getopt, sys
import json
import os.path
from parseconfig import FliesConfig
from flieslib.client import FliesClient
from flieslib.client import NoSuchFileException
from flieslib.client import NoSuchProjectException
from flieslib.client import UnAuthorizedException
from flieslib.client import InvalidOptionException

sub_command = {
                'help':[],
                'list':[],
                'status':[],
                'project':['info','create', 'remove'],
                'iteration':['info', 'create', 'remove'],
                'publican':['push', 'pull']
                }

class FliesConsole:

    def __init__(self):
        config = FliesConfig()
    	server = config.get_config_value("server")
    	project_id = config.get_config_value("project.id")
    	iteration_id = config.get_config_value("project.iteration.id") 
    	user = config.get_config_value("user")
    	apikey = config.get_config_value("apikey")
        self.options = {
                        'server' : server,
                        'project_id':project_id,
                        'iteration_id':iteration_id,
                        'user':user,
                        'apikey':apikey,
                        'name':'',
                        'desc':''
                       }
     
    def _print_usage(self):
        print ('\nClient for talking to a Flies Server\n\n'
               'basic commands:\n\n'
               'list             List all available projects\n'
               'project info      Retrieve a project\n'
               'iteration info    Retrieve a iteration\n\n'
               "Use 'flies help' for the full list of commands")

    def _print_help_info(self, args):
        if not args:
            print ('Client for talking to a Flies Server:\n\n'
                  'list of commands:\n\n'
                  ' list                List all available projects\n'
                  ' project info         Retrieve a project\n'
                  ' iteration info       Retrieve a iteration\n'
                  ' project create      Create a project\n'
                  ' iteration create    Create a iteration of a project\n'   
                  ' publican pull       Pull the content of publican file\n'
                  ' publican push       Push the content of publican to Flies Server\n')
        else:
            command = args[0]
            sub = args[1:]
            if sub_command.has_key(command):
                if sub_command[command]:
                    if sub:
                        if sub[0] in sub_command[command]:
                            command = command+'_'+sub[0]
                        else:
                            print "Can not find such command"
                            sys.exit()
                    else:
                        print "Please complete the command!"
                        sys.exit()
            else:
                print "Can not find such command"
                sys.exit()

            self._command_help(command)

    def _command_help(self, command):      
        if command == 'list':
            self._list_help()
        elif command == 'project_info':
            self._projec_info_help()
        elif command == 'project_create':
            self._project_create_help()
        elif command == 'iteration_info':
            self._iteration_info_help()
        elif command == 'iteration_create':
            self._iteration_create_help()
        elif command == 'publican_push':
            self._publican_push_help()
        elif command == 'publican_pull':
            self._publican_pull_help()
                

    def _list_help(self):
       	print ('flies list [OPTIONS]\n\n'
               'list all available projects\n\n'
               'options:\n\n'
               ' --server url address of the Flies server')
    
    def _projec_info_help(self):
	    print ('flies project info [OPTIONS]')

    def _project_create_help(self):
        print ('flies project create [PROJECT_ID] [OPTIONS]') 

    def _iteration_info_help(self):
	    print ('flies iteration info [OPTIONS]')

    def _iteration_create_help(self):
        print ('flies iteration create [ITERATION_ID] [OPTIONS]')

    def _publican_push_help(self):
        print ('flies publican push [OPTIONS] {document}')

    def _publican_pull_help(self):
        print ('flies publican pull [OPTIONS] {document}')
              
    def _list_projects(self):
        if not self.options['server']:
            print "Please provide valid server url by fliesrc or by '--server' option"
            sys.exit()
        
        flies = FliesClient(self.options['server'])
        res, content = flies.list_projects()
        print 'Status: '+res['status']
        if res.get('status') == '200':
            projects = json.loads(content)
            for project in projects:
                print "*"*40
                print project
        else:
            print 'Flies REST service not available at %s' % self.options['server']
        
    def _get_project(self):
        if not self.options['server']:
            print "Please provide valid server url by fliesrc or by '--server' option"
            sys.exit()
        
        if not self.options['project_id']:
            print 'Please use flies project info --project=project_id to retrieve the project info'
            sys.exit()
        
        flies = FliesClient(self.options['server'])
        res, content = flies.get_project_info(self.options['project_id'])
        print 'Status: '+res['status']
        print content
        
    def _get_iteration(self):
        if not self.options['server']:
            print "Please provide valid server url by fliesrc or by '--server' option"
            sys.exit()
        
        if not self.options['iteration_id'] or not self.options['project_id']:
            print 'Please use flies iteration info --project=project_id --iteration=iteration_id to retrieve the iteration'
            sys.exit()

        flies = FliesClient(self.options['server'])
        res, content = flies.get_iteration_info(self.options['project_id'], self.options['iteration_id'])
        print 'Status: '+res['status']
        print content
                
    def _create_project(self, args):
        if not self.options['server']:
            print "Please provide valid server url by fliesrc or by '--server' option"
            sys.exit()
    
        if self.options['user'] and self.options['apikey']:
            flies = FliesClient(self.options['server'], self.options['user'], self.options['apikey'])
        else:
            print "Please provide username and apikey in .fliesrc"
            sys.exit()
        
        try:
            result = flies.create_project(args[0], self.options['name'], self.options['desc'])
            if result == "Success":
                print "Success create the project"
        except NoSuchProjectException as e:
            print "No Such Project on the server" 
        except UnAuthorizedException as e:
            print "Unauthorized Operation"
        except InvalidOptionException as e:
            print "Options are not valid"

    def _create_iteration(self, args):
        if not self.options['server']:
            print "Please provide valid server url by fliesrc or by '--server' option"
            sys.exit()

        if self.options['user'] and self.options['apikey']:
            flies = FliesClient(self.options['server'], self.options['user'], self.options['apikey'])
        else:
            print "Please provide username and apikey in .fliesrc"
            sys.exit()
        
        if not args:
            print "Please provide ITERATION_ID for creating iteration"
            sys.exit()
         
        try:
            result = flies.create_iteration(self.options['project_id'], args[0], self.options['name'],
            self.options['desc'])
            if result == "Success":
                print "Success create the itearion"
        except NoSuchProjectException as e:
            print "No Such Project on the server"
        except UnAuthorizedException as e:
            print "Unauthorized Operation"
        except InvalidOptionException as e:
            print "Options are not valid"

    def _push_publican(self, args):
        if not self.options['server']:
            print "Please provide valid server url by fliesrc or by '--server' option"
            sys.exit()
        
        if self.options['user'] and self.options['apikey']:
            flies = FliesClient(self.options['server'], self.options['user'], self.options['apikey'])
        else:
            print "Please provide username and apikey in .fliesrc"
            sys.exit()

        if not args:
            print "Please provide at least one file name for processing"
            sys.exit()

        for filename in args:
            try:
       	        result = flies.push_publican(filename, self.options['project_id'], self.options['iteration_id'])
                if result == "Success":
                    print "Success push the content of %s to %s"%(filename, self.options['project_id'])
            except NoSuchFileException as e:
       	        print "Can not find file"
            except UnAuthorizedException as e:
                print "Unauthorized Operation"
            except NoSuchProjectException as e:
                print "No Such Project on the server"

    def _pull_publican(self):
        pass

    def _remove_project(self):
        pass

    def _remove_iteration(self):
        pass

    def _project_status(self):
        pass
    
    def _process_command_line(self):
        try:
            opts, args = getopt.gnu_getopt(sys.argv[1:], "v", ["server=", "project=", "iteration=", "name=", "description="])
        except getopt.GetoptError, err:
            print str(err)
            sys.exit(2)

        if args:
            command = args[0]
            sub = args[1:]            
            if sub_command.has_key(command):
                if sub_command[command]:
                    if sub[0]:
                        if sub[0] in sub_command[command]:
                            command = command+'_'+sub[0]
                            command_args = sub[1:]
                        else:
                            print "Can not find such command"
                            sys.exit()
                    else:
                        print "Please complete the command!"
                        sys.exit()
                else: 
                    command_args = sub
            else:
                print "Can not find such command"
                sys.exit()
        else:
            self._print_usage()
            sys.exit(2)
                         
        if opts:
            for o, a in opts:
                if o in ("--server"):
                    self.options['server'] = a
                elif o in ("--name"):
                    self.options['name'] = a
                elif o in ("--description"):
                    self.options['desc'] = a
                elif o in ("--project"):
                    self.options['project_id'] = a
                elif o in ("--iteration"):
                    self.options['iteration_id'] = a
    
        return command, command_args
 
    def run(self):
        command, command_args = self._process_command_line()        
        
        if command == 'help':
            self._print_help_info(command_args)
        elif command == 'list':
            self._list_projects()
        elif command == 'status':
            self._poject_status()
        elif command == 'project_info':
            self._get_project()
        elif command == 'project_create':
            self._create_project(command_args)
        elif command == 'project_remove':
            self._remove_project(command_args)
        elif command == 'iteration_info':
            self._get_iteration()
        elif command == 'iteration_create':
            self._create_iteration(command_args)
        elif command == 'iteration_remove':
            self._remove_iteration(command_args)
        elif command == 'publican_push':
            self._push_publican(command_args)
        elif command == 'publican_pull':
            self._push_publican(command_args)      
        

def main():
    client = FliesConsole()
    client.run()

if __name__ == "__main__":
    main()       
