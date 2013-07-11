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
from django.contrib import admin

class TwentyPerPageAdmin(admin.ModelAdmin):
    list_per_page = 20

class DesignStepAdmin(TwentyPerPageAdmin):
    list_display = ('step_number','procedure','comments')
    list_display_links = list_display
    ordering = ('id',)
    search_fields = ['procedure','expected','comments',]

class FolderAdmin(TwentyPerPageAdmin):
    list_display = ('name','parent','import_id')
    list_display_links = list_display
    ordering = ('name',)
    search_fields = ['name','import_id']

class ResultAdmin(TwentyPerPageAdmin):
    list_display = ('status','tester','bug_ticket','timestamp',)
    list_display_links = list_display
    list_filter = ('status','tester','bug_ticket','timestamp',)
    ordering = ('-timestamp',)

class TestCaseAdmin(TwentyPerPageAdmin):
    list_display = ('name','folder','author','priority')
    list_display_links = list_display
    ordering = list_display
    search_fields = ['name','description']
    exclude = ("design_steps",)

class TestPlanAdmin(TwentyPerPageAdmin):
    list_display = ('name','creator','enabled','schedule','release','start_date','end_date','leader')
    list_display_links = list_display
    ordering = ('end_date','start_date','name')
    search_fields = ['name','release']

class UploadedFileAdmin(TwentyPerPageAdmin):
    list_display = ('caption',)
    list_display_links = list_display
    search_fields = list_display

admin.site.register(DesignStep, DesignStepAdmin)
admin.site.register(Folder, FolderAdmin)
admin.site.register(Result, ResultAdmin)
admin.site.register(TestCase,TestCaseAdmin)
admin.site.register(TestPlan,TestPlanAdmin)
admin.site.register(UploadedFile, UploadedFileAdmin)

