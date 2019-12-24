#!/usr/bin/env python

"""Return if a website or subdomains are hosted on AWS.

Usage:
  ip-checker check (--website-list FILE) [--export-json=<filename>] [--export-csv=<filename>] [-vd]
  ip-checker --version
  ip-checker --help

Modes of operation:
  check                         Display if site is hosted in AWS.

Options:
  -h, --help                    Show this help message and exit.
  --version                     Display version info and exit.
  -w FILE, --website-list FILE  List of websites / urls to check in JSON format. (../big_data_london_exhibitors.json)
  --export-json<filename>       Exports results to a JSON file.
  --export-csv<filename>        Exports results in CSV format.
  -v, --verbose                 Log to activity to STDOUT at log level INFO.
  -d, --debug                   Increase log level to 'DEBUG'. Implies '--verbose'.

"""
import csv
import json
import logging
import urllib.request
import socket
from tabulate import tabulate

from docopt import docopt
from netaddr import IPNetwork, IPAddress
import tldextract

IP_RANGE_SOURCE_ADDRESS = "https://ip-ranges.amazonaws.com/ip-ranges.json"

def get_logger(args):
    """
    Setup basic logging.
    Return logging.Logger object.
    """
    # log level
    log_level = logging.CRITICAL
    if args['--verbose'] or args['check']:
        log_level = logging.INFO
    if args['--debug']:
        log_level = logging.DEBUG

    log_format = '%(name)s: %(levelname)-9s%(message)s'
    if args['--debug']:
        log_format = '%(name)s: %(levelname)-9s%(funcName)s():  %(message)s'
    if (('--export-json' in args and not args['--export-json']) and not args['check']):
        log_format = '[dryrun] %s' % log_format

    logFormatter = logging.Formatter(log_format)
    rootLogger = logging.getLogger()
    rootLogger.setLevel(log_level)

    #add console appened
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)

    rootLogger.addHandler(consoleHandler)

    return rootLogger


def load_aws_ip_ranges(log, url):
    with urllib.request.urlopen(url) as url:
        data = json.loads(url.read().decode())
    log.info("Load successful, found %s records" %(len(data['prefixes'])))
    return data


def load_websites_from_file(log, file_name):
    log.debug("loading file '%s'" % file_name)
    with open(file_name) as f:
        websites = json.loads(f.read())
    log.info("Found: %s webites to check." %(len(websites)))
    return websites

def clean_website_address(log, site):
    #check if value domain name
    parsed = tldextract.extract(site)
    return parsed.registered_domain


def check_websites_against_ip_ranges(log, args, ip_ranges, website_list):
    #loop over websites
    results = []
    for site in website_list:
        #obtain ip addresses from DNS
        parsed_url = clean_website_address(log, site)
        log.info("Checking %s " %(parsed_url))
        if parsed_url:
            try:
                ip_addresses = socket.gethostbyname(parsed_url)
                log.info("Site: %s = %s" % (parsed_url, ip_addresses))
                for current_ip_range in ip_ranges['prefixes']:
                    if IPAddress(ip_addresses) in IPNetwork(current_ip_range['ip_prefix']):
                        #remove generic AMAZON service
                        if current_ip_range['service'] != 'AMAZON':
                            log.info("MATCH! %s is in region: %s service: %s" %(parsed_url, current_ip_range['region'], current_ip_range['service']))
                            result = {}
                            result['url'] = parsed_url
                            result['ip'] = ip_addresses
                            result['region'] = current_ip_range['region']
                            result['service'] = current_ip_range['service']
                            results.append(result)

            except:
                log.error("Socket error: failed to connect to website %s " % (parsed_url))
        else:
            log.info("Cannot parse website: %s" % (site))

    if len(results) > 0:
        log.info("Found: %s matches." % (len(results)))
        print('\n')
        print('Results: %s' % (len(results)))
        print(tabulate(results))

    #write result to file if --export-json flag is set
    if args['--export-json']:
        log.debug("Exporting data to file: %s.json" %(args['--export-json']))
        with open(args['--export-json'], 'w') as outfile:
            json.dump(results, outfile)

    #write results to csv file if export-csv flaf is set
    if args['--export-csv']:
        log.debug("Exporting data to file: %s.csv" %(args['--export-csv']))
        with open(args['--export-csv'], mode='w') as outfile:
            csvwriter = csv.writer(outfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            count = 0
            for result in results:
                if count == 0:
                    header = result.keys()
                    csvwriter.writerow(header)
                    count += 1
                csvwriter.writerow(result.values())


def main():
    args = docopt(__doc__, version='1.0')
    log = get_logger(args)

    #load IP ranges from AWS JSON data source
    log.info("Loading AWS IP Ranges...")
    ip_ranges = load_aws_ip_ranges(log, IP_RANGE_SOURCE_ADDRESS)

    #load websites from file
    log.info("Loading website urls...")
    website_list = load_websites_from_file(log, args['--website-list'])

    #check websites against AWS ranges
    log.info("Checking websites against AWS IP ranges...")
    check_websites_against_ip_ranges(log, args, ip_ranges, website_list)

if __name__ == "__main__":
    main()

