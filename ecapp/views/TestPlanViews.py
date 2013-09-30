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
from datetime import datetime, timedelta
import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.paginator import Paginator, InvalidPage, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.db import connection
from django.db.models import Count, Q
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from ecapp.models import Result, TestPlan, TestplanTestcaseLink, Folder, TestCase
from ecapp.forms import TestPlanForm


def getBarData(testplan):
    """get bar graph data for a test plan"""
    report_data = []

    #sql fun

    #this gets all the results by folder by status
    testcases = TestplanTestcaseLink.objects.raw("select tptc.id, count(r.status) as cnt, r.status, tc.folder_id, f.name as folder_name, f.parent_id from ecapp_testplantestcaselink tptc left outer join ecapp_result as r on tptc.id = r.testplan_testcase_link_id join ecapp_testcase as tc on tc.id = tptc.testcase_id join ecapp_folder as f on tc.folder_id = f.id where tptc.testplan_id = %s and (r.latest=1 or r.latest is null) group by folder_id, status" % testplan.id)

    #this gets all the test cases in the plan by folder
    alltestcases = TestplanTestcaseLink.objects.raw("select tptc.id, count(tptc.id) as cnt, tc.folder_id from ecapp_testplantestcaselink as tptc join ecapp_testcase as tc on tptc.testcase_id = tc.id where tptc.testplan_id = %s group by tc.folder_id" % testplan.id)

    #this gets the count of the ones that haven't run by folder
    notrun = TestplanTestcaseLink.objects.raw("select tptc.id, count(tptc.id) as cnt, tptc.testcase_id, r.status, tc.folder_id from ecapp_testplantestcaselink as tptc left outer join ecapp_result as r on tptc.id = r.testplan_testcase_link_id join ecapp_testcase as tc on tptc.testcase_id = tc.id where r.testplan_testcase_link_id is null and tptc.testplan_id = %s group by folder_id;" % testplan.id)

    folder_data = {}

    #here we build the main part of the dictionary
    for t in testcases:
        if t.folder_id not in folder_data:
            folder_data[t.folder_id] = {}
            folder_data[t.folder_id]["team"] = t.folder_name
            folder_data[t.folder_id]["teamoption"] = t.folder_name.replace(" ", "+")
            folder_data[t.folder_id]["id"] = t.folder_id
            folder_data[t.folder_id]["parent_id"] = t.parent_id

            #this is an excursion off in to folder parent land. Not done yet.
            parent = Folder.objects.get(id=t.parent_id)
            while parent.name != "root":
                if parent.id not in folder_data:
                    folder_data[parent.id] = {}
                    folder_data[parent.id]["id"] = parent.id
                    folder_data[parent.id]["parent_id"] = parent.parent_id
                    folder_data[parent.id]["team"] = parent.name
                parent = Folder.objects.get(id=parent.parent.id)

        folder_data[t.folder_id][t.status] = t.cnt 
        folder_data[t.folder_id]["notrun"] = 0

    #pop on the not-runs
    for nr in notrun:
        folder_data[nr.folder_id]["notrun"] = nr.cnt

    #pop on the total, and do the aggregate calculations
    for at in alltestcases:
        folder_data[at.folder_id]["total"] = at.cnt
        if "passed" not in folder_data[at.folder_id]:
            folder_data[at.folder_id]["passed"] = 0
        folder_data[at.folder_id]["actual"] = folder_data[at.folder_id]["passed"]/float(folder_data[at.folder_id]["total"] or 1)*100.0
        folder_data[at.folder_id]["progress"] = (folder_data[at.folder_id]["total"] - folder_data[at.folder_id]["notrun"])/float(folder_data[at.folder_id]["total"] or 1)*100

    #this is for backward compatibility with the template code. will go away eventually.
    for f in folder_data:
        print folder_data[f]
        report_data.append(folder_data[f])

###old code####


    for folder in Folder.objects.filter(parent=Folder.objects.get(name="root")):
        folder_data = {}
        annotated_status = {}
        all_latest_results = Result.objects.filter(latest=True, testplan_testcase_link__testplan=testplan, testplan_testcase_link__testcase__enabled=1, testplan_testcase_link__testcase__in=folder.in_testplan(testplan.id))
        all_tptc_links = TestplanTestcaseLink.objects.filter(testplan=testplan, testcase__enabled=1, testcase__in=folder.in_testplan(testplan.id))

        if all_latest_results.exists():
            annotated_status = dict(all_latest_results.values_list('status').annotate(Count('id')))
            folder_data["notrun"] = all_tptc_links.exclude(pk__in=all_latest_results.values('testplan_testcase_link')).count()
        else:
            folder_data["notrun"] = all_tptc_links.count()

        for item in dict(Result.STATUS_CHOICES).keys():
            folder_data[item] = annotated_status.get(item, 0)

        folder_data["total"] = sum(folder_data.values())
        folder_data["actual"] = folder_data["passed"]/float(folder_data["total"] or 1)*100.0
        folder_data["progress"] = (folder_data["total"] - folder_data["notrun"])/float(folder_data["total"] or 1)*100

        if folder_data["total"] > 0:
            folder_data["team"] = folder.name
            folder_data["teamoption"] = folder.name.replace(" ", "+")
            #report_data.append(folder_data)

    return report_data


