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
import logging

from django.shortcuts import redirect
from django.contrib.auth import logout
from django.shortcuts import render_to_response

def logout_page(request):
    log = logging.getLogger('actions_log')
    if str(request.user) != 'AnonymousUser':
        log.info("%s logged out" % request.user)
    logout(request)
    return render_to_response('registration/logout.html')
