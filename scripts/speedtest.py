#!/usr/local/munkireport/munkireport-python3

# show external_ip_isp in listing

import os
import subprocess
import sys
import plistlib
import platform
import json
import time

import xml.etree.ElementTree as ET
from Foundation import CFPreferencesCopyAppValue

sys.path.insert(0, '/usr/local/munkireport')
from munkilib.purl import Purl
from Foundation import NSHTTPURLResponse
from munkilib import osutils

def get_networkquality():

    speedtest = {'start_time':str(int(time.time()))}
    output = json.loads(bashCommand(['/usr/bin/networkQuality', '-s', '-c']))

    if 'base_rtt' in output:
        speedtest['base_rtt'] = int(output['base_rtt'])
    if 'dl_flows' in output:
        speedtest['dl_flows'] = str(output['dl_flows'])
    if 'dl_responsiveness' in output:
        speedtest['dl_responsiveness'] = str(output['dl_responsiveness'])
    if 'dl_throughput' in output:
        speedtest['dl_throughput'] = str(output['dl_throughput'])
    if 'dl_bytes_transferred' in output:
        speedtest['dl_bytes_transferred'] = str(output['dl_bytes_transferred'])
    if 'interface_name' in output:
        speedtest['interface_name'] = output['interface_name']
    if 'test_endpoint' in output:
        speedtest['test_endpoint'] = output['test_endpoint']
    if 'ul_bytes_transferred' in output:
        speedtest['ul_bytes_transferred'] = str(output['ul_bytes_transferred'])
    if 'ul_flows' in output:
        speedtest['ul_flows'] = str(output['ul_flows'])
    if 'ul_responsiveness' in output:
        speedtest['ul_responsiveness'] = str(output['ul_responsiveness'])
    if 'ul_throughput' in output:
        speedtest['ul_throughput'] = str(output['ul_throughput'])

    speedtest['end_time'] = str(int(time.time()))
    speedtest['latest'] = 1

    return speedtest

def get_speedtest_net_config():

    isp_data = {}
    isp_data['external_ip'] = ""
    isp_data['isp'] = ""
    isp_data['isp_rating'] = ""
    isp_data['country'] = ""
    isp_data['lat'] = ""
    isp_data['lon'] = ""

    # Check if getting the ISP config from Speedtest.net is enabled, by default it is disabled
    speedtest_get_isp = str(get_pref_value('speedtest_get_isp', 'MunkiReport'))

    if speedtest_get_isp == "True":
        try:
            isp_xml = curl("https://www.speedtest.net/speedtest-config.php")
            tree = ET.ElementTree(ET.fromstring(isp_xml))
            root = tree.getroot()
            xmldict = XmlDictConfig(root)

            isp_data['external_ip_isp'] = xmldict['client']['ip']
            isp_data['isp'] = xmldict['client']['isp']
            isp_data['isp_rating'] = xmldict['client']['isprating']
            isp_data['country'] = xmldict['client']['country']

            # Check if setting the location from Speedtest.net is enabled, by default it is disabled
            speedtest_get_isp = str(get_pref_value('speedtest_get_location', 'MunkiReport'))
            if speedtest_get_isp == "True":
                isp_data['lat'] = xmldict['client']['lat']
                isp_data['lon'] = xmldict['client']['lon']

            return isp_data

        except Exception:
            return isp_data
    else:
        return isp_data

