import argparse
import dns.message
import dns.name
import dns.query
import dns.rdata
import dns.rdataclass
import dns.rdatatype

FORMATS = (("CNAME", "{alias} is an alias for {name}"),
           ("A", "{name} has address {address}"),
           ("AAAA", "{name} has IPv6 address {address}"),
           ("MX", "{name} mail is handled by {preference} {exchange}"))

# current as of 23 February 2017
ROOT_SERVERS = ("198.41.0.4",
                "192.228.79.201",
                "192.33.4.12",
                "199.7.91.13",
                "192.203.230.10",
                "192.5.5.241",
                "192.112.36.4",
                "198.97.190.53",
                "192.36.148.17",
                "192.58.128.30",
                "193.0.14.129",
                "199.7.83.42",
                "202.12.27.33")


def collect_results(name: str) -> dict:
    """
    This function parses final answers into the proper data structure that
    print_results requires. The main work is done within the `lookup` function.
    """
    full_response = {}
    target_name = dns.name.from_text(name)
    # lookup CNAME
    response = lookup(target_name, dns.rdatatype.CNAME)
    cnames = []
    for answers in response.answer:
        for answer in answers:
            cnames.append({"name": answer, "alias": name})
    # lookup A
    response = lookup(target_name, dns.rdatatype.A)
    arecords = []
    for answers in response.answer:
        a_name = answers.name
        for answer in answers:
            if answer.rdtype == 1:  # A record
                arecords.append({"name": a_name, "address": str(answer)})
    # lookup AAAA
    response = lookup(target_name, dns.rdatatype.AAAA)
    aaaarecords = []
    for answers in response.answer:
        aaaa_name = answers.name
        for answer in answers:
            if answer.rdtype == 28:  # AAAA record
                aaaarecords.append({"name": aaaa_name, "address": str(answer)})
    # lookup MX
    response = lookup(target_name, dns.rdatatype.MX)
    mxrecords = []
    for answers in response.answer:
        mx_name = answers.name
        for answer in answers:
            if answer.rdtype == 15:  # MX record
                mxrecords.append({"name": mx_name,
                                  "preference": answer.preference,
                                  "exchange": str(answer.exchange)})

    full_response["CNAME"] = cnames
    full_response["A"] = arecords
    full_response["AAAA"] = aaaarecords
    full_response["MX"] = mxrecords

    return full_response


def lookup(target_name: dns.name.Name,
           qtype: dns.rdata.Rdata) -> dns.message.Message:
    """
    This function uses a recursive resolver to find the relevant answer to the
    query.
    """
    global target_hostnames
    target_hostnames = []

    if target_name not in target_hostnames:
        target_hostnames.append(target_name)
        x = 0
        ip_addresses = {}
        while (x < len(ROOT_SERVERS)):
            ip_addresses[x] = ROOT_SERVERS[x]
            x = x + 1

        try:
            for x in ip_addresses:
                response = recursive_dns(target_name, qtype, ip_addresses[x])
#                print("Lookup : ", target_name, ip[x])
                return response
        except:
            return None
    else:
        return None

no_of_queries = 0


def recursive_dns(target_name: dns.name.Name,
                  qtype: dns.rdata.Rdata,
                  ip_address: str):

    global no_of_queries
    global cache_data

    cache_data = []
    ip_cache = []

    no_of_queries = no_of_queries + 1

    if ip_address in cache_data:
        return None

    ip_cache.append(target_name)
    try:

        outbound_query = dns.message.make_query(target_name, qtype)
        response: dns.message.Message = dns.query.udp(outbound_query, ip_address, 3)

        if (len(response.answer) > 0):
            return response

        for value in response.index.values():
            values_in_rrset: dns.rrset.RRset = value
            if ((values_in_rrset.rdtype == 1) and (values_in_rrset.ttl > 0)):
                values_in_inner: dns.rrset.RRset = values_in_rrset.items
                for x in values_in_inner:
                        dns_reply: dns.message.Message \
                            = recursive_dns(target_name, qtype, str(x))
                        if dns_reply is not None and len(dns_reply.answer) > 0:
                            return dns_reply
        return response

    except:
        cache_data.add(ip_address)

        return None


def print_results(results: dict) -> None:
    """
    take the results of a `lookup` and print them to the screen like the host
    program would.
    """
    for rtype, fmt_str in FORMATS:
        for result in results.get(rtype, []):
            print(fmt_str.format(**result))


def main():
    """
    if run from the command line, take args and call
    printresults(lookup(hostname))
    """
    temp = []
    argument_list = []
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("name", nargs="+",
                                 help="DNS name(s) to look up")
    argument_parser.add_argument("-v", "--verbose",
                                 help="increase output verbosity",
                                 action="store_true")
    program_args = argument_parser.parse_args()
    print(program_args.name)

    temp = program_args.name

    argument_list = set(temp)  # To avoid duplicate entries
    for a_domain_name in argument_list:
        print_results(collect_results(a_domain_name))


if __name__ == "__main__":
    main()
