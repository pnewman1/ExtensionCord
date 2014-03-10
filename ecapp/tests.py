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

from ecapp.views import RESTViews, OtherViews

import json

class TestCaseViewsTest(TestCase):
    fixtures = ['ecapp/fixtures/initial_data.json',]
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

class TestPlanViewsTest(TestCase):
    fixtures = ['ecapp/fixtures/initial_data.json',]
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
    fixtures = ['ecapp/fixtures/initial_data.json',]
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('test_user', 'test_testuser@test.com', 'test')
        self.logged_in = self.client.login(username='test_user', password='test')
        root_folder = ecapp.models.Folder.objects.get(name='root')
        sample_folder_in_root = ecapp.models.Folder.objects.create(name='folder_in_root', parent=root_folder)
        sample_sub_folder = ecapp.models.Folder.objects.create(name='sub_folder', parent=sample_folder_in_root)
        sample_sub_sub_folder = ecapp.models.Folder.objects.create(name='sub_sub_folder', parent=sample_sub_folder)
        test_in_sub_folder = ecapp.models.Folder.objects.create(name='test', parent=sample_sub_folder)
        test_in_sub_sub_folder = ecapp.models.Folder.objects.create(name='test', parent=sample_sub_sub_folder)
        sample_testcase = ecapp.models.TestCase.objects.create(name='sample_testcase', author=self.user, description="Sample Testcase", folder=sample_folder_in_root)
        sample_testplan = ecapp.models.TestPlan.objects.create(name='sample_testplan', creator=self.user, start_date=date.today())
        sample_testplan_testcase_link = ecapp.models.TestplanTestcaseLink.objects.create(testplan=sample_testplan, testcase=sample_testcase)
        sample_result = ecapp.models.Result.objects.create(testplan_testcase_link=sample_testplan_testcase_link)
        sample_testcase_not_in_testplan = ecapp.models.TestCase.objects.create(name='sample_testcase_not_in_testplan', author=self.user, description="Sample Testcase not in tespln", folder=sample_sub_folder)

    def test_restAPI(self): 
        response = self.client.get('/api/')
        self.assertEqual(response.status_code, 200)

    def test__folderpath_to_folderid(self):

        # Test the folder path 
        folder_in_root = ecapp.models.Folder.objects.get(name="folder_in_root")
        self.assertEqual(RESTViews._folderpath_to_folderid("/folder_in_root"), folder_in_root.id)
        sub_folder = ecapp.models.Folder.objects.get(name="sub_folder")
        self.assertEqual(RESTViews._folderpath_to_folderid("/folder_in_root/sub_folder"), sub_folder.id)
        sub_sub_folder = ecapp.models.Folder.objects.get(name="sub_sub_folder")
        self.assertEqual(RESTViews._folderpath_to_folderid("/folder_in_root/sub_folder/sub_sub_folder"), sub_sub_folder.id)

        # Test a folder path which is not starting from root
        self.assertEqual(RESTViews._folderpath_to_folderid("/sub_folder"), 0)

        # Test folder path which is not exsists
        self.assertEqual(RESTViews._folderpath_to_folderid("/wrong_folder"), 0)

        # Test folders with same name but diffrent places
        test_in_sub_folder = ecapp.models.Folder.objects.get(name="test", parent= sub_folder)
        self.assertEqual(RESTViews._folderpath_to_folderid("/folder_in_root/sub_folder/test"), test_in_sub_folder.id)
        test_in_sub_sub_folder = ecapp.models.Folder.objects.get(name="test", parent= sub_sub_folder)
        self.assertEqual(RESTViews._folderpath_to_folderid("/folder_in_root/sub_folder/sub_sub_folder/test"), test_in_sub_sub_folder.id)

    def test_rest_result(self):
        testcase = ecapp.models.TestCase.objects.get(name="sample_testcase")
        testplan = ecapp.models.TestPlan.objects.get(name="sample_testplan")
        testplan_testcase_link = ecapp.models.TestplanTestcaseLink.objects.get(testplan=testplan, testcase=testcase)
        status_before_api = ecapp.models.Result.objects.get(testplan_testcase_link=testplan_testcase_link, latest=True).status
        #test before updating the status
        self.assertEqual(status_before_api, "failed")
        data = {
                "testcase_name": "sample_testcase",
                "testplan_name": "sample_testplan",
                "result": "passed",
                "username": "test_user"
               }
        url = "/api/result"
        response = self.client.post(url,data)
        status_after_api = ecapp.models.Result.objects.get(testplan_testcase_link=testplan_testcase_link, latest=True).status
        # test after updating the status
        self.assertEqual(status_after_api, "passed")
        data = {
                "testcase_name": "sample_testcase_not_in_testplan",
                "testplan_name": "sample_testplan",
                "result": "passed",
                "username": "test_user"
               }
        response = self.client.post(url,data)
        # test for testcase not in testplan
        self.assertIn("FAIL", response.content)

    def test_rest_testcase_update(self):
        testcase = ecapp.models.TestCase.objects.get(name="sample_testcase")
        # test before update
        self.assertEquals(testcase.name, "sample_testcase")
        self.assertEquals(testcase.description, "Sample Testcase")
        self.assertEquals(testcase.folder_id, ecapp.models.Folder.objects.get(name='folder_in_root').id)
        data = {"name": "Name Updated By Testcase  Update API",
                "description": "Description Updated By TestCase Update API",
                "folder_id": ecapp.models.Folder.objects.get(name="sub_sub_folder").id}
        url = "/api/testcase/%d/update/" % testcase.id
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        #test after update
        updated_testcase = ecapp.models.TestCase.objects.get(id = testcase.id)
        self.assertEquals(updated_testcase.name, "Name Updated By Testcase  Update API")
        self.assertEquals(updated_testcase.description, "Description Updated By TestCase Update API")
        self.assertEquals(updated_testcase.folder_id, ecapp.models.Folder.objects.get(name="sub_sub_folder").id)
        
