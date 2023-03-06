#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This Skript fetches the IPs from a simple Text-File and
an external Alias from a opnsense via API.

After fetching, it comparse the content of the Text-File with
the content of the Alias, collects the Entries, which have the
following to be true in a Worklist:

- Not content of the opnsense Alias Table
- Is not already the the Worklist
- Is not a private Address
- Is not the external IP of the opnsense

After this process the new IPs in the Worklist will
be written into the Alias on the opnsense via API with https.

# Copyright Robert Friemer@ friem[media], 2022

"""
# ----------------------------------------------------------------------------------------- #
# Needed Modules
import socket
import requests
import ipaddress
import json
import time
import os


# ----------------------------------------------------------------------------------------- #
# Server2PF
class Server2PF:

    def __init__(self):
        # The Configuration
        self.server2ip = {'ip_list': '/path/to/ip-list.txt',                # Path to the Text-File
            'external_host':'<FQDN>',                                       # FQDN of your external IP, Your Domain or DynDNS
            'alias': 'server2pf',                                           # Name of the external ALias in opnsense
            'url_host': 'https://<IP of opnsense>/api/firewall/',           # URL to access your opnsense
            'url_list': 'alias_util/list/',                                 # API-Call to List the Content of Alias
            'url_add': 'alias_util/add/',                                   # API-Call to add Cntent to an Alias
            'url_del': 'alias_util/delete/',                                # API-Call to delete an Entry of an Alias
            'key': "<API-Key of User>",                                     # API Key of an User of opnsense
            'secret': "<Secret of User>",                                   # API Secret of an User of opnsense
            'fw_cert': "/path/to/Certificate.pem",                          # Path to Certificate
            'waitIntervall': 2}                                             # Time Period to wait between API-Calls

        self.badip_list = []
        self.alias_table = []
        self.worklist = []
        self.external_ip = ''

        self.url = ''
        self.command = ''
        self.zeile = ''

# ----------------------------------------------------------------------------------------- #
# Reading the file
    def read_file(self):

        if not os.path.isfile(self.server2ip['ip_list']):
            print("There are no IPs in the List. Stopping Script")
            os._exit(0)

        print("Reading the List ...")

        self.ipfile = open(self.server2ip['ip_list'], "r")

        self.content = self.ipfile.readlines()

        for self.zeile in self.content:
            self.badip_list.append(self.zeile.strip())

        self.ipfile.close()

        print("Imported %i IPs." % self.badip_list.__len__())

        self.command = "rm " + self.server2ip['ip_list']

        os.system(self.command)

# ----------------------------------------------------------------------------------------- #
# Get the external IP
    def get_external_host_ip(self):
        print("Fetch the external IP.")

        self.external_ip = socket.gethostbyname(self.server2ip['external_host'])

        print("The external IP is: %s" % self.external_ip)

# ----------------------------------------------------------------------------------------- #
# Get the ip-addresses from opnsense Alias 
    def get_tablelist(self):
        print("Fetch the external Alias from opnsense.")

        self.url = self.server2ip['url_host']+self.server2ip['url_list']+self.server2ip['alias']

        self.request = requests.post(url=self.url,
                                     auth=(self.server2ip['key'], self.server2ip['secret']),
                                     verify=self.server2ip['fw_cert'])

        self.alias_content = json.loads(self.request.text)

        for self.zeile in self.alias_content['rows']:
            self.alias_table.append(self.zeile['ip'])

# ----------------------------------------------------------------------------------------- #
# Compare the Lists
    def check_list(self):
        print("Comparing the Lists.")

        for self.content in self.badip_list:
            if (not self.content in self.alias_table) & (not self.content in self.worklist) & (not ipaddress.ip_address(self.content).is_private) & (self.content != self.external_ip):
                self.worklist.append(self.content)

# ----------------------------------------------------------------------------------------- #
# Transfer ip-addresses to opnsense Alias
    def block_ip(self):
        print("The IP-Adresses will be written.")

        if len(self.worklist) != 0:
            print("There are %i IPs to write." % self.worklist.__len__())
            for self.content in self.worklist:
                print("IP %s will be added" % self.content)
                self.payload = {'address': self.content + '/32'}

                self.url = self.server2ip['url_host']+self.server2ip['url_add']+self.server2ip['alias']

                self.request = requests.post(url=self.url,
                                             auth=(self.server2ip['key'], self.server2ip['secret']),
                                             verify=self.server2ip['fw_cert'], json=self.payload)

                print(self.request.status_code, self.request.text)

                print("Waitung %i Seconds" % self.server2ip['waitIntervall'])
                time.sleep(self.server2ip['waitIntervall'])

        else:
            print("There is nothing to do. :)")

# ----------------------------------------------------------------------------------------- #
# Delete external ip-Address from opnsense Alias
    def check_external_ip(self):

        if (self.external_ip in self.badip_list):
            print("The external IP will be deleted from the alias.")

            self.payload = {'address': self.external_ip + '/32'}

            self.url = self.server2ip['url_host']+self.server2ip['url_delete']+self.server2ip['alias']

            self.request = requests.post(url=self.url,
                                         auth=(self.server2ip['key'], self.server2ip['secret']),
                                         verify=self.server2ip['fw_cert'], json=self.payload)

        print("Finished! :)")


# ----------------------------------------------------------------------------------------- #
# Run Script

def main():
    # Let's start.
    server2pf = Server2PF()     	    # The Program is running.
    server2pf.read_file()        	    # The IP-List will be red.
    server2pf.get_external_host_ip()	# Fetch the external IP
    server2pf.get_tablelist()    	    # Fetch the IP from opnsense.
    server2pf.check_list()       	    # The Lists will be compared.
    server2pf.block_ip()         	    # The new IPs will bewritten to opnsense.
    server2pf.check_external_ip()       # Recheck, if the external IP-Addess is not in the list.

if __name__ == '__main__':
    main()
