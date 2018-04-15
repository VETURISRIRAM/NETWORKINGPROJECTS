# A Barebones HTTP/1.1 Client

In this project, a barebones web client is implemented and although python includes a basic http client module `http.client`, this project translated the protocol into implementation.
. This project contains a client which only implements the
`GET` method and follows the basics of the HTTP/1.1 specification, enough to
download files as one would with the command line program `curl`.

## HTTP/1.1 Features

[HTTP/1.0](https://tools.ietf.org/search/rfc1945) describes the most basic
functionality that an HTTP client is required to do. HTTP/1.1 includes several
new features that extend the protocol. For this project, following additional features are implemented:

  * Include a `Host:` header
  * Correctly interpret `Transfer-encoding: chunked`
  * Include a `Connection: close` header, or handle persistent connections

These new features are described in James Marshall's excellent [HTTP Made Really Easy](https://www.jmarshall.com/easy/http/#http1.1clients) under the HTTP/1.1
clients subsection.


## Basic HTTP functionality

HTTP is a stateless request-response protocol that consists
of an initial line, zero or more headers, and zero or more bytes of content.
The program has a function implementation, `retrieve_url`, which takes a url (as
a `str`) as its only argument, and uses the HTTP protocol to retrieve and
return the body's bytes.

The assumption is that the URL will not include a fragment, query string, or
authentication credentials. It is not required to follow any redirects -
only return bytes when receiving a `200 OK` response from the server. If for
any reason the program cannot retrieve the resource correctly, `retrieve_url`
returns `None`.


## Testing Script

A testing script is also provided, `client_test.py`. You will need to install the
[requests](http://docs.python-requests.org/en/master/) library to use it
(this can be done using `pip install requests`, or possibly
  `pip3 install requests`, depending on your setup). 

One you have `requests` installed, you can call the testing script with
`python ./client_test.py` (with an optional `--debug` flag to provide more
information).  The testing script will compare your implementation of the
`retrieve_url` function with a correct one, when calling a set of URLs.
