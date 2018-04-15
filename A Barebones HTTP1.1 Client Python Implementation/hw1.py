import socket
import sys
import logging

def retrieve_url(url):

	# Initializing the Socket

	s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	
	# Splitting the URL for the HTTP/HTTPS protocols

	split = url.split("://")
	schema=split[0]
	url=split[1]

	# Splitting the path of the webpage

	split2=url.split("/")
	path=""

	if len(split2)==1:
		path=path+'/'
	else:
		url=split2[0]
		for x in range(1, (len(split2))):
			path=path+"/"+split2[x]

	# Searching for the port number in the URL. If found, initialize port number as specified

	split3=url.split(":")
	url=split3[0]

	portString=""
	portNumber=80

	# Handling the HTTPS protocol

	if schema.startswith('https')==True:
		print("")
	if len(split3)>1:
		portString=":"+split3[1]
		portNumber=int(split3[1])

	#print(url)
	#print(portNumber)
	# GET request to be sent

	r = "GET "+path+" HTTP/1.1\r\nHOST:"+url+"\r\nConnection:close\r\n\r\n"

	#print(r.encode(encoding="utf-8"))
	# Connecting to the URL and port number

	try:
		s.connect((url,portNumber))
		s.send(r.encode(encoding='utf-8', errors='strict'))
		
		final_response2 = b""
		final_response=s.recv(512)
		while len(final_response)>0:
			final_response2= final_response2+final_response
			final_response=s.recv(512)
		#content1=final_response2


		split4=final_response2.split(b"\r\n\r\n")
		headers=split4[0].decode(encoding="utf-8")
		source_code=split4[1]
		#print("SHIT")
		if(headers.find("Chunked")>0 or headers.find("chunked")>0):
			source_code = Chunked_data(source_code)
		#print(source_code)

	except:
		s.close() # Closing the Socket connection
		return None
	
	#print(content1.decode(encoding="utf-8"))
	#header_response=s.recv(4096).decode(encoding="utf-8")
	#print(header_response)
	#seperating Headers and the Source content
	#print(headers)

	# Split the header content and check if the status code returned is 200

	split5=headers.split(" ")
	status_code=split5[1]
	if(status_code=="200"):
		return source_code
	else:
		return None

# Handling the chuncked files in the URL list.

def Chunked_data(source): 
	var = source.decode(encoding='utf-8', errors='ignore')
	sizechunkdata = var[:var.find("\r\n")]
	first_bit = len(sizechunkdata) + len(b"\r\n")
	last_bit = first_bit + (int(bytes(sizechunkdata.encode()),16))
	chunk_reply = b''

	while (sizechunkdata!=0):
		chunk_reply=chunk_reply+source[first_bit : last_bit]
		var=source[last_bit+len(b'\r\n'):].decode(encoding='utf-8',errors='ignore')
		sizechunkdata=var[:var.find("\r\n")]
		if(len(sizechunkdata)==0):
			sizechunkdata=0
			continue
		first_bit = last_bit + len(sizechunkdata) + 2 * len(b"\r\n")
		last_bit = first_bit + (int(bytes(sizechunkdata.encode()),16))
	return chunk_reply

#retrieve_url("http://www.example.com")