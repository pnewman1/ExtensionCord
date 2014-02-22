####
#
# Copyright (c) 2013, Deem Inc. All Rights Reserved.
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
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core import serializers
from django.conf import settings
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.db.models import Q, Max, Count
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.db import connection

from pytz import timezone
from jira.client import JIRA
from jira.exceptions import JIRAError

import json
from exceptions import ValueError
from requests import ConnectionError

from ecapp.models import Folder, TestCase, TestPlan, Result, TestplanTestcaseLink, DesignStep, UploadedFile, User


def index(request):
    """ view for the home page"""
    return render_to_response('index.html',
                              context_instance=RequestContext(request))


def ajax_showresults(request, testplan_id, testcase_id):
    results = Result.objects.filter(testplan_testcase_link__testplan_id=testplan_id,
                                    testplan_testcase_link__testcase_id=testcase_id).order_by('-timestamp')
    return HttpResponse(json.dumps({"results": serializers.serialize('json', results),
                                    "testcase": TestCase.objects.get(id=testcase_id).name,
    }))


def ajax_plan_details(request):
    testplan_id = request.GET.get('testplan_id', None)
    folder_id = int(request.GET.get('key', '-100'))
    if folder_id == -100:
        folder_id = Folder.get_root_folder().id
    testplan_testcase_count = TestPlan.objects.get(pk=testplan_id).testcases.count()
    folder_testcase_count = TestPlan.objects.get(pk=testplan_id).testcases.filter(folder__id=folder_id).count()
    return HttpResponse(json.dumps({'testplan_testcase_count': testplan_testcase_count,
                                    'folder_testcase_count': folder_testcase_count
    })
    )


def ajax_fetch_designsteps(request, testcase_id):
    if testcase_id == '-1':
        design_steps = request.GET.get("designsteps", None)
        if design_steps:
            design_steps = [int(item) for item in design_steps.split(",")]
            design_steps = DesignStep.objects.filter(id__in=design_steps)
            design_steps = list(design_steps.values_list().order_by("step_number"))
        else:
            design_steps = []
    else:
        testcase = TestCase.objects.get(pk=testcase_id)
        design_steps = testcase.design_steps.all().values_list().order_by("step_number")
    return HttpResponse(
        json.dumps({"data": list(design_steps), "currpage": 1, "totalpages": 1, "totalrecords": len(design_steps)}))


def _set_designstep(design_step, querysetdict, testcase_id):
    for item in design_step._meta.fields:
        if item.name is not "id" and item.name is not "import_id":
            setattr(design_step, item.name, querysetdict[item.name])
    design_step.save()
    if not testcase_id == "-1":
        testcase = TestCase.objects.get(pk=testcase_id)
        if not testcase.design_steps.filter(pk=design_step.id).exists():
            testcase.design_steps.add(design_step)


def ajax_edit_designsteps(request, testcase_id):
    design_step = None
    if request.POST['oper'] == 'edit':
        design_step = DesignStep.objects.get(pk=int(request.POST['id']))
        _set_designstep(design_step, request.POST, testcase_id)
    elif request.POST['oper'] == 'add':
        design_step = DesignStep()
        _set_designstep(design_step, request.POST, testcase_id)
    elif request.POST['oper'] == 'del':
        if not testcase_id == "-1":
            design_step = DesignStep.objects.get(pk=int(request.POST['id']))
            testcase = TestCase.objects.get(pk=testcase_id)
            testcase.design_steps.remove(design_step)
            design_step.delete()
            design_step.save()
        else:
            design_step = DesignStep.objects.get(pk=int(request.POST['id']))
            design_step.delete()
            design_step.save()
    else:
        raise Exception("Invalid Operation")

    return HttpResponse(json.dumps(design_step.id))


