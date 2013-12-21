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
import datetime
import pytz
import logging

from django.db import models
from django.db.models import Count, Q
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)


class Folder(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    parent = models.ForeignKey('self', null=True, blank=True)
    import_id = models.IntegerField(null=True, blank=True, help_text='ID for this item in the external DB it was imported from', db_index=True)

    class Meta:
        unique_together = (('name', 'parent',),)

    def __unicode__(self):
        return str(self.name)

    @staticmethod
    def get_root_folder():
        return Folder.objects.get(name="root")

    def folder_path_raw(self):
        if self.name == "root":
            return "/"
        else:
            folder_path = self.name
            parent = self.parent
            while parent.name != "root":
                folder_path = parent.name + "/" + folder_path
                parent = parent.parent
            return "/" + folder_path

    def folder_path_display(self):
        raw = self.folder_path_raw()
        if not raw or len(raw) == 0:
            return "root"
        return raw[1:]

    def folder_path(self):
        return self.folder_path_raw()

    def in_testplan(self, testplan_id):
        folder_and_child_folders_list = [self.id]
        query_list = folder_and_child_folders_list
        has_child = True
        while has_child:
            if len(query_list)>0 :
                child_folders = Folder.objects.filter(parent_id__in=query_list)
                query_list = []
                for item in child_folders:
                    folder_and_child_folders_list.append(item.id)
                    query_list.append(item.id)
            else:
                has_child = False

        return TestPlan.objects.get(pk=testplan_id).testcases.filter(folder_id__in=folder_and_child_folders_list)

    def child_nodes(self, testplan_id=None):
        node_list = []
        add_to_end = None

        for item in Folder.objects.filter(parent__id=self.id).order_by('name'):
            if not testplan_id or item.in_testplan(testplan_id):
                if Folder.objects.filter(parent=item).count() > 0:
                    # the children list is a hack to show the plus sign
                    if item.name != "deletedfolders":
                        node_list.append({
                            "title": item.name,
                            "isFolder": True,
                            "key": item.id,
                            "children": [{
                                "title": "",
                                "key": "hack" + str(item.id)
                            }]
                        })
                    else:
                        add_to_end = {
                            "title": item.name,
                            "isFolder": False,
                            "key": item.id,
                            "children": [{
                                "title": "",
                                "key": "hack" + str(item.id)
                            }]
                        }
                else:
                    node_list.append({
                        "title": item.name,
                        "isFolder": True,
                        "key": item.id
                    })
        if add_to_end:
            node_list.append(add_to_end)
        return node_list


class DesignStep(models.Model):
    step_number = models.IntegerField()
    procedure = models.TextField()
    expected = models.TextField()
    comments = models.TextField()
    import_id = models.IntegerField(null=True, blank=True, help_text='ID for this item in the external DB it was imported from', db_index=True)


class UploadedFile(models.Model):
    caption = models.CharField(max_length=255, blank=True, null=True, help_text='a description of the uploaded file')
    file = models.FileField(max_length=255, upload_to='testcase_uploads/%Y/%m/%d')
    slug = models.SlugField(max_length=150, blank=True, help_text='original filename - this is automatically set')

    @models.permalink
    def get_absolute_url(self):
        return self.url

    def save(self, *args, **kwargs):
        if not len(self.slug):
            self.slug = self.file.name
        if not len(self.caption):
            self.caption = self.file.name
        super(UploadedFile, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.file.delete(False)
        super(UploadedFile, self).delete(*args, **kwargs)

    def __unicode__(self):
        return self.caption + " (" + self.slug + ")"


class TestCase(models.Model):
    name = models.CharField(max_length=255, help_text='a descriptive conventional format, like travel-air-787', db_index=True)
    description = models.TextField(null=True, blank=True, help_text='description of what the test case does')
    author = models.ForeignKey(User, related_name='author', editable=True)
    enabled = models.BooleanField(default=True)
    is_automated = models.BooleanField(default=False,)
    default_assignee = models.ForeignKey(User, editable=True, null=True)
    folder = models.ForeignKey(Folder, null=True)
    added_version = models.CharField(max_length=100, null=True, blank=True)
    deprecated_version = models.CharField(max_length=100, null=True, blank=True)
    bug_id = models.CharField(max_length=100, null=True, blank=True)
    updated_datetime = models.DateTimeField(null=True, blank=True)
    updated_by = models.ForeignKey(User, related_name='updated_by', null=True, editable=True)
    related_testcase = models.ForeignKey('self', null=True, blank=True, help_text='Use this field to link to another test case id')
    LANGUAGE_CHOICES = (
        ('J', 'Java'),
        ('P', 'Python'),
    )
    language = models.CharField(max_length=1, choices=LANGUAGE_CHOICES, null=True, blank=True, default='P')
    test_script_file = models.CharField(max_length=1000, null=True, blank=True)
    method_name = models.CharField(max_length=255, null=True, blank=True, help_text='what method the test case is, eg test_booking()')
    import_id = models.IntegerField(null=True, blank=True, help_text='ID for this item in the external DB it was imported from', db_index=True)
    creation_date = models.DateTimeField(null=True, blank=True)
    PRIORITY_CHOICES = (
        ('P1', 'Critical (P1)'),
        ('P2', 'Major (P2)'),
        ('P3', 'Minor (P3)'),
        ('P4', 'Trivial (P4)'),
    )
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, null=True, blank=True)
    product = models.CharField(max_length=20, null=True, blank=True)
    feature = models.CharField(max_length=20, null=True, blank=True)
    CASE_TYPE_CHOICES = (
        ('Regression', 'Regression'),
        ('Mixed mode', 'Mixed mode'),
        ('New feature', 'New feature'),
        ('Automated Regression', 'Automated Regression'),
        ('Manual Only', 'Manual Only'),
        ('Migration', 'Migration'),
        ('Hotfix', 'Hotfix'),
        ('Production Sanity Check', 'Production Sanity Check'),
    )
    case_type = models.CharField(max_length=30, choices=CASE_TYPE_CHOICES, default='Regression', null=True, blank=True)
    design_steps = models.ManyToManyField(DesignStep, null=True, blank=True, help_text='steps to run when executing this test case, and the expected results')
    uploads = models.ManyToManyField(UploadedFile, null=True, blank=True, help_text='files associated with this test case -')

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return "/test_case/%i/" % self.id

    def save(self, *args, **kwargs):
        if not self.id:
            self.creation_date = datetime.datetime.now(pytz.timezone('US/Pacific'))
        super(TestCase, self).save(*args, **kwargs)


class ResultCounts:
    def __str__(self):
        return "%d passed, %d failed, %d not run" % (self.passed, self.failed, self.notrun)

    def __init__(self, testplan_id):
        results = {}
        results['passed'] = 0
        results['failed'] = 0
        results['blocked'] = 0
        results['notrun'] = 0

        all_latest_results = Result.objects.filter(latest=True, testplan_testcase_link__testplan__id=testplan_id)
        all_cases = TestplanTestcaseLink.objects.filter(testplan__id=testplan_id, testcase__enabled=1)
        total = all_cases.count()

        raw_results = Result.objects.filter(latest=True, testplan_testcase_link__testplan__id=testplan_id).values('status').annotate(status_count=Count('status'))
        for raw_result in raw_results:
            results[raw_result['status']] = raw_result['status_count']
        self.passed = results['passed']
        self.failed = results['failed']
        self.blocked = results['blocked']
        self.notrun = all_cases.exclude(id__in=all_latest_results.values("testplan_testcase_link")).count()

        if total != 0:
            self.pass_rate = self.passed/float(total)*100.0

        if total != 0 and self.notrun != total:
            self.progress = (total-self.notrun-self.blocked)/float(total)*100.0
        else:
            self.progress = 0

        logger.debug("created resultcounts '%s' for plan %d" % (self, testplan_id))


class TestPlan(models.Model):
    name = models.CharField(max_length=255, db_index=True, unique=True)
    creator = models.ForeignKey(User, related_name='creator')
    enabled = models.BooleanField(default=True, help_text='rather than delete, we will disable')
    schedule = models.CharField(max_length=20, null=True, blank=True, help_text='cron notation')
    release = models.CharField(max_length=50, null=True, blank=True, help_text='release name (if applicable)')
    testcases = models.ManyToManyField(TestCase, null=True, blank=True, through='TestplanTestcaseLink')
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    leader = models.CharField(max_length=300, null=True, blank=True)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return "/test_plan/%i/" % self.id

    def result_counts(self):
        return ResultCounts(self.id)

    def enabled_testcases(self):
        return self.testcases.filter(enabled=1)


class TestplanTestcaseLink(models.Model):
    testcase = models.ForeignKey(TestCase)
    testplan = models.ForeignKey(TestPlan)

    class Meta:
        unique_together = (('testcase', 'testplan',), )


class Result(models.Model):
    testplan_testcase_link = models.ForeignKey(TestplanTestcaseLink)
    timestamp = models.DateTimeField()
    STATUS_CHOICES = (
        ('failed', 'Failed'),
        ('passed', 'Passed'),
        ('na', 'N/A'),
        ('blocked', 'Blocked'),
        ('future', 'Future'),
        ('notcomplet', 'Not Complete'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='failed')
    environment = models.CharField(max_length=100, null=True, blank=True)
    tester = models.CharField(max_length=100)
    ninja_id = models.CharField(max_length=150, null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    bug_ticket = models.TextField(null=True, blank=True)
    latest = models.BooleanField(default=True)

    def __unicode__(self):
        return str(self.testplan_testcase_link.testplan) + " - " + str(self.testplan_testcase_link.testcase)

    def save(self, *args, **kwargs):
        ''' On save, update timestamps if this is its first time saving '''
        if not self.id:
            self.timestamp = datetime.datetime.now(pytz.timezone('US/Pacific'))

        Result.objects.filter(testplan_testcase_link=self.testplan_testcase_link).update(latest=False)
        self.latest = True
        super(Result, self).save(*args, **kwargs)
