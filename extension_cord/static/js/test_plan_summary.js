/*
*
*   Copyright (c) 2013, Rearden Commerce Inc. All Rights Reserved.
*
*   Licensed under the Apache License, Version 2.0 (the "License");
*   you may not use this file except in compliance with the License.
*   You may obtain a copy of the License at
*
*       http://www.apache.org/licenses/LICENSE-2.0
*
*   Unless required by applicable law or agreed to in writing, software
*   distributed under the License is distributed on an "AS IS" BASIS,
*   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
*   See the License for the specific language governing permissions and
*   limitations under the License.
*
*/
var CURRPAGE = 1;
var VIEWDISABLED = false;
var QUERY = "";

var plansummary = {
    // searchbar calls this on submit
    init:  function(){
        $("#searchForm").submit(function() {
            // get the search query inside the search bar
            QUERY = $("#searchbar").val() ;
            CURRPAGE= 1;
            var dataString = "&ajaxMethod=ajaxTests&page=" + CURRPAGE +"&disabled="+VIEWDISABLED+"&query="+QUERY;
            
            $.ajax({
                type: "GET",
                url: "./",
                data: dataString,
                dataType: 'json',
                cache: false,
                success: function(data){
                    // NOTE, this makeRowsWithData is not to be confused with the makeRowsWithData in common.js
                    makeRowsWithData(data['tests']);
                    updatePaginate(data);
                }
            }) 

        })

        // when view disabled link is clicked, switch between displaying disabled cases
        $("#viewDisabled").click(function(event){
            event.preventDefault();
            var CURRPAGE = 1;
            if (VIEWDISABLED) {
                VIEWDISABLED = false;
                document.getElementById('viewDisabled').innerHTML = "View Disabled Test Cases"
            } else {
                VIEWDISABLED = true;
                document.getElementById('viewDisabled').innerHTML = "View Enabled Test Cases"
            }
            // make the ajaxMethod = paginate, because they will do the exact same thing in the server side
            var dataString = "&ajaxMethod=ajaxTests&disabled=" + VIEWDISABLED + "&page=" + CURRPAGE+"&query="+QUERY;
            
            $.ajax({
                type: "GET",
                url: "./",
                data: dataString,
                dataType: 'json',
                cache: false,
                success: function(data){
                    // NOTE, this makeRowsWithData is not to be confused with the makeRowsWithData in common.js
                    makeRowsWithData(data['tests']);
                    updatePaginate(data);
                }
            })
        })
    }
}

var testPlanSearch = {
    init:function() {
        $("#planSearchForm").submit( function() { 
            var formdata = $(this).find('input').not('[value=""]').serialize();
            window.location.href = "/test_plan/archive/?search=true&" + formdata;
        });
    }
}

$(function(){
    plansummary.init();
    testPlanSearch.init();
})
