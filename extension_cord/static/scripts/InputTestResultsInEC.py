####
#
# Copyright (c) 2013, Rearden Commerce Inc. All Rights Reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
####
import sys
import json
import urllib
import datetime

# This script will POST test results JSON to the Extension Cord server.
#
# It also creates a .txt file containing details of which tests passed and
# failed.
#
# Usage:
# $ python InputTestResultsInEC.py jsonFile url
#
# Arguments:
#   jsonFile - a file containing an array of test results to load into EC
#   url - the REST URL for EC
#
# Example:
#   python InputTestResultsInEC.py result.json http://extensioncord/api/result/
#
# The json file should look something like this:
#[
#    {
#        "testcase_id": 7,
#        "testplan_name: "A Unique TestPlan Name",
#        "result": "passed",
#        "username": "someuser",
#        "ninja_id": "ninjaIDhere"
#    },
#    {
#        "testcase_name": "A Unique TestCase Name",
#        "testplan_name: "A Unique TestPlan Name",
#        "result": "failed",
#        "username": "someuser",
#        "ninja_id": "ninjaIDhere"
#    },
#    {
#        "testcase_id": 8,
#        "testplan_name: "Another Unique Name",
#        "result": "notcomplet",
#        "username": "someuser"
#    }
#]
#

if len(sys.argv) < 3:
    sys.exit('\nERROR: Please provide the required parameters.\n\nUsage:\n\t$ python InputTestResultsInEC.py jsonfile url\nExample:\n\t$ python InputTestResultsInEC.py results.json http://extensioncord.mygazoo.com/api/result\n')

jsonFile = sys.argv[1]
url = sys.argv[2]

# use input file basename for output file
outfile = open( jsonFile.split(".")[0]  + "_log.txt", 'a' )

succeeded = 0
failed = 0

outfile.write( "New Execution at: %s\n" % (str(datetime.datetime.now()).split(".")[0]) )
outfile.write( "--------------\n\n")

cases = json.load( open(jsonFile) )

for (item, case) in enumerate(cases):

    #urllib.urlencode encodes a dictionary to this format: "testplan_name=A%20Unique%20Name&testcase_id=1&result=notcomplet&username=someuser&ninja_id=coolID"
    f = urllib.urlopen( url, urllib.urlencode(case) )
    
    #reply_dict is the status of submission in json format
    reply_dict = eval( f.read() )
    
    if reply_dict['result_type'] == 'Success':
        succeeded += 1
    else:
        failed += 1

    outfile.write( 'Item index %d:\n' % (item) )
    outfile.write( '  data: %s\n' % (case) )
    outfile.write( '  Message: %s\n\n' % (reply_dict['message']) )

outfile.close()

print( "Successful submissions: %d" % (succeeded) )
print( "Failed submissions: %d" % (failed) )
print( "Total submissions: %d" % (len(cases)) )
