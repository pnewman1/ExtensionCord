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
from ecapp.models import *
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import simplejson
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist

import json

true = True
false = False

def restAPI(request):
    """The information page for the REST API"""
    return render_to_response('rest_guide.html',context_instance=RequestContext(request))


def _add_one_testplan(data):
    try:
        plan = TestPlan()
        if 'name' in data:
            plan.name = data['name']
        else:
            return 'FAIL: "name" must be provided'
            
        if 'creator' in data:
            try:
                plan.creator = User.objects.get(username=data['creator'])
            except ObjectDoesNotExist:
                return 'FAIL: creator %s not found' % data['creator']
        else:
            return 'FAIL: "creator" must be provided'
            
        if 'start_date' in data:
            plan.start_date = data['start_date']
        else:
            return "FAIL: 'start_date' must be provided"
            
        if 'enabled' in data:
            plan.enabled = data['enabled']
        if 'schedule' in data:
            plan.schedule = data['schedule']
        if 'release' in data:
            plan.release = data['release']
        if 'end_date' in data:
            plan.end_date = data['end_date']
        if 'leader' in data:
            plan.leader = data['leader']

        plan.save()

        # now that we have a plan, we can add testcases to it
        if 'testcase_ids' in data:
            for testcase_id in data['testcase_ids']:
                tptc = TestplanTestcaseLink()
                tptc.testplan_id = plan.id
                tptc.testcase_id = testcase_id
                tptc.save()

        return str(plan.id)
    except Exception as e:
        # remove the plan if it got created, so it can be imported after fixed
        if plan.id:
            plan.delete()
        return "FAIL: %s" % e


@csrf_exempt
def rest_testplan(request, name = None):
    if request.method == "GET":
        try:
            data = {}
            try:
                testplan = TestPlan.objects.get(name=name)
            except ObjectDoesNotExist:
                message = "No test plan found with name '%s'." % name
                return HttpResponse(simplejson.dumps(message))

            for key,value in vars(testplan).items():
                if key == "creator_id":
                    data['creator'] = str(testplan.creator.username)
                elif key != "_state":
                    data[key] = str(value)

            data['test_case_ids'] = map(int, testplan.testcases.all().values_list('pk', flat=True))

            return HttpResponse(simplejson.dumps(data))

        except Exception as e:
            return HttpResponse('Unknown Error "%s"\n' % e)

    elif request.method == "POST":
        """ Add one or more TestPlan.
        INPUT:
        A JSON array of TestPlan objects to add. Only name and start_date are required.
        EXAMPLE: will add 2 test plans, one complete and one minimal:
        [
          {
            "name": "A new Test Plan! string <= 255 chars",
            "creator": "someuser", # the username of the creator
            "start_date": "2013-01-15",
            "end_date": "2013-02-15", // optional
            "enabled": false, // optional, boolean, default true
            "schedule": "string <= 20 chars", // optional
            "release": "string <= 50 chars", // optional
            "leader": "string <= 300 chars" // optional
            "testcase_ids": [1,2,3,4,5], // optional, list of existing TC IDs
          },
          {
            "name": "Another new Test Plan! string <= 255 chars",
            "start_date": "2012-01-01",
            "creator": "someuser"
          }
        ]
        OUTPUT:
        An array of strings, one per input object. 
        Each item is either the new testplan_id or an error message.
        The indices of the output array will match those of the input array.
        A sample response from an input array of length 7, showing 6 successes and 1 error:
        ["1","2","3","FAIL: 'name' must be provided","4","5","6"]
        """
        replydata = []
        try:
            data = json.loads(request.raw_post_data)
            for entry in data:
                replydata.append( _add_one_testplan(entry) )

        except Exception as e:
            return HttpResponse( simplejson.dumps( {'message': "FAIL: Received Exception '%s'" % e } ) )
        return HttpResponse( simplejson.dumps(replydata) )
    else:
        return HttpResponse( simplejson.dumps( {'message': 'FAIL: POST or GET required.'} ) )