class OtherViewsTest(TestCase):
    fixtures = ['ecapp/fixtures/initial_data.json',]
    def setUp(self):
        self.client = Client()
        root_folder = ecapp.models.Folder.objects.get(name='root')
        sample_folder_in_root = ecapp.models.Folder.objects.create(name='folder_in_root', parent=root_folder)
        sample_sub_folder = ecapp.models.Folder.objects.create(name='sub_folder', parent=sample_folder_in_root)
        sample_sub_sub_folder = ecapp.models.Folder.objects.create(name='sub_sub_folder', parent=sample_sub_folder)
        test_in_sub_folder = ecapp.models.Folder.objects.create(name='test', parent=sample_sub_folder)
        test_in_sub_sub_folder = ecapp.models.Folder.objects.create(name='test', parent=sample_sub_sub_folder)

    def test_help(self):
        response = self.client.get('/help/')
        self.assertEqual(response.status_code, 200)

    def test_folder_and_child_folders_list(self):
        folder_in_root = ecapp.models.Folder.objects.get(name="folder_in_root")
        sub_folder = ecapp.models.Folder.objects.get(name="sub_folder")
        sub_sub_folder = ecapp.models.Folder.objects.get(name="sub_sub_folder")
        test_in_sub_folder = ecapp.models.Folder.objects.get(name="test", parent=sub_folder)
        test_in_sub_sub_folder = ecapp.models.Folder.objects.get(name="test", parent=sub_sub_folder)
        # folders in folder_in_root
        self.assertEqual(OtherViews.folder_and_child_folders_list(folder_in_root.id), [folder_in_root.id, sub_folder.id, sub_sub_folder.id, test_in_sub_folder.id, test_in_sub_sub_folder.id])
        # folders in sub_folder
        self.assertEqual(OtherViews.folder_and_child_folders_list(sub_folder.id), [sub_folder.id, sub_sub_folder.id, test_in_sub_folder.id, test_in_sub_sub_folder.id])
        # folders in sub_sub_folder
        self.assertEqual(OtherViews.folder_and_child_folders_list(sub_sub_folder.id), [sub_sub_folder.id, test_in_sub_sub_folder.id])