def ajax_fetch_uploads(request, testcase_id):
    if testcase_id == '-1':
        uploads = request.GET.get("uploads", None)
        if uploads:
            uploads = [int(item) for item in uploads.split(",")]
            uploads = UploadedFile.objects.filter(id__in=uploads)
            uploads = list(uploads.values_list().order_by("id"))
        else:
            uploads = []
    else:
        testcase = TestCase.objects.get(pk=testcase_id)
        uploads = testcase.uploads.all().values_list().order_by("id")
    return HttpResponse(
        json.dumps({"data": list(uploads), "currpage": 1, "totalpages": 1, "totalrecords": len(uploads)}))


def _set_upload(upload, querysetdict, testcase_id):
    upload.caption = querysetdict["caption"]
    upload.save()
    if not testcase_id == "-1":
        testcase = TestCase.objects.get(pk=testcase_id)
        if not testcase.uploads.filter(pk=upload.id).exists():
            testcase.uploads.add(upload)


def ajax_edit_uploads(request, testcase_id):
    upload = None
    if request.POST['oper'] == 'edit':
        upload = UploadedFile.objects.get(pk=int(request.POST['id']))
        _set_upload(upload, request.POST, testcase_id)
    elif request.POST['oper'] == 'add':
        upload = UploadedFile()
        _set_upload(upload, request.POST, testcase_id)
    elif request.POST['oper'] == 'del':
        if not testcase_id == "-1":
            upload = UploadedFile.objects.get(pk=int(request.POST['id']))
            testcase = TestCase.objects.get(pk=testcase_id)
            testcase.uploads.remove(upload)
            upload.delete()
        else:
            upload = UploadedFile.objects.get(pk=int(request.POST['id']))
            upload.delete()
    else:
        raise Exception("Invalid Operation")

    return HttpResponse(json.dumps(upload.id))


def ajax_addtests(request, testplan_id):
    current_edit = []
    testplan = TestPlan.objects.get(id=testplan_id)
    add_array = request.GET['add']
    add_list = add_array.split(",")
    received_count = len(add_list)

    try:
        testplan = TestPlan.objects.get(id=testplan_id)
        initial_count = testplan.testcases.count()
        expected_count = initial_count + received_count

        for testcase_id in add_list:
            testplan_testcase_link = TestplanTestcaseLink(testplan=testplan,
                                                          testcase=TestCase.objects.get(pk=testcase_id))
            testplan_testcase_link.save()

        actual_count = testplan.testcases.count()
        if actual_count == expected_count:
            number = testplan.testcases.count() - initial_count
            alert_type = "alert-success"
            message = "Added %d tests to %s." % (received_count, testplan.name)
        elif actual_count == initial_count:
            alert_type = "alert-info"
            message = "No changes made to %s." % (testplan.name)
        else:
            alert_type = "alert-info"
            net_count = actual_count - initial_count
            present_count = received_count - net_count
            message = "Added %d tests to <em>%s<em>.\n%d tests already present." % (
                net_count, testplan.name, present_count)
        return HttpResponse(
            json.dumps({
                'currentEdit': current_edit,
                "alertType": alert_type,
                "alertflag": True,
                'message': message
            })
        )
    except ValueError, ex:
        return HttpResponse(
            json.dumps({
                "currentEdit": current_edit,
                "alertType": "alert-error",
                "alertflag": True,
                "message": "Please select the tests to add"
            })
        )


def ajax_removetests(request, testplan_id):
    current_edit = []
    testplan = TestPlan.objects.get(id=testplan_id)
    delete_array = request.GET['add']
    delete_list = delete_array.split(",")
    received_count = len(delete_list)

    try:
        testplan = TestPlan.objects.get(id=testplan_id)
        initial_count = testplan.testcases.count()
        expected_count = initial_count - received_count
        for testcase_id in delete_list:
            testplan_testcase_link = TestplanTestcaseLink.objects.get(testplan=testplan,
                                                                      testcase__id=testcase_id)
            testplan_testcase_link.delete()
        actual_count = testplan.testcases.count()
        if actual_count == expected_count:
            number = testplan.testcases.count() - initial_count
            alert_type = "alert-success"
            message = "Removed %d tests to %s." % (received_count, testplan.name)
        elif actual_count == initial_count:
            alert_type = "alert-info"
            message = "No changes made to %s." % (testplan.name)
        else:
            alert_type = "alert-info"
            net_count = initial_count - actual_count
            present_count = received_count - net_count
            message = "Deleted %d tests to <em>%s<em>.\n%d tests already deleted." % (
                net_count, testplan.name, present_count)
        return HttpResponse(
            json.dumps({
                'currentEdit': current_edit,
                "alertType": alert_type,
                "alertflag": True,
                'message': message
            })
        )
    except ValueError, ex:
        return HttpResponse(
            json.dumps({
                "currentEdit": current_edit,
                "alertType": "alert-error",
                "alertflag": True,
                "message": "Please select the tests to delete"
            })
        )