@csrf_exempt
def rest_add_tc_to_existing_tp(request):
    """ Add TestCases to an existing TestPlan.

    INPUT:
    A JSON dictionary containing TestPlan ID and array of TestCase IDs to be added to the TestPlan.
    EXAMPLE: will add two TestCases to the TestPlan:
    {
      "testplan_id": 76,
      "testcase_list": [52502,52580]
    }
    """
    if request.method == "POST":
        try:
            testplan = json.loads(request.raw_post_data)
            tp_id = testplan['testplan_id']
            tc_list = testplan['testcase_list']
            for testcase_id in tc_list:
                tptc = TestplanTestcaseLink()
                tptc.testplan_id = tp_id
                tptc.testcase_id = testcase_id
                tptc.save()
        except Exception as e:
            return HttpResponse( simplejson.dumps( {'message': "FAIL: Received Exception '%s'" % e } ) )
        return HttpResponse( simplejson.dumps( {'message': "SUCCESS: TestCases added.%"} ) )
    else:
        return HttpResponse( simplejson.dumps( {'message': 'FAIL: POST required.'} ) )

def _folderpath_to_folderid(folder_path):
    folder_path_list = folder_path.strip().strip("/").split("/")
    parent_id = 1
    for folder_name in folder_path_list:
        try:
            folder = Folder.objects.get(name=folder_name, parent_id=parent_id)
            folder_id = folder.id
            parent_id = folder.id
        except Folder.DoesNotExist:
            folder_id = 0
    return folder_id

def _add_one_testcase(data):
    try:
        case = TestCase()

        if 'name' in data:
            case.name = data['name']
        else:
            return 'FAIL: "name" must be provided'
            
        if 'description' in data:
            case.description = data['description']
        else:
            return 'FAIL: "description" must be provided'
            
        if 'author' in data:
            try:
                case.author = User.objects.get(username=data['author'])
            except ObjectDoesNotExist:
                return 'FAIL: author %s not found' % data['author']
        else:
            return 'FAIL: "author" must be provided'
            
        if 'folder_id' in data:
            folder = Folder.objects.get(pk=data['folder_id'])
            case.folder = folder
            case.folder_path = folder.folder_path()
        elif 'folder_path' in data:
            folder_id = _folderpath_to_folderid(data['folder_path'])
            if folder_id == 0:
                return 'FAIL: The provided path does not exist'
            else:
                folder = Folder.objects.get(pk=folder_id)
                case.folder = folder
                case.folder_path=data['folder_path']
        else:
            return 'FAIL: "folder_id" or "folder_path must be provided'
            

        if 'enabled' in data:
            case.enabled = data['enabled']
        if 'is_automated' in data:
            case.is_automated = data['is_automated']
        if 'added_version' in data:
            case.added_version = data['added_version']
        if 'deprecated_version' in data:
            case.deprecated_version = data['deprecated_version']
        if 'bug_id' in data:
            case.bug_id = data['bug_id']
        if 'language' in data:
            case.language = data['language']
        if 'test_script_file' in data:
            case.test_script_file = data['test_script_file']
        if 'method_name' in data:
            case.method_name = data['method_name']
        if 'import_id' in data:
            case.import_id = data['import_id']
        if 'priority' in data:
            case.priority = data['priority']
        if 'product' in data:
            case.product = data['product']
        if 'case_type' in data:
            case.case_type = data['case_type']

        case.save()

        # override automatic creation_date saving by resetting
        if 'creation_date' in data:
            case.creation_date = data['creation_date']
            case.save()

        # now that we have a case, we can add it to specified test plans
        if 'testplan_ids' in data:
            for testplan_id in data['testplan_ids']:
                tptc = TestplanTestcaseLink()
                tptc.testplan_id = testplan_id
                tptc.testcase_id = case.id
                tptc.save()

        # we can also add design steps to it
        if 'design_steps' in data:
            for step_data in data['design_steps']:
                step = DesignStep()
                step.step_number = step_data['step_number']
                step.procedure = step_data['procedure']
                step.expected = step_data['expected']
                if 'comments' in step_data:
                    step.comments = step_data['comments']
                else:
                    step.comments = ""
                if 'import_id' in step_data:
                    step.import_id = step_data['import_id']
                step.save() 
                case.design_steps.add(step)

        return str(case.id)
    except Exception as e:
        # remove the case if it got created, so it can be imported after fixed
        if case.id:
            case.delete()
        return "FAIL: %s" % e

