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
import json
import datetime
import pytz
import logging

from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Max, Min
from django.db.models import Count
from django.contrib import messages
from django.conf import settings

from ecapp.models import TestCase, Folder, Result, DesignStep, UploadedFile, User
from ecapp.forms import TestCaseForm, TestCaseBulkForm


logger = logging.getLogger(__name__)


def generate_product_lookup():
    return Folder.objects.filter(parent__name="root").exclude(name="deletedfolders").order_by("name")

def generate_folder_path(folder_id):
    try:
        folder = Folder.objects.get(id=folder_id)
    except Folder.DoesNotExist:
        logger.critical("DB is not configured.")
        raise

    if folder.name == "root":
        folder_path = "/"
    else:
        parent = folder.parent
        folder_path = str(folder)
        while(True):
            if parent.name == "root":
                break
            folder_path = str(parent) + "/" + folder_path
            parent = parent.parent

        folder_path = "/" + folder_path

    return folder_path

def test_case_summary_view(request):
    """ A view for listing the root cases in the database"""
    if TestCase.objects.count() == 0:
        welcome = True
    else:
        welcome = False

    root = Folder.objects.get(name="root")
    #GET ONLY ENABLED CASES. DISABLED CASES CAN BE REQUESTED THROUGH AJAX REQUEST
    tests = TestCase.objects.filter(enabled=True).order_by('id')
    if 'showsubtree' not in request.GET:
        tests = tests.filter(folder=root)

    bulk_form = TestCaseBulkForm()
    return render_to_response('test_case_summary.html',
                              {'tests': tests,
                               'bulk_form': bulk_form,
                               'welcome': welcome,
                               'teams': json.dumps(Folder.get_root_folder().child_nodes())
                               },
                              context_instance=RequestContext(request))

def _add_steps(testcase, request):
    req_steps = request.POST['designsteplist']
    if req_steps:
        step_ids = [int(item) for item in (req_steps.split(","))]
        design_steps = DesignStep.objects.filter(id__in=step_ids)
        for design_step in design_steps:
            testcase.design_steps.add(design_step)

def _add_uploads(testcase, request):
    req_uploads = request.POST['uploadlist']
    if req_uploads:
        upload_ids = [int(item) for item in (req_uploads.split(","))]
        uploads = UploadedFile.objects.filter(id__in=upload_ids)
        for upload in uploads:
            testcase.uploads.add(upload)

def _set_tc_id(tc_id):
    if tc_id != -1:
        return tc_id
    else:
        return None


@login_required
def test_case_edit(request, test_case_id=-1):
    updated_by = request.user.username
    if test_case_id == -1:
        testcase = None
        author = updated_by
    else:
        testcase = TestCase.objects.get(pk=test_case_id)
        author = testcase.author

    message = None

    if request.method == 'POST':
        form = TestCaseForm(request.POST, instance=testcase)

        if form.is_valid():

            tc = form.save()
            _add_steps(tc, request)
            _add_uploads(tc, request)
            testcase = tc
            testcase.folder_path = generate_folder_path(request.POST['folder'])
            testcase.updated_datetime = datetime.datetime.now(pytz.timezone('US/Pacific'))
            testcase.updated_by = User.objects.get(username=updated_by)
            testcase.save()
            if test_case_id == -1:
                message = "Created the testcase %s successfully" % tc.name
                author = updated_by
            else:
                message = "Edited the testcase %s successfully" % tc.name
                author = testcase.author
            messages.add_message(request, messages.SUCCESS, message)
            test_case_id = tc.id
            return HttpResponseRedirect(reverse('case_view', args=(tc.id,)))
        else:
            messages.add_message(request, messages.ERROR, "There was a problem submitting the form. Please check the values and try again.")
            return render_to_response('test_case_form.html',
                                      {'form': form,
                                       'type': 'View/Edit Test Case',
                                       'author': author,
                                       'updated_by': updated_by,
                                       'test_case': testcase,
                                       'product_lookup': generate_product_lookup(),
                                       'id': _set_tc_id(test_case_id)
                                       },
                                      context_instance=RequestContext(request))
    else:
        if test_case_id == -1:
            folder_id = request.GET['folder_id']
            author = request.user
        else:
            folder_id = testcase.folder_id

        if folder_id == "-100":
            folder = Folder.objects.get(name="root")
            folder_path = "/" + folder.name
        else:
            folder = Folder.objects.get(id=folder_id)
            folder_path = generate_folder_path(folder_id)
        initial_value = {'author': author, 'folder': folder, 'folder_path': folder_path}
        form = TestCaseForm(instance=testcase, initial=initial_value)

    return render_to_response('test_case_form.html',
                              {'form': form,
                               'type': 'View/Edit Test Case',
                               'author': author,
                               'updated_by': updated_by,
                               'test_case': testcase,
                               'product_lookup': generate_product_lookup(),
                               'foldername': folder,
                               'folder_path': folder_path,
                               'folderid': folder_id,
                               'id': _set_tc_id(test_case_id)
                               },
                              context_instance=RequestContext(request))