def test_plan_summary_view(request):
    """ Called when viewing active test plans """
    plans = TestPlan.objects.filter(enabled=True).filter(end_date__gte=datetime.now()).order_by('start_date')
    return _generate_test_views(request, plans)


def test_plan_archive_view(request):
    """ Called when viewing expired test plans """
    plans = TestPlan.objects.filter(enabled=True).order_by('start_date')
    return _generate_test_views(request, plans)


def _generate_test_views(request, plans):
    total_count = plans.count()
    all_plans_count = TestPlan.objects.count()
    all_tests_count = TestCase.objects.count()
    
    if (all_plans_count > 0) or (all_tests_count > 0):
        welcome = False
    else:
        welcome = True
    
    page = request.GET.get('page')
    if 'archive' in request.path:
        archive = True
    else:
        archive = False
    if request.GET.get('search') == 'true':
        display = "inline;"
        search = True
        if request.GET.get('asname'):
            plans = plans.filter(name__icontains=request.GET['asname'].replace("+", " "))
        if request.GET.get('asid'):
            plans = plans.filter(id=request.GET.get('asid'))
        if request.GET.get('asrelease'):
            plans = plans.filter(release__icontains=request.GET['asrelease'].replace("+", " "))
        if request.GET.get('asleader'):
            plans = plans.filter(leader__icontains=request.GET['asleader'].replace("+", " "))
    else:
        display = "none;"
        search = False
    try:
        elems = int(request.GET.get("elems", request.COOKIES.get("elems", settings.ELEMENTS_PER_PAGE)))

        paginator = Paginator(plans, elems)
        plans = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        plans = paginator.page(1)
    except (InvalidPage, EmptyPage):
        plans = paginator.page(paginator.num_pages)


    response = render_to_response('test_plan_summary.html',
                                 {'plans': plans, 'total_count': total_count, 'all_plans_count': all_plans_count,
                                 'welcome': welcome,
                                 'archive':archive,
                                 'search':search,
                                 'display':display,
                                 }, context_instance=RequestContext(request))

    if request.GET.get("elems"):
        response.set_cookie('elems', request.GET.get("elems"))

    return response


#Adds results into the db
@login_required
def test_plan_add_results(request, test_plan_id):
    """ Called when results are added to a test plan """

    testplan = TestPlan.objects.get(id=test_plan_id)
    tests = testplan.testcases.filter(enabled=True)
    return render_to_response('test_plan_add_results.html', {
        'plan': testplan,
        'tests': tests,
        'results': Result.objects.filter(testplan_testcase_link__testplan=testplan),
        'teams': json.dumps(Folder.get_root_folder().child_nodes(test_plan_id)),
        'bug_url': settings.BUG_TRACKING_URL
        }, context_instance=RequestContext(request))


@login_required
def edit_test_plan_view(request, test_plan_id):
    """ Edits an existing test plan's details """
    if request.method == 'GET':
        plan = TestPlan.objects.get(id=test_plan_id)
        form = TestPlanForm(instance=plan)
        author = plan.creator.username
        currentEdit = []

        return render_to_response(
            'test_plan_form.html', {
            'form': form,
            'type': 'View/Edit Test Plan',
            'plan': plan,
            'author': author,
            'currentEdit': currentEdit,
            }, context_instance=RequestContext(request))
    else:
        plan = TestPlan.objects.get(id=test_plan_id)
        form = TestPlanForm(request.POST, instance=plan)
        testplan = form.save()
        message = "Edited the plan successfully"
        messages.add_message(request, messages.SUCCESS, message)
        return render_to_response(
            'test_plan_add_testcases.html',
            {"testplan": testplan
               }, context_instance=RequestContext(request))


