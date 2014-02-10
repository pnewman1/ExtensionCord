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
from django.forms import ModelForm
from django.contrib.auth.models import User
from django import forms
from django.conf import settings

from ecapp.models import TestCase, TestPlan

from jira.client import JIRA


class TestCaseForm(ModelForm):
    author = forms.ModelChoiceField(queryset=User.objects.all(),
                                    widget=forms.HiddenInput())
    default_assignee = forms.ModelChoiceField(required=False,
                                              queryset=User.objects.all().order_by('username'))
    related_testcase = forms.ModelChoiceField(required=False,
                                              queryset=TestCase.objects.all(),
                                              widget=forms.TextInput)

    class Meta:
        model = TestCase
        fields = (
            'name', 'description', 'author', 'enabled',
            'is_automated', 'default_assignee', 'folder', 'added_version',
            'deprecated_version', 'language', 'test_script_file',
            'method_name', 'bug_id', 'related_testcase', 'import_id',
            'priority', 'product', 'feature', 'case_type',
            'design_steps', 'uploads')


class TestPlanForm(ModelForm):
    creator = forms.ModelChoiceField(queryset=User.objects.all(),
                                     widget=forms.HiddenInput())

    class Meta:
        model = TestPlan
        fields = (
            'name', 'creator', 'enabled', 'start_date',
            'end_date', 'release', 'leader', 'schedule',
        )


class TestCaseBulkForm(ModelForm):
    class Meta:
        model = TestCase
        fields = (
            'folder', 'added_version', 'enabled', 'default_assignee', 'is_automated', 'priority',
            'product', 'case_type')


def bug_project_choices():
    jira = JIRA(options={'server': settings.BUG_SERVER}, basic_auth=(settings.BUG_USER, settings.BUG_PASSWORD))
    projects = jira.projects()

    choices = []
    for project in projects:
        choices.append((project.key, project.key))

    return tuple(choices)


class BugForm(forms.Form):
    project = forms.ChoiceField(choices=bug_project_choices())
    summary = forms.CharField()
    priority = forms.ChoiceField(choices=(
        ("Critical (P1)", 'Critical (P1)'), ('Major (P2)', 'Major (P2)'), ('Minor (P3)', 'Minor (P3)'),
        ('Trivial (P4)', 'Trivial (P4)'),
        ('Unassigned', 'Unassigned'), ('Blocker (retired)', 'Blocker (retired)')))
    reporter = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    description = forms.CharField(widget=forms.Textarea)