@csrf_exempt
def rest_testcase(request, id = -1):

    if request.method == "GET":
        try:
            data = {}

            try:
                case = TestCase.objects.get(id=id)
            except ObjectDoesNotExist:
                message = "No test case found with name '%s'." % name
                return HttpResponse(simplejson.dumps(message))

            for key,value in vars(case).items():
                if value is None:
                    value = ""

                if key == "author_id":
                    author = User.objects.get(id=value).username
                    data['author'] = author
                elif key == 'folder_id':
                    folder = Folder.objects.get(id=value).name
                    data['folder'] = folder
                elif key != "_state":
                    data[str(key)] = str(value)

            return HttpResponse(simplejson.dumps(data))

        except Exception:
            return HttpResponse(simplejson.dumps('Unknown Error'))

    elif request.method == "POST":
        """ Add TestCase(s).
        INPUT:
        A JSON array of TestCase objects to add.
        EXAMPLE: will add 2 test cases, one complete and one minimal:
        [
          {
            "name": "A new Test Case! string <= 255 chars",
            "description": "An awesome new Test Case",
            "author": "someuser", # the username of the testcase author
            "enabled": false, // optional, boolean, default true
            "is_automated": false, // optional, boolean, default false
            "folder_id": 2, // ID of folder the TestCase belongs in
            "added_version": "string <= 100 chars", // optional
            "deprecated_version": "string <= 100 chars", // optional
            "bug_id": "string <= 100 chars", // optional
            "language": "J", // optional, P for Python (default) or J for Java
            "test_script_file": "/some/path/to/script.sh", // optional, <= 1000 chars
            "method_name": "MethodUnderTest", // optional, <= 255 chars
            "import_id": 42, // optional, ID for the item in external DB
            "creation_date": "2013-01-15T12:00:00", // optional, defaults to 'now'
            "priority": "P2", // optional, <= 10 chars
            "product": "Purchase", // optional, <= 20 chars
            "case_type": "Regression", // optional, <= 30 chars, default is 'Regression'
            "testplan_ids": [1,2,3], // optional, array of IDs of testplans this case is in
            "design_steps": // optional, array of design steps for test case
              [
                {
                  "step_number": 1,
                  "procedure": "Ask for the meaning of life",
                  "expected": "Get answer 42",
                  "comments": "But now we need the question", // optional
                  "import_id": 42 // optional
                },
                {
                  "step_number": 2,
                  "procedure": "Ask for the question of life",
                  "expected": "Get 'Thanks for all the fish'",
                }
              ]
          },
          {
            "name": "A minimal Test Case!",
            "description": "A very merry Test Case",
            "author": "someuser",
            "folder_id": 2
          }
        ]
        OUTPUT:
        An array of strings, one per input object. 
        Each item is either the new testcase_id or an error message.
        The indices of the output array will match those of the input array.
        A sample response from an input array of length 7, showing 6 successes and 1 error:
        ["1","2","3","FAIL: 'name' must be provided","4","5","6"]
        """
        replydata = []
        try:
            data = json.loads(request.raw_post_data)
            for entry in data:
                replydata.append( _add_one_testcase(entry) )

        except Exception as e:
            return HttpResponse( simplejson.dumps( {'message': "FAIL: Received Exception '%s'" % e } ) )
        return HttpResponse( simplejson.dumps(replydata) )

    else:
        return HttpResponse(simplejson.dumps('Only GET requests allowed'))