def get_status(testplan_id, testcase_id):
    """Gets the latest passed/failed/not finished status for a testcase in a testplan"""
    try:
        result = Result.objects.get(testplan_testcase_link__testplan_id=testplan_id,
                                    testplan_testcase_link__testcase_id=testcase_id,
                                    latest=True)

        settings_time_zone = timezone(settings.TIME_ZONE)
        updated_timestamp = result.timestamp.astimezone(settings_time_zone)
        status_return = {"timestamp": str(updated_timestamp), "bug_id": result.bug_ticket, "note": result.note}

        if result.status == 'passed':
            status_return["type"] = "badge-success"
            status_return["message"] = "Passed"
        elif result.status == 'failed':
            status_return["type"] = "badge-important"
            status_return["message"] = "Failed"
        elif result.status in ('blocked', 'future', 'na', 'notcomplet'):
            status_return["type"] = "badge-warning"
            if result.status in ('blocked', 'future'):
                status_return["message"] = result.status.capitalize()
            elif result.status == 'notcomplet':
                status_return["message"] = "Not Complete"
            else:
                status_return["message"] = "N/A"
        else:
            status_return = {"type": "nada", "message": "Notrun", "timestamp": "na", "bug_id": "", "note": ""}
    except ObjectDoesNotExist:
        status_return = {"type": "nada", "message": "Notrun", "timestamp": "na", "bug_id": "", "note": ""}

    return status_return


def ajax_folders(request):
    node = None
    if '-100' == request.GET.get('key', '-100'):
        node = Folder.get_root_folder()
    else:
        node = Folder.objects.get(pk=request.GET['key'])

    return HttpResponse(json.dumps({
        'id': node.id,
        'parent_id': node.parent_id,
        'node_list': node.child_nodes(request.GET.get('testplan_id', None)),
        'testplan_id': request.GET.get('testplan_id', None)
    }))


def folder_and_child_folders_list(folder_id):
    folder_and_child_folders_list = [folder_id]
    query_list = folder_and_child_folders_list
    has_child = True
    while has_child:
        if len(query_list) > 0:
            child_folders = Folder.objects.filter(parent_id__in=query_list)
            query_list = []
            for item in child_folders:
                folder_and_child_folders_list.append(item.id)
                query_list.append(item.id)
        else:
            has_child = False

    return folder_and_child_folders_list


