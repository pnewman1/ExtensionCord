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
from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import RedirectView

from ecapp.views.FileUploadViews import PictureCreateView, PictureDeleteView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('ecapp.views',
    url(r'^$', RedirectView.as_view(url='/test_plan/'), name='home'),
    url(r'^index$','OtherViews.index', name='index'),

    url(r'^test_case/$','TestCaseViews.test_case_summary_view', name='testcases'),
    url(r'^test_case/bulk/$','OtherViews.ajax_testcasebulk', name="case_bulk"),
    url(r'^test_case/(?P<test_case_id>\d+)/edit/$','TestCaseViews.test_case_edit', name="case_edit"),
    url(r'^test_case/(?P<test_case_id>\d+)/result/$','TestCaseViews.test_case_plot', name="case_result"),
    url(r'^test_case/(?P<test_case_id>\d+)/$','TestCaseViews.test_case_view', name="case_view"),
    url(r'^test_case/(?P<test_case_id>\d+)/modal/$','TestCaseViews.test_case_modal', name="case_modal"),
    url(r'^create_test_case/$','TestCaseViews.test_case_edit', name="test_create"),
    url(r'^clone_test_case/(?P<test_case_id>\d+)/$','TestCaseViews.test_case_clone', name="test_clone"),

    (r'^test_case/upload_new/(?P<testcase_id>\d+)$', PictureCreateView.as_view(), {}, 'upload-new'),
    (r'^test_case/upload_delete/(?P<pk>\d+)$', PictureDeleteView.as_view(), {}, 'upload-delete'),

    url(r'^test_plan/$','TestPlanViews.test_plan_summary_view', name='testplans'),
    url(r'^test_plan/archive/$','TestPlanViews.test_plan_archive_view', name='testplan_archive'),
    url(r'^test_plan/(?P<test_plan_id>\d+)/result/$','TestPlanViews.test_plan_add_results', name="plan_add_results"),
    url(r'^test_plan/(?P<test_plan_id>\d+)/plot/$','TestPlanViews.test_plan_plot', name="plan_view_plot"),
    url(r'^test_plan/(?P<test_plan_id>\d+)/edit/$','TestPlanViews.edit_test_plan_view', name="plan_edit"),
    url(r'^create_test_plan/$','TestPlanViews.create_test_plan_view', name="plan_create"),
    url(r'^clone_test_plan/(?P<test_plan_id>\d+)/$','TestPlanViews.clone_test_plan_view', name="plan_clone"),
    url(r'^test_plan/(?P<test_plan_id>\d+)/tests/add/$','TestPlanViews.add_testcases_view', name="plan_add_tests"),
    url(r'^test_plan/(?P<test_plan_id>\d+)/tests/review/$','TestPlanViews.review_testcases_view', name="plan_review_tests"),
    url(r'^test_plan/(?P<test_plan_id>\d+)/analyze/$','TestPlanViews.analyze', name="plan_analyze"),

    url(r'^ajax_folders/$','OtherViews.ajax_folders', name='ajax_folders'),
    url(r'^ajax_plan_details/$','OtherViews.ajax_plan_details', name='ajax_plan_details'),
    url(r'^ajax_tests/$','OtherViews.ajax_tests', name='ajax_tests'),
    url(r'^ajax_designsteps/(?P<testcase_id>-?\d+)/fetch/$','OtherViews.ajax_fetch_designsteps', name='ajax_fetch_designsteps'),
    url(r'^ajax_designsteps/(?P<testcase_id>-?\d+)/edit/$','OtherViews.ajax_edit_designsteps', name='ajax_edit_designsteps'),
    url(r'^ajax_testcase_uploads/(?P<testcase_id>-?\d+)/fetch/$','OtherViews.ajax_fetch_uploads', name='ajax_fetch_uploads'),
    url(r'^ajax_testcase_uploads/(?P<testcase_id>-?\d+)/edit/$','OtherViews.ajax_edit_uploads', name='ajax_edit_uploads'),
    url(r'^ajax_addfolder/$','OtherViews.ajax_addfolder'),
    url(r'^ajax_deletefolder/$','OtherViews.ajax_deletefolder'),
    url(r'^ajax_renamefolder/$','OtherViews.ajax_renamefolder'),
    url(r'^ajax_addtests/(?P<testplan_id>\d+)/$','OtherViews.ajax_addtests', name="ajax_add_tests"),
    url(r'^ajax_removetests/(?P<testplan_id>\d+)/$','OtherViews.ajax_removetests', name="ajax_remove_tests"),
    url(r'^ajax_addresults/(?P<testplan_id>\d+)/$','OtherViews.ajax_addresults', name="ajax_add_results"),
    url(r'^ajax_showresults/(?P<testplan_id>\d+)/(?P<testcase_id>\d+)/$','OtherViews.ajax_showresults', name="ajax_show_results"),

    url(r'^api/$','RESTViews.restAPI', name='api'),
    url(r'^api/find_tests_by_folder/(?P<folder_id>\w{0,50})/$','RESTViews.rest_find_tests_by_folder', name='rest_find_tests_by_folder'),
    url(r'^api/find_tests_by_folder/$','RESTViews.rest_find_tests_by_folder', name='rest_find_tests_by_folder'),
    url(r'^api/result$','RESTViews.rest_result', name='rest_result'),
    url(r'^api/result/$','RESTViews.rest_result'),
    url(r'^api/testcase/(?P<id>\d+)$','RESTViews.rest_testcase', name='rest_testcase'),
    url(r'^api/testcase/$','RESTViews.rest_testcase', name='rest_testcase'),
    url(r'^api/testcase$','RESTViews.rest_testcase', name='rest_testcase'),
    url(r'^api/testplan/(?P<name>.+?)/$','RESTViews.rest_testplan', name='rest_testplan'),
    url(r'^api/testplan/$','RESTViews.rest_testplan', name='rest_testplan'),
    url(r'^api/testplan$','RESTViews.rest_testplan', name='rest_testplan'),
    url(r'^api/add_testcase_to_existing_testplan', 'RESTViews.rest_add_tc_to_existing_tp', name='rest_add_tc_to_existing_tp'),

    url(r'^help/$','OtherViews.help', name='help'),
    url(r'^metrics/$','OtherViews.metrics_dashboard', name='metrics'),
)

urlpatterns += patterns('',
    #using the django provided login
    #corresponding html can be found in /templates/registration/
    url(r'^login/$', 'django.contrib.auth.views.login', name='login'),
    url(r'^logout/$', 'ecapp.logout.logout_page', name='logout'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += staticfiles_urlpatterns()