@csrf_exempt
def rest_result(request):
    if request.method == "GET":
        data = []
        results = Result.objects.all()

        if 'testcase_name' not in request.GET and 'testcase_id' not in request.GET and 'testplan_name' not in request.GET:
            return HttpResponse("FAIL: no testcase or testplan specified")

        if 'testcase_id' in request.GET or 'testcase_name' in request.GET:
            testcase = None
            if 'testcase_id' in request.GET:
                try:
                    testcase = TestCase.objects.get(id=request.GET['testcase_id'])
                except ObjectDoesNotExist:
                    return HttpResponse("No testcase found for testcase_id %s." % request.GET['testcase_id'])
            if 'testcase_name' in request.GET:
                testcases = TestCase.objects.filter(name=request.GET['testcase_name'])
                if len(testcases) > 1:
                    return HttpResponse("Multiple testcases found for name '%s'. Try using testcase_id or removing dupes." 
                            % (request.GET['testcase_name']) )
                if len(testcases) == 0:
                    return HttpResponse("No testcase found for testcase_name '%s'." % request.GET['testcase_name'])
                testcase = testcases[0]

            results = results.filter(testplan_testcase_link__testcase=testcase,latest=True)

        if 'testplan_name' in request.GET:
            try:
                testplan = TestPlan.objects.get(name=request.GET['testplan_name'])
                results = results.filter(testplan_testcase_link__testplan=testplan, latest=True)
            except ObjectDoesNotExist:
                return HttpResponse("No result found for testplan '%s'." % request.GET['testplan_name'])

        # results do a vars trick here to make a dict of key value of useful info, include tc/tp name & id
        # also add a template description
        for result in results:
            result_dict = {}
            for key,value in vars(result).items():
                if value is None:
                    value = ""

                if key == "testcase_id":
                    result_dict['test_case'] = result.testplan_testcase_link.testcase.name
                    result_dict['test_case_id'] = result.testplan_testcase_link.testcase.id
                elif key == "testcase_name":
                    result_dict['test_case'] = result.testplan_testcase_link.testcase.name
                    result_dict['test_case_name'] = result.testplan_testcase_link.testcase.name
                elif key =="testplan_id":
                    result_dict['test_plan'] = result.testplan_testcase_link.testplan.name
                    result_dict['test_plan_id']  = result.testplan_testcase_link.testplan.id
                elif key != "_state" and key != "id":
                    result_dict[str(key)] = str(value)
            data.append(result_dict)
        return HttpResponse(simplejson.dumps(data))

    elif request.method == "POST":
        #saves a result of a test case under a test plan
        """Adds results to the database when called through the rest API
        Returns a reply dictionary in json. An example looks like:
        {
          'testplan_name': 'some_plan_name',
          'testcase_id': 1, (or 'testcase_name': 'some cool testcase',)
          'result': 'passed',
          'username': 'pnewman',
          'message': 'FAIL: that test case is not under the test plan',
          'result_type': 'Invalid match'
        }
        """
        try:

            #this dictionary will be what is returned to the user in json
            reply_dict = {}

            try:
                testplan_name = request.POST['testplan_name']
                result = request.POST["result"]
                username = request.POST["username"]

                reply_dict['testplan_name'] = testplan_name
                reply_dict['result'] = result
                reply_dict['username'] = username

                testcase_id = None
                testcase_name = None
                if 'testcase_id' in request.POST: 
                    testcase_id = int(request.POST["testcase_id"])
                    reply_dict['testcase_id'] = testcase_id
                elif 'testcase_name' in request.POST: 
                    testcase_name = request.POST["testcase_name"]
                    reply_dict['testcase_name'] = testcase_name
                else:
                    raise Exception()

                ninja_id = None
                if 'ninja_id' in request.POST:
                    ninja_id = request.POST["ninja_id"]
                    reply_dict['ninja_id'] = ninja_id

                comments = ""
                if 'comments' in request.POST:
                    comments = request.POST['comments']
                    reply_dict['comments'] = comments

            except:
                # display what parameters users provided
                post_params = []
                for post_param in request.POST:
                    post_params.append(post_param)

                reply_dict['message'] = "FAIL: required parameters '%s' not found. You provided '%s'." % ( ['testplan_name','testcase_name or testcase_id','result','username'], post_params )
                reply_dict['result_type'] = 'Invalid parameters'

                return HttpResponse(simplejson.dumps(reply_dict))

            # make sure testplan exists
            try:
                testplan = TestPlan.objects.get(name=testplan_name, enabled=True)
            except ObjectDoesNotExist:
                reply_dict['message'] = "FAIL: no enabled testplans found for name '%s'" % (testplan_name)
                reply_dict['result_type'] = "Invalid testplan"
                return HttpResponse(simplejson.dumps(reply_dict))

            # make sure testcase exist
            testcase = None
            if testcase_id:
                try:
                    testcase = TestCase.objects.get(id=testcase_id)
                except ObjectDoesNotExist:
                    reply_dict['message'] = "FAIL: given testcase_id '%d' does not exist" % (testcase_id)
                    reply_dict['result_type'] = "Invalid testcase"
                    return HttpResponse(simplejson.dumps(reply_dict))
            else:
                testcases = TestCase.objects.filter(name=testcase_name, enabled=True)
                if len(testcases) > 1:
                    reply_dict['message'] = "FAIL: Multiple enabled testcases found for name '%s'. Try using testcase_id or removing dupes" % (testcase_name)
                    reply_dict['result_type'] = "Invalid testcase"
                    return HttpResponse(simplejson.dumps(reply_dict))
                if len(testcases) == 0:
                    reply_dict['message'] = "FAIL: no enabled testcases found for name '%s'" % (testcase_name)
                    reply_dict['result_type'] = "Invalid testcase"
                    return HttpResponse(simplejson.dumps(reply_dict))
                testcase = testcases[0]

            # check if username is in the db, if not return error
            # note that a user in the active directory is not in the database
            # unless he/she logs in at least once through the normal interface
            try:
                tester = User.objects.get(username=username)
            except ObjectDoesNotExist:
                reply_dict['message'] = "FAIL: username '%s' does not exist. Have you logged into the website at least once?" % (username)
                reply_dict['result_type'] = "Invalid username"
                return HttpResponse(simplejson.dumps(reply_dict))

            # check if test case is under a test plan, if not return error
            if testcase not in testplan.testcases.all():
                reply_dict['message'] = 'FAIL: that test case is not under the test plan'
                reply_dict['result_type'] = 'Invalid match'
                return HttpResponse(simplejson.dumps(reply_dict))

            #everything passes save result
            testplan_testcase_link = TestplanTestcaseLink.objects.get(testplan=testplan, testcase=testcase)
            Result(testplan_testcase_link=testplan_testcase_link,status=result,tester=tester,ninja_id=ninja_id,note=comments).save()

            message = "SUCCESS: case %d: '%s' in plan %d: '%s' recorded as %s" % (testcase.id, testcase.name, testplan.id, testplan.name, result)
            reply_dict['message'] = message
            reply_dict['result_type'] = 'Success'
            return HttpResponse(simplejson.dumps(reply_dict))

        # exception catch-all
        except Exception as err:
            reply_dict['message'] = "FAIL: '%s'" % (err)
            reply_dict['result_type'] = 'Unknown error'
            return HttpResponse(simplejson.dumps(reply_dict))

    else:
        return HttpResponse( simplejson.dumps( {'message': 'FAIL: POST or GET required.'} ) )


def rest_find_tests_by_folder(request, folder_id):
    
    if request.method == "GET":
        try:
            data = {}
            try:
                folder = Folder.objects.get(id__exact=folder_id)
                data['folder_id'] = int(folder_id)
                data['parent_id'] = folder.parent_id
                data['folder'] = str(folder)
                data['folder_path'] = str(folder.folder_path())
                test_cases = TestCase.objects.filter(folder__id__exact=folder_id).values("id", "name")
                data['test_cases'] = []
                for test_case in test_cases:
                    data['test_cases'].append({"id": test_case['id'], "name": test_case['name']})
            except ObjectDoesNotExist:
                message = "No folder found with name '%s'." % name
                return HttpResponse(simplejson.dumps(message))


            return HttpResponse(simplejson.dumps(data))

        except Exception as e:
            return HttpResponse('Unknown Error "%s"\n' % e)