def ajax_tests(request):
    enabled = True

    if 'disabled' in request.GET:
        enabled = (request.GET['disabled'] != "true")

    tests = TestCase.objects.filter(enabled=enabled).order_by('id')

    testplan_id = None
    if "planid" in request.GET:
        testplan_id = int(request.GET['planid'])
        if request.GET.get('add', 'false') == 'true':
            tests = tests.exclude(testplantestcaselink__testplan_id=testplan_id)
        else:
            tests = tests.filter(testplantestcaselink__testplan_id=testplan_id)

    if 'search' in request.GET and request.GET['search'] == "true":
        if request.GET.get('nameordesc'):
            searchstring = request.GET['nameordesc'].replace("+", " ")
            tests = tests.filter(Q(name__icontains=searchstring)
                                 | Q(description__icontains=searchstring))
        if request.GET.get('asid'):
            tests = tests.filter(id=request.GET['asid'].replace("+", " "))
        if request.GET.get('asname'):
            searchstring = request.GET['asname'].replace("+", " ")
            tests = tests.filter(name__icontains=searchstring)
        if request.GET.get('bugid'):
            tests = tests.filter(bug_id__icontains=request.GET['bugid'])
        if request.GET.get('addedversion'):
            tests = tests.filter(added_version__icontains=request.GET['addedversion'])
        if request.GET.get('astype'):
            astype = []
            for type in request.GET['astype'].split(','):
                astype.append(type.replace("+", " "))
            tests = tests.filter(case_type__in=astype)
        if request.GET.get('asdescription'):
            searchstring = request.GET['asdescription'].replace("+", " ")
            tests = tests.filter(description__icontains=searchstring)
        if request.GET.get('aspriority'):
            tests = tests.filter(priority=request.GET['aspriority'])
        if request.GET.get('asauthor'):
            tests = tests.filter(Q(author__username__icontains=request.GET['asauthor'])
                                 | Q(author__first_name__icontains=request.GET['asauthor'])
                                 | Q(author__last_name__icontains=request.GET['asauthor']))
        if request.GET.get('asdefaultassignee'):
            tests = tests.filter(Q(default_assignee__username__icontains=request.GET['asdefaultassignee']))
        if request.GET.get('asfeature'):
            tests = tests.filter(feature__icontains=request.GET['asfeature'])
        if request.GET.get('asfolder'):
            tests = tests.filter(folder__id=request.GET['asfolder'])
        if request.GET.get('asauto') == "auto":
            tests = tests.filter(is_automated=True)
        if request.GET.get('asauto') == "noauto":
            tests = tests.filter(is_automated=False)
        if request.GET.get('asproduct'):
            product = request.GET['asproduct'].replace("+", " ")
            root_folder = Folder.objects.get(name='root')
            folder_id = Folder.objects.get(name=product, parent=root_folder).id
            tests = tests.filter(folder_id__in=folder_and_child_folders_list(folder_id))
        if request.GET.get('asstatus'):
            asstatus = request.GET['asstatus'].split(',')
            tests_with_results = tests.filter(
                testplantestcaselink__testplan_id=testplan_id,
                testplantestcaselink__result__latest=True)
            if "any" in asstatus:
                tests = tests_with_results
            elif "notrun" in asstatus:
                tests = tests.exclude(id__in=tests_with_results.values('id'))
            else:
                tests = tests_with_results.filter(
                    testplantestcaselink__result__status__in=asstatus,
                    testplantestcaselink__testplan_id=testplan_id,
                    testplantestcaselink__result__latest=True)

    else:
        if '-100' == request.GET.get('key', '-100'):
            tests = tests.filter(folder__name="root")
        else:
            tests = tests.filter(folder_id=request.GET.get('key'))

    total_count = tests.count()

    # pagination begins
    elems = int(request.GET.get("elems", request.COOKIES.get("elems", settings.ELEMENTS_PER_PAGE)))
    paginator = Paginator(tests, elems)

    try:
        curr_page = int(request.GET.get('page', '1'))
    except ValueError:
        curr_page = 1
    try:
        tests = paginator.page(curr_page)
    except (InvalidPage, EmptyPage):
        curr_page = 1
        tests = paginator.page(paginator.num_pages)
    resp_dict = {}
    resp_dict['start_index'] = paginator.page(curr_page).start_index()
    resp_dict['end_index'] = paginator.page(curr_page).end_index()
    resp_dict['has_next'] = paginator.page(curr_page).has_next()
    resp_dict['has_prev'] = paginator.page(curr_page).has_previous()
    resp_dict['curr_page'] = curr_page
    resp_dict['total_count'] = total_count

    if testplan_id:
        resp_dict['status'] = dict(((test.id, get_status(testplan_id, test.id)) for test in tests))

    # pagination ends

    testjson = serializers.serialize('json', tests, use_natural_keys=True)
    resp_dict["tests"] = testjson

    response = HttpResponse(json.dumps(resp_dict))

    if request.GET.get("elems"):
        response.set_cookie('elems', request.GET.get("elems"))
    return response