def get_network_data():

    # Gets data from the network module's cache file
    network_data = {}

    try:
        # Network cache file
        cachedir = '%s/cache' % os.path.dirname(os.path.realpath(__file__))
        network_plist = os.path.join(cachedir, 'networkinfo.plist')

        # Make sure the nertwork cache file exists and we can open it
        if os.path.isfile(network_plist):
            with open(network_plist, 'rb') as infile:
                network_cache = plistlib.load(infile)
            infile.close()

        network_index = 0
        # Get the index of the first active network device when going by service order
        for idx, interface in enumerate(network_cache):
            if "status" in interface and interface['status'] == 1:
                network_index = idx
                break

        # Fill in network data for later comparisons
        if network_cache[network_index]:
            if "externalip" in network_cache[network_index]:
                network_data['external_ip'] = network_cache[network_index]['externalip']

                # If we're not getting the external IP from speedtest.net, try to get it from the network module
                speedtest_get_isp = str(get_pref_value('speedtest_get_isp', 'MunkiReport'))
                if speedtest_get_isp != "True":
                    network_data['external_ip_isp'] = network_cache[network_index]['externalip']

            if 'dhcp_domain_name' in network_cache[network_index]:
                network_data['dhcp_domain_name'] = network_cache[network_index]['dhcp_domain_name']
            if 'dhcp_domain_name_servers' in network_cache[network_index]:
                network_data['dhcp_domain_name_servers'] = network_cache[network_index]['dhcp_domain_name_servers']
            if 'dhcp_routers' in network_cache[network_index]:
                network_data['dhcp_routers'] = network_cache[network_index]['dhcp_routers']
            if 'dhcp_subnet_mask' in network_cache[network_index]:
                network_data['dhcp_subnet_mask'] = network_cache[network_index]['dhcp_subnet_mask']
            if 'ipv4router' in network_cache[network_index]:
                network_data['ipv4router'] = network_cache[network_index]['ipv4router']
            if 'ipv4ip' in network_cache[network_index]:
                network_data['ipv4ip'] = network_cache[network_index]['ipv4ip']
            if 'ipv4dns' in network_cache[network_index]:
                network_data['ipv4dns'] = network_cache[network_index]['ipv4dns']
            if 'ipv4mask' in network_cache[network_index]:
                network_data['ipv4mask'] = network_cache[network_index]['ipv4mask']

            if 'ipv6router' in network_cache[network_index]:
                network_data['ipv6router'] = network_cache[network_index]['ipv6router']
            if 'ipv6ip' in network_cache[network_index]:
                network_data['ipv6ip'] = network_cache[network_index]['ipv6ip']
            if 'ipv6mask' in network_cache[network_index]:
                network_data['ipv6mask'] = network_cache[network_index]['ipv6mask']

        return network_data

    except Exception:
        return network_data

def debug_msg(msg):

    # Prints debug messages if enabled
    debug_enabled = str(get_pref_value('speedtest_debug_enabled', 'MunkiReport'))
    if debug_enabled == "True":
        print(msg)

def get_pref_value(key, domain):

    value = CFPreferencesCopyAppValue(key, domain)

    if(value is not None):
        return value
    elif(value is not None and len(value) == 0):
        return ""
    else:
        return ""