@login_required
def create_test_plan_view(request):
    """Creates a new test plan"""
    author = request.user.username
    if request.method == 'POST':  # If the form has been submitted...
        form = TestPlanForm(request.POST)
        if form.is_valid():
            testplan = form.save()
            message = "Created the plan successfully"
            messages.add_message(request, messages.SUCCESS, message)
            return HttpResponseRedirect(reverse('plan_add_tests', args=(testplan.id,)))
    else:
        form = TestPlanForm(initial={'creator': request.user})

    return render_to_response(
        'test_plan_form.html',
        {'form': form,
         'type': 'Create Test Plan',
         'author': author,
         }, context_instance=RequestContext(request))


@login_required
def clone_test_plan_view(request, test_plan_id):

    if request.method == 'GET':
        plan = TestPlan.objects.get(id=test_plan_id)
        previous_name = plan.name
        previous_id = plan.id
        plan.name = "CLONE OF " + plan.name
        plan.id = None
        author = request.user.username
        plan.creator = request.user
        form = TestPlanForm(instance=plan)

        return render_to_response(
            'test_plan_form.html', {
            'form': form,
            'type': 'Clone Test Plan',
            'plan': plan,
            'name': plan.name,
            'previous_id': previous_id,
            'previous_name': previous_name,
            'author': author,
            'clone': True
            }, context_instance=RequestContext(request))
    else:

        form = TestPlanForm(request.POST)
        prevous_testplan = TestPlan.objects.get(id=request.POST['previous_plan_id'])

        testplan = form.save()
        message = "Edited the plan successfully"

        tests = prevous_testplan.testcases.all()

        for test in tests:
            testplan_testcase_link = TestplanTestcaseLink(testplan=testplan, testcase=test)
            testplan_testcase_link.save()

        message = message + " and added " + str(tests.count()) + " tests"
        messages.add_message(request, messages.SUCCESS, message)
        return render_to_response(
            'test_plan_add_testcases.html',
            {"testplan": testplan
             }, context_instance=RequestContext(request))


@login_required
def add_testcases_view(request, test_plan_id):
    """Adds testcases to a testplan"""
    testplan = TestPlan.objects.get(id=test_plan_id)
    return render_to_response(
        'test_plan_add_testcases.html',
        {"testplan": testplan,
        'teams': json.dumps(Folder.get_root_folder().child_nodes()),
        }, context_instance=RequestContext(request))


@login_required
def review_testcases_view(request, test_plan_id):
    """Review and remove testcases in a testplan"""
    testplan = TestPlan.objects.get(id=test_plan_id)
    return render_to_response(
        'test_plan_review_testcases.html',
        {"testplan": testplan,
        'teams': json.dumps(Folder.get_root_folder().child_nodes(test_plan_id)),
        }, context_instance=RequestContext(request))


def test_plan_plot(request, test_plan_id):
    """Graphs the results under a test plan"""
    testplan = TestPlan.objects.get(id=test_plan_id)

    all_query = Result.objects.filter(testplan_testcase_link__testplan=testplan, latest=True, testplan_testcase_link__testcase__enabled=1)
    pass_query = all_query.filter(status='passed')
    fail_query = all_query.filter(status='failed')

    pass_list, fail_list, agg_pass_list, agg_fail_list = [], [], [], []

    #passed and failed counts with the corresponding dates
    for item in pass_query.extra({'rundate': "date(timestamp)"}).values('rundate').annotate(count=Count('testplan_testcase_link__testcase')).order_by('rundate'):
        pass_list.append([str(item['rundate']), item['count']])

    for item in fail_query.extra({'rundate': "date(timestamp)"}).values('rundate').annotate(count=Count('testplan_testcase_link__testcase')).order_by('rundate'):
        fail_list.append([str(item['rundate']), item['count']])

    # Fetch all the test run dates
    rundate_list = all_query.extra({'rundate': "date(timestamp)"}).values_list('rundate', flat=True).order_by('-timestamp')

    #Gives the total tests which passed till a rundate
    for rundate in set(rundate_list):
        #Count all tests which have smaller timestamps than that of the next day to account for tests which ran on the same day
        nextday = rundate + timedelta(1)
        agg_pass_list.append([str(rundate), pass_query.filter(timestamp__lt=nextday).count()])
        agg_fail_list.append([str(rundate), fail_query.filter(timestamp__lt=nextday).count()])

    report_data = getBarData(testplan)

    # TO FIX FIREFOX bug where string formatted times are not accepted
    mindate = str(int(testplan.start_date.strftime("%s"))*1000)

    maxdate = testplan.end_date or (testplan.start_date + timedelta(days=90))
    maxdate = str(int(maxdate.strftime("%s"))*1000)

    max_results_count = 0
    try:
        max_results_count = max([item[1] for item in agg_fail_list + agg_pass_list + fail_list + pass_list])
    except ValueError:
        max_results_count = 0

    return render_to_response('test_plan_plot.html', {'pass_list': pass_list,
                                           'agg_pass_list': agg_pass_list,
                                           'mindate': mindate,
                                           'maxdate': maxdate,
                                           'fail_list': fail_list,
                                           'agg_fail_list': agg_fail_list,
                                           'testplan': testplan,
                                           'report_data': report_data,
                                           'max_results_count': max_results_count
                                           }, context_instance=RequestContext(request))