def ajax_addfolder(request):
    name = request.GET['name']
    parent_id = request.GET['parent']
    if parent_id == "-9":
        parent = Folder.objects.get(name="root")
    else:
        parent = Folder.objects.get(id=parent_id)

    resp = {}
    folder = Folder(name=name, parent=parent)
    try:
        folder.save()
        new_child = [{"title": folder.name, "isFolder": True, "key": folder.id}]
        resp["child"] = new_child
        resp["message"] = "Folder " + folder.name + " added"
        resp["added"] = True
    except IntegrityError:
        resp["added"] = False
        resp["message"] = "Folder name " + folder.name + " is already in use, please try a different name."

    return HttpResponse(json.dumps(resp))


def ajax_addresults(request, testplan_id):
    results = json.loads(request.POST.get('data'))
    status = request.POST.get('type').split('btn')[0]
    for row in results:
        testplan_testcase_link = TestplanTestcaseLink.objects.get(testcase__id=row[0],
                                                                  testplan__id=testplan_id)
        result = Result(testplan_testcase_link=testplan_testcase_link,
                        status=status,
                        tester=request.user,
                        bug_ticket=row[1],
                        note=row[2])
        result.save()
    return HttpResponse(json.dumps({"alertType": "alert-success",
                                    "alertflag": True,
                                    "message": "%d testcases have been marked as %s"
                                               % (len(results), status)
    }))


def ajax_deletefolder(request):
    folder = Folder.objects.get(pk=request.GET['key'])
    count_of_tests_in_folder = TestCase.objects.filter(folder=folder).count()
    has_subfolder = Folder.objects.filter(parent_id=folder.id).count()

    resp = {}
    if count_of_tests_in_folder > 0:
        resp["deleted"] = False
        resp["message"] = "Folder " + str(folder.name) + " has " + str(
            count_of_tests_in_folder) + " test cases. Move these test cases before deleting the folder."
    elif has_subfolder > 0:
        resp["deleted"] = False
        resp["message"] = "Folder " + str(
            folder.name) + " has a child folder. Delete this the child folder before deleting the folder."
    else:
        resp["deleted"] = True
        resp["message"] = "Folder " + str(folder.name) + " permanently deleted"
        folder.delete()

    return HttpResponse(json.dumps(resp))


def ajax_renamefolder(request):
    folder = Folder.objects.get(pk=request.GET['key'])
    renamed_folder_name = request.GET['name']

    resp = {}
    try:
        if renamed_folder_name:
            resp["renamed"] = True
            resp["message"] = "Folder " + folder.name + " has been successfully renamed to " + renamed_folder_name
            folder.name = renamed_folder_name
            folder.save()
        else:
            resp["renamed"] = False
            resp["message"] = "Folder name cannot be empty"

    except IntegrityError:
        resp["renamed"] = False
        resp["message"] = "Folder name " + folder.name + " is already in use, please try a different name."

    return HttpResponse(json.dumps(resp))


def help(request):
    """ view for the help page"""
    return render_to_response('help.html',
                              context_instance=RequestContext(request))


@csrf_exempt
def ajax_testcasebulk(request):
    if request.POST:
        tc_id_list = request.POST['tc-ids'].split(",")
        for tc_id in tc_id_list:
            testcase = TestCase.objects.get(id=int(tc_id))
            if request.POST['added_version']:
                testcase.added_version = request.POST['added_version']
            if request.POST['product']:
                testcase.product = request.POST['product']
            if request.POST['priority']:
                testcase.priority = request.POST['priority']
            if request.POST['case_type']:
                testcase.case_type = request.POST['case_type']
            if request.POST['folder']:
                testcase.folder = Folder.objects.get(id=request.POST['folder'])
            if request.POST['default_assignee']:
                testcase.default_assignee = User.objects.get(id=request.POST['default_assignee'])
            if 'enabled' in request.POST:
                testcase.enabled = True
            else:
                testcase.enabled = False
            if 'is_automated' in request.POST:
                testcase.is_automated = True
            else:
                testcase.is_automated = False
            testcase.save()

    return HttpResponse()