def bashCommand(script):
    proc = subprocess.Popen(script, shell=False, bufsize=-1,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (output, unused_error) = proc.communicate()
    return output

def hide_curl_log(msg, *args):
    # Empty function to hide curl log output
    pass

def curl(url):
    # Curl function lovingly copied from reportcommon.py 

    options = dict()
    options["url"] = url
    options["logging_function"] = hide_curl_log # Local function to suppress messages
    options["connection_timeout"] = 10 # Set connection timeout
    options["follow_redirects"] = False # Set follow_redirects

    # Build Purl with initial settings
    connection = Purl.alloc().initWithOptions_(options)
    connection.start()
    try:
        while True:
            # if we did `while not connection.isDone()` we'd miss printing
            # messages if we exit the loop first
            if connection.isDone():
                break

    except (KeyboardInterrupt, SystemExit):
        # safely kill the connection then re-raise
        connection.cancel()
        raise
    except Exception as err:  # too general, I know
        # Let us out! ... Safely! Unexpectedly quit dialogs are annoying...
        connection.cancel()
        # Re-raise the error as a GurlError
        print("Error: -1 "+connection.error.localizedDescription())
        return ""

    if connection.error != None:
        # Gurl returned an error
        if connection.SSLerror:
            print("SSL error detail: %s", str(connection.SSLerror))
        print("Error: "+ str(connection.error.code()), connection.error.localizedDescription())
        return ""

    if connection.response != None and connection.status != 200:
        print("Status: %s", connection.status)
        print("Headers: %s", connection.headers)
    if connection.redirection != []:
        print("Redirection: %s", connection.redirection)

    connection.headers["http_result_code"] = str(connection.status)
    description = NSHTTPURLResponse.localizedStringForStatusCode_(connection.status)
    connection.headers["http_result_description"] = description

    if str(connection.status).startswith("2"):
        return connection.get_response_data()
    else:
        # there was an HTTP error of some sort.
        print(connection.status, "%s failed, HTTP returncode %s (%s)"
            % (url, connection.status, connection.headers.get("http_result_description", "Failed"),),
        )
        return ""

class XmlListConfig(list):
    def __init__(self, aList):
        for element in aList:
            if element:
                # treat like dict
                if len(element) == 1 or element[0].tag != element[1].tag:
                    self.append(XmlDictConfig(element))
                # treat like list
                elif element[0].tag == element[1].tag:
                    self.append(XmlListConfig(element))
            elif element.text:
                text = element.text.strip()
                if text:
                    self.append(text)

class XmlDictConfig(dict):
    '''
    Example usage:

    >>> tree = ElementTree.parse('your_file.xml')
    >>> root = tree.getroot()
    >>> xmldict = XmlDictConfig(root)

    Or, if you want to use an XML string:

    >>> root = ElementTree.XML(xml_string)
    >>> xmldict = XmlDictConfig(root)

    And then use xmldict for what it is... a dict.
    '''
    def __init__(self, parent_element):
        if list(parent_element.items()):
            self.update(dict(list(parent_element.items())))
        for element in parent_element:
            if len(element):
                # treat like dict - we assume that if the first two tags
                # in a series are different, then they are all different.
                if len(element) == 1 or element[0].tag != element[1].tag:
                    aDict = XmlDictConfig(element)
                # treat like list - we assume that if the first two tags
                # in a series are the same, then the rest are the same.
                else:
                    # here, we put the list in dictionary; the key is the
                    # tag name the list elements all share in common, and
                    # the value is the list itself 
                    aDict = {element[0].tag: XmlListConfig(element)}
                # if the tag has attributes, add those to the dict
                if list(element.items()):
                    aDict.update(dict(list(element.items())))
                self.update({element.tag: aDict})
            # this assumes that if you've got an attribute in a tag,
            # you won't be having any text. This may or may not be a 
            # good idea -- time will tell. It works for the way we are
            # currently doing XML configuration files...
            elif list(element.items()):
                self.update({element.tag: dict(list(element.items()))})
            # finally, if there are no child tags and no attributes, extract
            # the text
            else:
                self.update({element.tag: element.text})


def main():
    '''Main'''

    # Check if getting speedtest module is enabled, by default it is disabled
    speedtest_enabled = str(get_pref_value('speedtest_enabled', 'MunkiReport'))
    if speedtest_enabled == "False":
        print('Error: The speedtest module is disabled')
        exit(0)

    # Check OS version and skip if too old, needs at least macOS Monterey
    if os.path.isfile('/usr/bin/networkQuality') == False:
        print('Skipping Speedtest check, OS does not have networkQuality')
        exit(0)

    # Make sure we have the networkinfo cache file from the Network module
    cachedir = '%s/cache' % os.path.dirname(os.path.realpath(__file__))
    network_plist = os.path.join(cachedir, 'networkinfo.plist')
    if os.path.isfile(network_plist) == False:
        print('Error: The speedtest module requires the network module')
        exit(0)

    output_plist = os.path.join(cachedir, 'speedtest.plist')

    # Check that we're not already running a speedtest
    myname = os.path.basename(sys.argv[0])
    other_pid = osutils.pythonScriptRunning(myname)
    if other_pid:
        # Another instance of this script is running, so we should quit
        print('Another instance of %s is running as pid %s, exiting.'% (myname, other_pid))
        exit(0)

    # Check how many results we have in the cache file
    if os.path.isfile(output_plist):
        with open(output_plist, 'rb') as infile:
            speedtest_cache = plistlib.load(infile)
            infile.close()

        result = speedtest_cache

        # Set initial speedtest run state
        run_speedtest = 0

        # Check if we are to run the speedtest because of the override
        if os.path.isfile('/Users/Shared/.com.github.munkireport.speedtest'):
            print('Running speedtest because of override')
            run_speedtest_override = 1
            try:
                os.remove("/Users/Shared/.com.github.munkireport.speedtest")
            except OSError:
                run_speedtest_override = 0
        else:
            run_speedtest_override = 0 # Set this to 1 for testing


        # Get network module's cache data
        network_data = get_network_data()

        test_iteration = 0

        # Check if we have any previous matching networks
        for idx, prev_result in enumerate(speedtest_cache):

            # Check if we have the same external IP address
            if "external_ip" in prev_result and "external_ip" in network_data and prev_result['external_ip'] == network_data['external_ip']:
                debug_msg("Duplicate external IP address")

                # Check if we are to refresh the speedtest every week, off by default
                speedtest_weekly = str(get_pref_value('speedtest_weekly_run', 'MunkiReport'))
                if speedtest_weekly == "True" or run_speedtest_override == 1:
                    debug_msg("Weekly run, external IP address")
                    # Check if the last run was over 1 week ago
                    if ("end_time" in prev_result and (int(prev_result['end_time']) + 604800) < int(time.time())) or run_speedtest_override == 1:
                        debug_msg("Refreshing speedtest, external IP address")
                        run_speedtest = 1
                        test_iteration = speedtest_cache[idx]['iteration']

                        # Delete the previous matching
                        del speedtest_cache[idx]
                        debug_msg("Breaking at refreshing speedtest, external IP address")

                        break

                debug_msg("Breaking at external IP address")
                run_speedtest = 0
                break

            elif "external_ip" in prev_result and "external_ip" in network_data and prev_result['external_ip'] != network_data['external_ip']:
                debug_msg("New external IP address: ")
                debug_msg("Previous: "+prev_result['external_ip'])
                debug_msg("New:      "+network_data['external_ip'])
                run_speedtest = 1

            match = 0

            # print(prev_result)
            # print(network_data)

            # Check for matching data from previous run
            if "dhcp_domain_name" in prev_result and "dhcp_domain_name" in network_data and prev_result['dhcp_domain_name'] == network_data['dhcp_domain_name']:
                match = match + 1
                debug_msg("Match on dhcp_domain_name")

            if "dhcp_domain_name_servers" in prev_result and "dhcp_domain_name_servers" in network_data and prev_result['dhcp_domain_name_servers'] == network_data['dhcp_domain_name_servers']:
                match = match + 1
                debug_msg("Match on dhcp_domain_name_servers")

            if "dhcp_routers" in prev_result and "dhcp_routers" in network_data and prev_result['dhcp_routers'] == network_data['dhcp_routers']:
                match = match + 1
                debug_msg("Match on dhcp_routers")

            if "dhcp_subnet_mask" in prev_result and "dhcp_subnet_mask" in network_data and prev_result['dhcp_subnet_mask'] == network_data['dhcp_subnet_mask']:
                match = match + 1
                debug_msg("Match on dhcp_subnet_mask")

            if "ipv4router" in prev_result and "ipv4router" in network_data and prev_result['ipv4router'] == network_data['ipv4router']:
                match = match + 1
                debug_msg("Match on ipv4router")

            if "ipv4ip" in prev_result and "ipv4ip" in network_data and prev_result['ipv4ip'] == network_data['ipv4ip']:
                match = match + 1
                debug_msg("Match on ipv4ip")

            if "ipv4dns" in prev_result and "ipv4dns" in network_data and prev_result['ipv4dns'] == network_data['ipv4dns']:
                match = match + 1
                debug_msg("Match on ipv4dns")

            if "ipv4mask" in prev_result and "ipv4mask" in network_data and prev_result['ipv4mask'] == network_data['ipv4mask']:
                match = match + 1
                debug_msg("Match on ipv4mask")

            if "ipv6router" in prev_result and "ipv6router" in network_data and prev_result['ipv6router'] == network_data['ipv6router']:
                match = match + 1
                debug_msg("Match on ipv6router")

            if "ipv6ip" in prev_result and "ipv6ip" in network_data and prev_result['ipv6ip'] == network_data['ipv6ip']:
                match = match + 1
                debug_msg("Match on ipv6ip")

            if "ipv6mask" in prev_result and "ipv6mask" in network_data and prev_result['ipv6mask'] == network_data['ipv6mask']:
                match = match + 1
                debug_msg("Match on ipv6mask")

            debug_msg("Match count: " + str(match))

            # If we have 3 or more matches, consider it a duplicate network
            if match >= 3:
                debug_msg("Duplicate network")

                # Check if we are to refresh the speedtest every week, off by default
                speedtest_weekly = str(get_pref_value('speedtest_weekly_run', 'MunkiReport'))
                if speedtest_weekly == "True" or run_speedtest_override == 1:
                    debug_msg("Weekly run, duplicate network")
                    # Check if the last run was over 1 week ago
                    if ("end_time" in prev_result and (int(prev_result['end_time']) + 604800) < int(time.time())) or run_speedtest_override == 1:
                        debug_msg("Refreshing speedtest, duplicate network")
                        run_speedtest = 1
                        test_iteration = speedtest_cache[idx]['iteration']

                        # Delete the previous matching
                        del speedtest_cache[idx]
                        debug_msg("Breaking at refreshing speedtest, duplicate network")

                        break

                debug_msg("Breaking at duplicate network")
                run_speedtest = 0
                break

            else:
                debug_msg("New network")
                run_speedtest = 1

        # Run speedtest
        if run_speedtest == 1:

            debug_msg("Running speedtest...")

            # Remove previous latest keys
            for idx, prev_result in enumerate(speedtest_cache):
                if "latest" in prev_result:
                    del speedtest_cache[idx]['latest']

            # Get results
            result = dict()
            result = get_networkquality()
            debug_msg("Finished speedtest")

            # Make sure we have a proper result with a download speed
            if result['dl_throughput'].isdigit() and int(result['dl_throughput']) > 0:
                result.update(get_speedtest_net_config())
                result.update(network_data)
                result["iteration"] = test_iteration + 1

                # Check if we are to to only save the latest (current) network, no by default
                speedtest_current_only = str(get_pref_value('speedtest_current_only', 'MunkiReport'))
                if speedtest_current_only == "True":
                    pass
                else:

                    speedtest_cache.append(result)

                    # If more than 5 speedtest results, remove the oldest
                    if len(speedtest_cache) > 5:
                        debug_msg("More than 5 entries, deleting")
                        del speedtest_cache[0]

                    # Clean up bad cached entries
                    for idx, prev_result in enumerate(speedtest_cache):
                        if 'dl_throughput' in prev_result and prev_result['dl_throughput'].isdigit() and int(prev_result['dl_throughput']) > 0:
                            # debug_msg("good entry")
                            # debug_msg(prev_result['dl_throughput'])
                            pass
                        else:
                            if 'dl_throughput' not in prev_result:
                                debug_msg("No dl_throughput entry!")
                            else:
                                debug_msg("Bad dl_throughput entry: ")
                                debug_msg(prev_result['dl_throughput'])
                            del speedtest_cache[idx]

                    result = speedtest_cache

                # Write speedtest results to cache file
                try:
                    plistlib.writePlist(result, output_plist)
                except:
                    with open(output_plist, 'wb') as fp:
                        plistlib.dump(result, fp, fmt=plistlib.FMT_XML)

    else:
        debug_msg("First speedtest entry")
        # Get results
        result = dict()
        result = get_networkquality()
        debug_msg("Finished speedtest")

        # Make sure we have a proper result with a download speed
        if result['dl_throughput'].isdigit() and int(result['dl_throughput']) > 0:
            result.update(get_speedtest_net_config())
            result.update(get_network_data())
            result["iteration"] = 1

            speedtest_cache = []
            speedtest_cache.append(result)
            result = speedtest_cache

            # Write speedtest results to cache file
            try:
                plistlib.writePlist(result, output_plist)
            except:
                with open(output_plist, 'wb') as fp:
                    plistlib.dump(result, fp, fmt=plistlib.FMT_XML)
        else:
            debug_msg("Network too slow")

#    print plistlib.writePlistToString(result)

if __name__ == "__main__":
    main()
