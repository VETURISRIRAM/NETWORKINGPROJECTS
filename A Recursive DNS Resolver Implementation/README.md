## Recursive DNS Resolver

The goal of this project is to recreate the functionality of a recursive DNS resolver.
The program is not allowed to perform any recursive queries (i.e.
request that another server perform recursion for it); it performs all
recursion itself.


### Getting Setup

You'll need to install
the [dnspython](http://www.dnspython.org/) library though.  You can do so
using [pip](https://pip.pypa.io/en/stable/).  In most cases you can
do so by running one of the following commands on your system:

 * `pip3 install dnspython`
 * `pip install dnspython`
 * `python -m pip install dnspython`


### The Implementation

The program
takes a domain name, and returns a summary of DNS information about the domain.
For example, given the domain "yahoo.com", `host` returns the "A", "AAAA"
and "MX" records for the domain.  You can test this out by running
the `resolve.py` command as so: `python resolve.py yahoo.com`.

You can lookup multiple domains in the same execution by passing multiple
domains to the program (e.g. `python resolve.py first.com second.edu third.org`).

In this project, the recursive functionality is implemented. The `resolve.py` will
query a root server itself, as well as performing any further needed
queries.

**Note : The IP addresses of the root servers are hard coded into the `resolve.py`
in the global `ROOT_SERVERS` list. 


### Handling Errors

The code also handles cases where the DNS servers are down or slow to respond. The
[rules governing DNS and how to handle errors](https://tools.ietf.org/html/rfc1034)
are very complex. In this assignment, the following simplified set of rules are used for handling errors. 

 * For all queries, the timeout value is 3 seconds.  Any request taking
   more than 3 seconds to respond should be treated as non-responsive.
 * You should exhaustively try all available servers when trying to answer
   a query.  For example, if a request to a root server gives you
   13 servers for the ".com" zone, you should try each of those 13 servers
   before giving up.
 * If you receive an error or non-response from a server, you should not
   retry the server.  Only query each server once.
 * Only query servers over IPv4.  You should not query servers over IPv6 when
   trying to resolve domains.

Your code should never throw an exception.  Dumping a stacktrace is not
an appropriate response for any query.  If you are unable to get a result
for a domain, your code should not print nothing out.

### Helpful Links 
 * [TCP IP Guide](http://www.tcpipguide.com/free/t_TCPIPDomainNameSystemDNS.htm)
 * [IANA DNS Parameters](http://www.iana.org/assignments/dns-parameters/dns-parameters.xhtml)