def ajax_bugstatus(request, bug_id):
    resp = {}
    try:
        jira = JIRA(options={'server': settings.BUG_SERVER}, basic_auth=(settings.BUG_USER, settings.BUG_PASSWORD))
        issue = jira.issue(bug_id)
        resp["status"] = issue.fields.status.name
        resp["assignee"] = issue.fields.assignee.displayName
        resp["reporter"] = issue.fields.reporter.displayName
        resp["summary"] = issue.fields.summary
        resp["priority"] = issue.fields.priority.name
        resp["url"] = settings.BUG_TRACKING_URL

    except JIRAError as e:
        resp["error"] = e.text
    except ConnectionError:
        resp["error"] = "Failed to Connect to Bug Server."

    return HttpResponse(json.dumps(resp))


def ajax_createbug(request):
    resp = {}
    try:
        jira = JIRA(options={'server': settings.BUG_SERVER}, basic_auth=(settings.BUG_USER, settings.BUG_PASSWORD))
        new_bug = jira.create_issue(project={'key': request.POST.get("project")},
                                    summary=request.POST.get("summary"),
                                    description=request.POST.get("description"),
                                    issuetype={'name': 'Bug'},
                                    reporter={'name': request.POST.get("reporter")},
                                    priority={'name': request.POST.get("priority")})
        resp["bug_id"] = new_bug.key

    except JIRAError as e:
        resp["error"] = e.text.values()[0]

    except ConnectionError:
        resp["error"] = "Failed to Connect to Bug Server."


    return  HttpResponse(json.dumps(resp))




def metrics_dashboard(request):
    #todo: use some of that awesome ORM stuff
    cursor = connection.cursor()
    cursor.execute(
        "select count(*) as cnt, DATE_FORMAT(timestamp, \'%%Y-%%m-%%d\') as date_run from ecapp_result group by date_run")
    total_results = []
    for r in cursor.fetchall():
        total_results.append([str(r[1]), int(r[0])])

    res_count = Result.objects.count()
    top_testers = Result.objects.values('tester').annotate(cnt=Count('testplan_testcase_link')).order_by('-cnt')[:20]
    top_teams = Result.objects.exclude(testplan_testcase_link__testcase__product=None).exclude(
        testplan_testcase_link__testcase__product="").values('testplan_testcase_link__testcase__product').annotate(
        cnt=Count('testplan_testcase_link')).order_by('-cnt')[:20]


    #cursor.execute("select count(*) as cnt, tc.id, tc.name, tc.is_automated from ecapp_result r, ecapp_testplantestcaselink tptc, ecapp_testcase tc where (r.testplan_testcase_link_id = tptc.id) and (tptc.testcase_id = tc.id) group by tc.id order by cnt desc limit 25")
    top_25_tests = Result.objects.values('testplan_testcase_link__testcase__id',
                                         'testplan_testcase_link__testcase__name',
                                         'testplan_testcase_link__testcase__is_automated').annotate(
        cnt=Count('testplan_testcase_link__testcase')).order_by('-cnt')[:25]

    #for t in cursor.fetchall():
    #	top_25_tests.append(t)

    top_25_manual_tests = Result.objects.filter(testplan_testcase_link__testcase__is_automated=False).values(
        'testplan_testcase_link__testcase__id', 'testplan_testcase_link__testcase__name').annotate(
        cnt=Count('testplan_testcase_link__testcase')).order_by('-cnt')[:25]

    cursor.execute(
        "select count(*), tc.is_automated from ecapp_result r, ecapp_testplantestcaselink tptc, ecapp_testcase tc where (r.testplan_testcase_link_id = tptc.id) and (tc.id = tptc.testcase_id) group by is_automated")

    return render_to_response('metrics_dashboard.html',
                              {'total_results': total_results, 'top_testers': top_testers, 'top_teams': top_teams,
                               'top_25_tests': top_25_tests, 'top_25_manual_tests': top_25_manual_tests,
                              }, context_instance=RequestContext(request))
