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
"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
import ecapp.models 
from datetime import date
from ecapp.forms import TestCaseForm, TestPlanForm
from django.test.client import RequestFactory

class TestCaseViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('test', 'test@test.com', 'test')
        self.logged_in = self.client.login(username='test', password='test')
        root_folder = ecapp.models.Folder.objects.get(name='root')
        sample_folder = ecapp.models.Folder.objects.create(name='testfolder', parent=root_folder)
        sample_sub_folder = ecapp.models.Folder.objects.create(name='subfolder', parent=sample_folder)
        sample_testcase = ecapp.models.TestCase.objects.create(name='testcase', author=self.user, folder=sample_folder)

    def test_test_case_summary_view(self):
        response = self.client.get('/test_case/')
        self.assertEqual(response.status_code, 200)

    def test_test_case_edit(self):
        self.assertEqual(self.logged_in, True)
        folder = ecapp.models.Folder.objects.get(name='testfolder')
        data = {'name':'test', 'description':'test', 'folder':folder}
        # creare a new test case
        response = self.client.post('/create_test_case/', data, follow=True)
        self.assertEqual(response.status_code, 200)
        # create a test case with an existing name in same folder
        data = {'name':'test', 'description':'test duplicated name', 'folder':folder}
        response = self.client.post('/create_test_case/', data, follow=True)
        self.assertEqual(response.status_code, 200)
        # editing an exsiting testcase
        test_case = ecapp.models.TestCase.objects.get(name='testcase')
        url = '/test_case/' + str(test_case.id) + '/edit/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
    def test_test_case_clone(self):
        self.assertEqual(self.logged_in, True)
        test_case = ecapp.models.TestCase.objects.get(name='testcase')
        url = '/clone_test_case/' + str(test_case.id)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 301)

    def test_test_case_plot(self):
        test_case = ecapp.models.TestCase.objects.get(name='testcase')
        url = '/test_case/' + str(test_case.id) + '/result/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_test_case_view(self):
        test_case = ecapp.models.TestCase.objects.get(name='testcase')
        url = '/test_case/' + str(test_case.id)
        response = self.client.get(url, follow=True)
        self.assertEqual(response.redirect_chain[0][1], 301)

    def test_test_case_modal(self):
        test_case = ecapp.models.TestCase.objects.get(name='testcase')
        url = '/test_case/' + str(test_case.id) + '/modal/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_generate_folder_path(self):
        # Testing for root
        root_folder_id = ecapp.models.Folder.objects.get(name="root").id
        self.assertEqual(ecapp.views.TestCaseViews.generate_folder_path(root_folder_id), "/")

        # Testing for "/testfolder"
        testfolder_folder_id = ecapp.models.Folder.objects.get(name="testfolder").id
        self.assertEqual(ecapp.views.TestCaseViews.generate_folder_path(testfolder_folder_id), "/testfolder")

        # Testing for "/testfolder/subfolder"
        subfolder_folder_id = ecapp.models.Folder.objects.get(name="subfolder").id
        self.assertEqual(ecapp.views.TestCaseViews.generate_folder_path(subfolder_folder_id), "/testfolder/subfolder")

class TestPlanViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('test', 'test@test.com', 'test')
        self.logged_in = self.client.login(username='test', password='test')
        sample_testcase = ecapp.models.TestCase.objects.create(name='testcase', author=self.user)
        sample_testplan = ecapp.models.TestPlan.objects.create(name='testplan', creator=self.user, start_date=date.today(), enabled=True)
        testplan_testcase_link = ecapp.models.TestplanTestcaseLink.objects.create(testcase=sample_testcase, testplan=sample_testplan)

    def test_test_plan_summary_view(self):
        response = self.client.get('/test_plan/')
        self.assertEqual(response.status_code, 200)

    def test_test_plan_archive_view(self):
        response = self.client.get('/test_plan/archive/')
        self.assertEqual(response.status_code, 200)

    def test_test_plan_add_results(self):
        self.assertEqual(self.logged_in, True)
        test_plan = ecapp.models.TestPlan.objects.get(name='testplan')
        url = '/test_plan/' + str(test_plan.id) + '/result/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_edit_test_plan_view(self):
        self.assertEqual(self.logged_in, True)
        test_plan = ecapp.models.TestPlan.objects.get(name='testplan')
        url = '/test_plan/' + str(test_plan.id) + '/edit/'
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_create_test_plan_view(self):
        self.assertEqual(self.logged_in, True)
        data = {'name':'create_testplan' , 'creator':self.user, 'start_date':date.today(), 'enabled':True}
        response = self.client.post('/create_test_plan/', data, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_clone_test_plan_view(self):
        self.assertEqual(self.logged_in, True)
        test_plan = ecapp.models.TestPlan.objects.get(name='testplan')
        url = '/clone_test_plan/' + str(test_plan.id)
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_add_testcase_view(self):
        self.assertEqual(self.logged_in, True)
        test_plan = ecapp.models.TestPlan.objects.get(name='testplan')
        url = '/test_plan/' + str(test_plan.id) + '/tests/add/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_review_testcases_view(self):
        self.assertEqual(self.logged_in, True)
        test_plan = ecapp.models.TestPlan.objects.get(name='testplan')
        url = '/test_plan/' + str(test_plan.id) + '/tests/review/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_test_plan_plot(self):
        test_plan = ecapp.models.TestPlan.objects.get(name='testplan')
        url = '/test_plan/' + str(test_plan.id) + '/plot'
        response = self.client.get(url, follow=True)
        self.assertEqual(response.redirect_chain[0][1], 301)

    def test_analyze(self):
        test_plan = ecapp.models.TestPlan.objects.get(name='testplan')
        url = '/test_plan/' + str(test_plan.id) + '/analyze/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

class RESTViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        sample_folder_in_root = ecapp.models.Folder.objects.create(name='folder_in_root', parent_id=1)
        sample_sub_folder = ecapp.models.Folder.objects.create(name='sub_folder', parent_id=sample_folder_in_root.id)
        sample_sub_sub_folder = ecapp.models.Folder.objects.create(name='sub_sub_folder', parent_id=sample_sub_folder.id)
        test_in_sub_folder = ecapp.models.Folder.objects.create(name='test', parent_id=sample_sub_folder.id)
        test_in_sub_sub_folder = ecapp.models.Folder.objects.create(name='test', parent_id=sample_sub_sub_folder.id)

    def test_restAPI(self): 
        response = self.client.get('/api/')
        self.assertEqual(response.status_code, 200)

    def test__folderpath_to_folderid(self):

        # Test the folder path 
        self.assertEqual(ecapp.views.RESTViews._folderpath_to_folderid("/folder_in_root"), 3)
        self.assertEqual(ecapp.views.RESTViews._folderpath_to_folderid("/folder_in_root/sub_folder"), 4)
        self.assertEqual(ecapp.views.RESTViews._folderpath_to_folderid("/folder_in_root/sub_folder/sub_sub_folder"), 5)

        # Test a folder path which is not starting from root
        self.assertEqual(ecapp.views.RESTViews._folderpath_to_folderid("/sub_folder"), 0)

        # Test folder path which is not exsists
        self.assertEqual(ecapp.views.RESTViews._folderpath_to_folderid("/wrong_folder"), 0)

        # Test folders with same name but diffrent places
        self.assertEqual(ecapp.views.RESTViews._folderpath_to_folderid("/folder_in_root/sub_folder/test"), 6)
        self.assertEqual(ecapp.views.RESTViews._folderpath_to_folderid("/folder_in_root/sub_folder/sub_sub_folder/test"), 7)

class OtherViewsTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_help(self):
        response = self.client.get('/help/')
        self.assertEqual(response.status_code, 200)
