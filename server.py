
import sys
import re
import os
import string,cgi,time
from os import curdir, sep
from BaseHTTPServer import *
from SimpleHTTPServer import *
from threading import *

from SocketServer import ThreadingMixIn

class MyHandler(BaseHTTPRequestHandler):

    def do_GET(self):
	try:
	    print 'Path=%s' % self.path

	    if self.path.endswith(".fits"):
		file_mime_type = "application/force-download"
		file = curdir + sep + 'fits' + sep + os.path.basename (self.path)
		file_size = os.path.getsize(file)

		self.send_response(200)
		self.send_header('Content-Description', 'File Transfer')
		self.send_header('Content-Type', '%s' % file_mime_type)
		self.send_header('Content-Disposition',  'attachment; filename=%s' % os.path.basename(self.path))
		self.send_header('Content-Transfer-Encoding', 'binary')
		self.send_header('Expires', '0')
		self.send_header('Cache-Control',  'must-revalidate, post-check=0, pre-check=0')
		self.send_header('Pragma', 'public')
		self.send_header('Content-Length', '%d' % file_size)
		self.end_headers()

		print "sending %s %d" % (file, file_size)

		f = open(file, "rb")
		try:
		    buffer = f.read(file_size)
		    print "sending %d bytes " % (len(buffer))
		    if len(buffer) > 0:
			self.wfile.write (buffer)
		finally:
		    f.close()

		print "%s sent" % (file)

		return

	except IOError:
	    self.send_error(404,'File Not Found: %s' % self.path)

	self.end_headers()
	self.wfile.write("<br>GET OK.<BR><BR>");
     

    def do_POST(self):
        global rootnode
	print 'post'
        try:
            ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
            if ctype == 'multipart/form-data':
                query=cgi.parse_multipart(self.rfile, pdict)
	    self.send_response(200)
            
            self.end_headers()
            upfilecontent = query.get('upfile')
            print "filecontent", upfilecontent[0]
            self.wfile.write("<HTML>POST OK.<BR><BR>");
            self.wfile.write(upfilecontent[0]);
            
        except :
            pass

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""


def main():

    port = 8080
    address = '127.0.0.1'
    
    i = 0
    for arg in sys.argv:
	i += 1
	if (i == 1):
	    continue

	if (re.match ('port=', arg)):
	    port = re.sub ('port=', '', arg)
	elif (re.match ('address=', arg)):
	    address = re.sub ('address=', '', arg)

    try:
	server_address = (address, port)
	server = ThreadedHTTPServer(server_address, MyHandler)

	sa = server.socket.getsockname()
	print "Serving HTTP on", sa[0], "port", sa[1], "..."

        server.serve_forever()

    except KeyboardInterrupt:
        print '^C received, shutting down server'
	t = 0
	while active_count () > 1:
	    n = active_count ()
	    print 'n=%d<br>' % (n)
	    sys.stdout.flush()
	    time.sleep (1)
	    t +=1
	    server.socket.close()

if __name__ == '__main__':
    main()

