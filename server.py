#  coding: utf-8 
import socketserver, os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
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
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):

    def create_html_response(self, code):
        if code == 404:
            message = "Page Not Found"
            body = "<!DOCTYPE html>\n<head><meta charset='UTF-8'></head>\n<html>\n<body>\n" +  str(code) + ":" + message + "\n" "</body>\n</html>" 
            length_body = len(body)
            return length_body, body
        elif code == 405:
            message = " Method Not Allowed"
            body = "<!DOCTYPE html>\n<head><meta charset='UTF-8'></head>\n<html>\n<body>\n" +  str(code) + ":" + message + "\n" "</body>\n</html>" 
            length_body = len(body)
            return length_body, body
        elif code == 301:
            message = "Page Permanently Moved"
            body = "<!DOCTYPE html>\n<head><meta charset='UTF-8'></head>\n<html>\n<body>\n" +  str(code) + ":" + message + "\n" "</body>\n</html>" 
            length_body = len(body)
            return length_body, body

    def create_response(self, address, code):
        if code == 404:
            content_length, body = self.create_html_response(404)
            template = "HTTP/1.1 "+ str(code) + " " + "Not Found" + "\r\n" + "Content-Length: " + str(content_length) + "\r\n" + \
             "Content-Type: " + "text/html\r\n" + "Connection: Closed" + "\r\n\r\n" + body
            return template
        elif code == 405:
            content_length, body = self.create_html_response(405)
            template = "HTTP/1.1 405 Method Allowed\r\nConntection: Closed\r\n\r\n"
            return template

    def valid_response(self, path, file_type):
        f = open(path, 'r')
        content = f.read()
        # generate http headers for response back to client
        response = "HTTP/1.1 200 OK\r\n" + "Content-Type: " + file_type + "\r\n" + "Content-Length: " + str(len(content)) + "\r\n" + \
        "Connection: Closed\r\n\r\n" + content
        f.close()
        return response
    

    def moved_permanently_response(self, correct_path, file_type):
        f = open(correct_path+"index.html", 'r')
        content = f.read()
        response = "HTTP/1.1 301 Moved Permanently\r\n" + "Content-Type: " + file_type + "\r\n" + "Content-Length: " + str(len(content)) + "\r\n" + \
        "Connection: Closed\r\n\r\n" + content
        f.close()
        return response
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)
        # self.request.sendall(bytearray("OK",'utf-8'))
        decoded_arr = self.data.decode('utf-8')
        split_arr = decoded_arr.split()
        request_type = split_arr[0]
        address = split_arr[1]
        prefix = "www"
        file_type = ""

        # get the file type from path
        if ".html" in address:
            file_type = "text/html"
        elif ".css" in address:
            file_type = "text/css"
        
        if request_type == "GET":
            path = prefix+address
            # grab the first and last character of the path
            first_char = address[0]
            last_char = address[-1]
            char_match = first_char == "/" and last_char == "/"
            # handle /../
            if char_match:
                # make sure this is a directory
                if os.path.isdir(path):
                    file_path = prefix + address + "index.html"
                # make sure the index.html file exists
                    if os.path.isfile(file_path):
                        response = self.valid_response(file_path, "text/html")
                        self.request.sendall(bytearray(response,'utf-8'))
                else:
                    file_path = prefix+"/index.html"
                    response = self.valid_response(file_path, "text/html")
                    self.request.sendall(bytearray(response,'utf-8'))

            # handle the situation /..
            elif os.path.exists(path):
                if os.path.isfile(path):
                    response = self.valid_response(path, file_type)
                    self.request.sendall(bytearray(response,'utf-8'))

                # if path doesn't exist and adding a "/" makes it a valid directory
                elif os.path.isdir(path+"/"):
                    correct_path = path+"/"
                    # throw 301 error and redirect to correct page
                    response = self.moved_permanently_response(correct_path, file_type)
                    self.request.sendall(bytearray(response,'utf-8'))

            # /hardcode/index.html
            # elif "index.html" in path:
            #     correct_path = prefix+"/index.html"
            #     print("the filetype is:", file_type)
            #     response = self.valid_response(correct_path, file_type)
            #     self.request.sendall(bytearray(response,'utf-8'))

            else:
                # throw 404 Page Not Found
                response = self.create_response(address, 404)
                self.request.sendall(bytearray(response,'utf-8'))

        else:
            # throw 405 Method Not Allowed
            response = self.create_response(address, 405)
            self.request.sendall(bytearray(response,'utf-8'))

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