@login_required
def test_case_clone(request, test_case_id):
    """ Clones an existing test case """

    testcase = TestCase.objects.get(id=test_case_id)
    author = request.user.username
    prior_id = None
    design_steps = None

    if request.method == 'POST':
        form = TestCaseForm(request.POST)
        if form.is_valid():
            tc = form.save()
            tc.folder_path = generate_folder_path(request.POST['folder'])
            tc.save()
            steps = request.POST['designsteplist']
            if steps:
                steps_id = [int(item) for item in (steps.split(","))]
                design_steps = DesignStep.objects.filter(id__in=steps_id)
                for design_step in design_steps:
                    tc.design_steps.add(design_step)
                tc.save()
            return HttpResponseRedirect(reverse('case_view', args=(tc.id,)))

    else:
        design_steps = testcase.design_steps.all()
        design_steps_dict = list(design_steps.values())  # creating a dict since a queryset is immutable
        for index in range(0, len(design_steps)):
            clone_step = design_steps[index]
            clone_step.pk = None
            clone_step.save()
            design_steps_dict[index]["id"] = clone_step.pk
        design_steps = json.dumps(design_steps_dict)

        testcase.description = testcase.description + "\n\n\nCLONED FROM\n=============\ntestcase id: " + str(testcase.id) + "\ntestcase name: " + testcase.name
        folderid = testcase.folder_id
        folder_path = testcase.folder_path
        testcase.name = "CLONE OF " + testcase.name
        testcase.author = User.objects.get(username=author)
        prior_id = testcase.id
        testcase.id = None
        form = TestCaseForm(instance=testcase)

    return render_to_response('test_case_form.html', {'form': form,
                                                      'type': 'View/Edit Test Case',
                                                      'author': author,
                                                      'gridData': design_steps,
                                                      'test_case': testcase,
                                                      'product_lookup': generate_product_lookup(),
                                                      'id': None,
                                                      'prior_id': prior_id,
                                                      'folderid': folderid,
                                                      'folder_path': folder_path,
                                                      'clone': True,
                                                      },
                                                      context_instance=RequestContext(request))


def test_case_plot(request, test_case_id):
    testcase = TestCase.objects.get(id=test_case_id)

    #Graphs the results under a test case
    #START PASS/FAIL PLOT GENERATION#
    all_results = Result.objects.filter(testplan_testcase_link__testcase=testcase).order_by('timestamp').reverse()

    if all_results:
        pass_query = all_results.filter(testplan_testcase_link__testcase=testcase, status='passed')
        fail_query = all_results.filter(testplan_testcase_link__testcase=testcase, status='failed')
        mindate = str(int(all_results.aggregate(Min('timestamp')).get('timestamp__min').strftime("%s"))*1000)
        maxdate = str(int(all_results.aggregate(Max('timestamp')).get('timestamp__max').strftime("%s"))*1000)
        pass_list, fail_list = [], []

        #passed and failed counts with the corresponding dates
        for item in pass_query.extra({'rundate': "date(timestamp)"}).values('rundate').annotate(count=Count('testplan_testcase_link__testcase')).order_by('rundate'):
            pass_list.append([str(item['rundate']), item['count']])

        for item in fail_query.extra({'rundate': "date(timestamp)"}).values('rundate').annotate(count=Count('testplan_testcase_link__testcase')).order_by('rundate'):
            fail_list.append([str(item['rundate']), item['count']])

        #END PASS/FAIL#
        return render_to_response('test_case_plot.html', {
            'mindate': mindate,
            'maxdate': maxdate,
            'testcase': testcase,
            'all_results': all_results,
            'pass_list': pass_list,
            'fail_list': fail_list,
            'bug_url': settings.BUG_TRACKING_URL,
             }, context_instance=RequestContext(request))

    else:
        return render_to_response('test_case_plot.html', {
            'all_results': all_results,
            'testcase': testcase,
            }, context_instance=RequestContext(request))

def test_case_view(request, test_case_id):
    testcase = TestCase.objects.get(id=test_case_id)
    design_steps = testcase.design_steps.all()
    uploads = testcase.uploads.all()

    return render_to_response('test_case_view.html', {
            'test_case': testcase,
            'design_steps': design_steps,
            'uploads': uploads,
            'MEDIA_URL': settings.MEDIA_URL,
            'id': _set_tc_id(test_case_id)
            },context_instance=RequestContext(request))

def test_case_modal(request, test_case_id):
    testcase = TestCase.objects.get(id=test_case_id)
    design_steps = testcase.design_steps.all()

    return render_to_response('test_case_modal.html', {
            'test_case': testcase,
            'design_steps': design_steps,
            'id': _set_tc_id(test_case_id)
            }, context_instance=RequestContext(request))
