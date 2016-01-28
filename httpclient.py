#!/usr/bin/env python
# coding: utf-8
# Copyright 2013 Abram Hindle, 2016 Sarah Van Belleghem
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib

def help():
    print "httpclient.py [GET/POST] [URL]\n"

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):

    #separate the port number from the rest of the url if needed
    def get_host_port(self,url):
        get_port = url.split(":")
        url = get_port[0]

        #check if a port was given, otherwise go to port 80
        if (len(get_port) > 1):
            port = int(get_port[1])
        else:
            port = 80
        return url, port

    #establish a connection with the specified host page
    #http://effbot.org/zone/effnews.htm#effnews-1 2016/27/01
    def connect(self, host, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        return s

    #extract the headers from the page data
    def get_info(self,data):
        code_index = data.find("HTTP/1.")
        code = int(data[code_index+9:code_index+12])
        body_index = data.find("\r\n\r\n", 30)
        body  = data[body_index:]
        return code, body

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return str(buffer)

    #split the url provided into a host name and a path
    def split_url(self, url):
        url = url.strip("/")
        url = url.strip("http://")
        split_url = url.split("/")
        host = split_url.pop(0)
        path = "/"+"/".join(split_url)
        return path, host

    #get the quey from the path
    def get_query(self, path):
        split = path.split("?")
        path = split[0]
        if len(split) > 1:
            query = split[1]
        else:
            query = False
        return path, query

    #send a GET request for the specified page
    def GET(self, url, args=None):
        #get the host, path and port number
        path, host = self.split_url(url)
        host, port = self.get_host_port(host)

        #connect to the requested web page
        s = self.connect(host, port)
        path, query = self.get_query(path)

        if (args != None):
            query = urllib.urlencode(args)

        #send GET request
        if (query):
            message = "GET "+path+" HTTP/1.1\r\nHost: "+host+"\r\n"
            message += "Connection: close\r\n"
            message += "Content-Length: "+str(len(query))+"\r\n"
            message += "Content-Type: application/x-www-form-urlencoded\r\n\r\n"
            message += query
            s.sendall(message)
        else:
            s.sendall("GET "+path+" HTTP/1.1\r\nHost: "+host+"\r\nContent-Length: 0\r\nConnection: close\r\n\r\n")
        
        #look for a reply on the socket
        data = self.recvall(s)

        #close the connection
        s.close()

        #Parse the returned data
        code,body = self.get_info(data)

        return HTTPResponse(code, body)

    #send a POST request to the specified url
    def POST(self, url, args=None): 
        #get the host, path and port number
        path, host = self.split_url(url)
        host, port = self.get_host_port(host)

        #connect to the requested web page
        s = self.connect(host, port)
        path, host = self.split_url(url)

        #check for attached query
        path, query = self.get_query(path)

        if (args != None):
            query = urllib.urlencode(args)

        #send POST request
        if (query):
            message = "POST "+path+" HTTP/1.1\r\nHost: "+host+"\r\n"
            message += "Connection: close\r\n"
            message += "Content-Length: "+str(len(query))+"\r\n"
            message += "Content-Type: application/x-www-form-urlencoded\r\n\r\n"
            message += query
            s.sendall(message)
        else:
            s.sendall("POST "+path+" HTTP/1.1\r\nHost: "+host+"\r\nContent-Length: 0\r\nConnection: close\r\n\r\n")

        #look for a reply on the socket
        data = self.recvall(s)

        #close the connection
        s.close()

        #Parse the returned data
        code,body = self.get_info(data)
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print client.command( sys.argv[2], sys.argv[1] )
    else:
        print client.command( sys.argv[1] )   