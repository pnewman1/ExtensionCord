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
# THIS IS WHERE SHORTCUT FUNCTIONS ARE STORED AND CREATED FOR VIEWS.PY

from ecapp.models import *
from django.utils import simplejson

#add DesignSteps for a testcase
def add_designstep(request,form):
    #numSteps is the total number of Design Steps to be added
    numSteps = len(request.POST['step_number'].split(','))

    # steps is going to be a list of DesignStep instances to be add to the test case
    steps = []

    #iterate through each step number
    for i in range(0,numSteps):
        #create a newStep to be added
        newStep = DesignStep()

        #iterate through each design step fields required and fish for it in the request
        for field,value in vars(newStep).items():
            if field in request.POST:
                # field_list will be a list of values for a specific field
                # e.g. if field == Animal (this field doesnt rly exist)
                # field_list == ['dog', 'cat', 'kangaroo' ]
                # the appropriate animal is picked by the variable "i" in the upper "for" loop
                field_list = request.POST[field].split(',')

                # exec_statement then assigns that field to a DesignStep instance
                exec_statement = "newStep." + field + "='" + field_list[i] +"'"
                # e.g. exec_statement will be "newStep.Animal = 'dog'"
                # then gets run through "exec" which runs a string as a statement
                exec(exec_statement)

        newStep.save()
        steps.append(newStep)

    #delete all previous steps and add the new ones
    form.design_steps.all().delete()
    for step in steps:
        # add each DesignStep instance to the testcase
        form.design_steps.add(step)



# SEARCH BAR UTILITY
import re
from django.db.models import Q

def parseQuery(queryString,
                    findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
                    normspace=re.compile(r'\s{2,}').sub):
    ''' Parses the query string to keywords in an array, getting rid of unecessary spaces
        and grouping quoted words together.
        e.g.:
        >>> parseQuery('  some random  words "with   quotes  " and   spaces')
        ['some', 'random', 'words', 'with quotes', 'and', 'spaces']

    '''
    return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(queryString)]

def get_query(query_string, search_fields):
    ''' Returns a query, that is a combination of Q objects. That combination
        aims to search keywords within a model by testing the given search fields.

    '''
    query = None # Query to search for every search term
    terms = parseQuery(query_string)
    for term in terms:
        or_query = None # Query to search for a given term in each field
        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q
        if query is None:
            query = or_query
        else:
            query = query & or_query
    return query
#END SEARCHBAR