def analyze(request, test_plan_id):
    """Graphs the results under a test plan"""

    testplan = TestPlan.objects.get(id=test_plan_id)
    testplan_testcase_link = TestplanTestcaseLink.objects.filter(testplan=testplan)
    automated_tests = testplan_testcase_link.filter(testcase__is_automated=True)
    number_of_all_tests = testplan_testcase_link.count() 
    number_of_automated_tests = automated_tests.count()
    number_of_non_automated_tests = number_of_all_tests - number_of_automated_tests
    if number_of_all_tests == 0:
        percent_of_automated_tests = 0
        percent_of_non_automated_tests =0
    else:
        percent_of_automated_tests = (float(number_of_automated_tests) / number_of_all_tests) * 100
        percent_of_non_automated_tests = (float(number_of_non_automated_tests) / number_of_all_tests) * 100
    percent_of_automated_tests = round(percent_of_automated_tests, 2)
    percent_of_non_automated_tests = round(percent_of_non_automated_tests, 2)
    leftstr = request.GET.get('left', 'Priority')
    topstr = request.GET.get('top', 'Tester')

    if leftstr == topstr:
        leftstr = 'Priority'
        topstr = 'Tester'

    # convert input str's to DB values
    dbmap = {'Priority': 'tc.priority',
             'Product': 'tc.product',
             'Assignee': 'tc.default_assignee_id',
             'Folder': 'f.name',
             'Tester': 'r.tester'
             }
    left = dbmap.get(leftstr)
    top = dbmap.get(topstr)

    tablerows = []
    headers = [leftstr, ]

    query = """select %s as 'left',
                    %s as 'top',
                    sum(case when status is null or status <> 'passed' then 1 else 0 end) notpassed,
                    sum(case when status = 'passed' then 1 else 0 end) passed,
                    sum(case when status is null or status is not null then 1 else 0 end) cases
               from ecapp_testcase tc join ecapp_testplantestcaselink tptc on tptc.testcase_id = tc.id and tptc.testplan_id = %s
                                   join ecapp_folder f on tc.folder_id = f.id
                                   left join ecapp_result r on r.testplan_testcase_link_id = tptc.id and r.latest = true group by %s, %s""" % (left, top, test_plan_id, left, top)

    # Data retrieval operation - no commit required
    cursor = connection.cursor()
    cursor.execute(query)

    # Unflatten data
    colvalues = set()
    rowvalues = set()
    rows = dict()
    row = None
    for datarow in cursor.fetchall():
        rowname = datarow[0]
        colname = datarow[1]
        passcount = datarow[3]
        casecount = datarow[4]

        if not rowname:
            rowname = "None"
        if not colname:
            colname = "None"
        if not len(rowname.strip()):
            rowname = "'" + rowname + "'"
        if not len(colname.strip()):
            colname = "'" + colname + "'"

        # see if we have a new row value
        if rowname not in rows:
            row = dict()
            rows[rowname] = row
            rowvalues.add(rowname)

        # see if we have a new column for this row
        acolumn = dict()
        row[colname] = acolumn
        colvalues.add(colname)
        acolumn['passcount'] = passcount
        acolumn['casecount'] = casecount

    # format table
    for rowvalue in sorted(rowvalues):
        tablerow = [{'name': rowvalue}, ]
        for colvalue in sorted(colvalues):
            cell = rows.get(rowvalue).get(colvalue)
            if cell:
                passed = cell.get('passcount')
                cases = cell.get('casecount')
                tablerow.append({'passed': passed, 'cases': cases, 'percent': 100*int(passed)/int(cases)})
            else:
                tablerow.append(None)
        tablerows.append(tablerow)

    headers.extend(sorted(colvalues))

    return render_to_response('test_plan_analyze.html', {
                                           'testplan': testplan,
                                           'all_tests': number_of_all_tests,
                                           'automated_tests': number_of_automated_tests,
                                           'percent_of_automated_tests': percent_of_automated_tests,
                                           'non_automated_tests': number_of_non_automated_tests,
                                           'percent_of_non_automated_tests': percent_of_non_automated_tests,
                                           'headers': headers,
                                           'data': tablerows,
                                           'topstr': topstr,
                                           'leftstr': leftstr,
                                           }
                              , context_instance=RequestContext(request))
