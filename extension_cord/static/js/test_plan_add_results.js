/*
*
*   Copyright (c) 2013, Deem Inc. All Rights Reserved.
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
var result = {
    STATUS:{
        'failed':'Failed',
        'passed':'Passed',
        'na':'N/A',
        'blocked':'Blocked',
        'future':'Future',
        'notcomplet':'Not Complete',
    },
    onselectall_listener: function(){
        $('#select-all').click(function(event) {
            if(this.checked) {
                // Iterate each checkbox
                $('td :checkbox').each(function() {
                    this.checked = true;
                });
            } else {
                $('td :checkbox').each(function(){
                    this.checked = false;
                });
            }
        });
    },
    renderResultModal:function(data){
        $("#myModalLabel").empty();
        $("#myModalLabel").text(data["testcase"]);
        
        $("#result_table").empty();
        $("#result_table").append("<thead></thead>")
            .append("<tbody></tbody>");
        $("#result_table thead").append('<tr></tr>');
        header = [];
        header[0] = '<th> ID </th>';
        header[1] = '<th> Status </th>';
        header[2] = '<th> BUG ID </th>';
        header[3] = '<th> Note </th>';
        header[4] = '<th> Ninja ID </th>';
        header[5] = '<th> Date Run </th>';
        for (var i=0; i < header.length; i++){
            $("#result_table thead tr").append(header[i]);
        }
        var results = JSON.parse(data["results"]);
        for (index in results){
            var column = [];
            column[0] = '<td>'+results[index]['pk']+'</td>';
            column[1] = '<td>'+result.STATUS[results[index]['fields']['status']]+'</td>';
            column[2] = '<td>'+results[index]['fields']['bug_ticket']+'</td>';
            column[3] = '<td>'+results[index]['fields']['note']+'</td>';
            column[4] = '<td>'+results[index]['fields']['ninja_id']+'</td>';
            column[5] = '<td>'+results[index]['fields']['timestamp']+'</td>';
            $("#result_table tbody:last").append('<tr></tr>');
            for (var i =0 ; i< column.length; i++){
                    $("#result_table tbody tr:last").append(column[i]);
            }
        }
    },
    fetchResultDetails:function(testcase_id){
        $.ajax({
            type: "GET",
            url: "/ajax_showresults/"+ state.planid +"/"+testcase_id+"/",
            data:null,
            dataType: 'json',
            cache: false,
            success: result.renderResultModal
        });
    },

   renderTestCaseModal:function(data){
      $("#tcModalBody").empty();
      $("#tcModalBody").append(data);
   }, 

   fetchTestCaseModal:function(testcase_id){
       $.ajax({
            type: "GET",
            url: "/test_case/"+testcase_id+"/modal",
            data:null,
            dataType: 'html',
            cache: false,
            success: result.renderTestCaseModal
        });
   },

    stateChangeCallback:function () {

        var State = History.getState();
        testcase.deserialize();

        $("#root").dynatree("getTree").activateKey(state.key);
        $.ajax({
            type: "GET",
            url: "/ajax_tests/",
            data: testcase.serialize(),
            dataType: 'json',
            cache: false,
            success: result.renderTestsTable
        });
    },
    pfClickListener:function(event){
		event.preventDefault();
        var data = [];
        $("#id_table td input:checked").each(function() {
            var row = [];
            row.push(this.value);
            if (($(this).closest("tr").find("a:.bugstatus(0)")[0]) == undefined){
                row.push("");
            }
            else{
                var bug_object = $(this).closest("tr").find("a:.bugstatus");
                var bug_string = "";
                for (i=0;i<bug_object.length;i++)
                {
                    bug_string += bug_object[i].innerHTML + ",";
                }
                row.push(bug_string);
            }
            
            row.push($(this).closest("tr").find("textarea:eq(0)").val());
            data.push(row);
        });
        $.ajax({
            type: "POST",
            url: "/ajax_addresults/"+ state.planid +"/",
            data: { "type": $(this).attr('id'),
                    "data": JSON.stringify(data)
                  },
            dataType: 'json',
            cache: false,
            success: function(data){
                result.stateChangeCallback();
                common.fireAlert(data["message"], data["alertType"]);
            }
        });
    },
    resultClickListener:function(event){
        $('#myModal').modal();
        var testcase = event.target.parentElement.id;
        result.fetchResultDetails(testcase);
    },
    tcModalListener:function(event){
        $('#tcModal').modal();
        var testcase = event.target.id;
        result.fetchTestCaseModal(testcase);
    },
    resultUpdater:function(testcase_id,bugs,status){
        var data = [];
        var update_element = [];
        update_element.push(testcase_id);
        update_element.push(bugs);
        update_element.push("");

        data.push(update_element);
        $.ajax({
            type: "POST",
            url: "/ajax_addresults/"+ state.planid +"/",
            data: { "type": status,
                "data": JSON.stringify(data)
            },
            dataType: 'json',
            cache: false,
            success: function(data){
                result.stateChangeCallback();
                common.fireAlert(data["message"], data["alertType"]);
            }
        });
    },
    bugModalListener:function(event){
        var current_bugs = "";
        var testcase_id = this.id;
        var testcase_name = $(this).closest("tr").find('td:eq(2)').text();
        var current_status 
        var desc_string = "\n\nTest Case Name: " + testcase_name + "\n";

        for (var key in result.STATUS){
            if (result.STATUS[key] == $(this).data("status")){
                current_status = key;
            }
        }
        if (($(this).closest("tr").find("a:.bugstatus(0)")[0]) != undefined){
            var bug_object = $(this).closest("tr").find("a:.bugstatus");
            for (i=0;i<bug_object.length;i++)
            {
                current_bugs += bug_object[i].innerHTML + ",";
            }
        } 
        $('#id_summary').width(750);
        $('#id_description').width(750);
        $('#id_summary').val("ExtensionCord__TestCase: "+testcase_name+"__Status: "+current_status.toUpperCase());

        //get designsteps information to create description field of the bug form
        $.ajax({
            type: "GET",
            url: "/ajax_designsteps/"+testcase_id+"/fetch/",
            data: null,
            dataType: 'json',
            cache: false,
            success: function(data){
                desc_string += "Test Case ID: " + testcase_id + "\n"; 
                desc_string += "Status: " + current_status.toUpperCase() + "\n\n";
                desc_string += "Design Steps: \n";
                desc_string += "#\tProcedure\tExpected\tComments\n";
                for (i=0;i<data['data'].length;i++){
                    for(j=1;j<data['data'][i].length-2;j++){
                        desc_string += data['data'][i][j];
                        desc_string += '\t';
                    }
                desc_string += '\n';
                }
                $('#id_description').val(desc_string);
            }
        });

        $('#bugModal').dialog({
            modal: true,
            buttons: {
                "Link": function() {
                    $('#linkModal').dialog({
                        modal: true,
                        buttons: {
                            "Link": function() {
                                var updated_bugs = current_bugs + $('#bugID').val();
                                result.resultUpdater(testcase_id,updated_bugs,current_status);
                                $(this).dialog("close");
                            },
                        }
                    });
                    $(this).dialog("close");
                },
                "Create": function() {
                    $('#createBugModal').dialog({
                        modal: true,
                        minWidth: 800,
                        buttons: {
                            "Create": function() {
                                $.ajax({
                                    type: "POST",
                                    url: "/ajax_createbug/",
                                    data: $("#bugForm").serializeArray(),
                                    dataType: 'json',
                                    cache: false,
                                    success: function(data){
                                        if (data['bug_id']){
                                            var bugs = current_bugs + data['bug_id'];
                                            result.resultUpdater(testcase_id,bugs,current_status);
                                            $('#bugCreateModalMessage').append("<a class='bugstatus' title='Click to see Bug Details' href='#' style='color: #0088CC;'>" + data['bug_id'] +"</a> has been created.");
                                            $('#bugCreateModalMessage').dialog({
                                                modal: true,
                                                title: "Success",
                                                minWidth: 400,
                                                buttons: {
                                                    "OK": function() {
                                                        $(this).dialog("close");
                                                    }
                                                },
                                                close: function() {
                                                    $('#bugCreateModalMessage').empty();
                                                }
                                            });
                                        }
                                        else
                                        {
                                            $('#bugCreateModalMessage').append("<p><span style='color: red; font-size: 24px;'>&#9888;</span> "+data['error']+"</p>");
                                            $('#bugCreateModalMessage').dialog({
                                                modal: true,
                                                title: "Error",
                                                buttons: {
                                                    "OK": function() {
                                                        $(this).dialog("close");
                                                    }
                                                },
                                                close: function() {
                                                    $('#bugCreateModalMessage').empty();
                                                }
                                            });                                       
                                        }
                                    }
                                });
                                $(this).dialog("close");
                            }
                        }
                    });
                    $(this).dialog("close");
                },
            }
        });
    },

    bugStatusModalListener:function(event){
        $('#bugStatusModal').append("<div id='please_wait'><p>Please Wait...</p><img src='/static/ajax-loader-2.gif' /></div>");
        $.ajax({
            type: "GET",
            dataType: 'json',
            url: "/ajax_bugstatus/"+ event.target.innerHTML +"/",
            success: function(data){
                $('#please_wait').remove();
                if(data["error"] == undefined)
                {
                    $('#bugStatusModal').append("<table class='table table-bordered table-condensed' id='jira-status-table'></table>");
                    var tr = []
                    var bug_link = data['url'] + event.target.innerHTML;
                    tr[0] = "<tr><td><strong>Bug ID:</strong></td><td>" + event.target.innerHTML + "</td><tr>";
                    tr[1] = "<tr><td><strong>Status:</strong></td><td>" + data['status'] + "</td></tr>";
                    tr[2] = "<tr><td><strong>Priority:</strong></td><td>" + data['priority'] + "</td></tr>";
                    tr[3] = "<tr><td><strong>Assignee:</strong></td><td>" + data['assignee'] + "</td></tr>";
                    tr[4] = "<tr><td><strong>Reporter:</strong></td><td>" + data['reporter'] + "</td></tr>";
                    tr[5] = "<tr><td><strong>Summary:</strong></td><td>" + data['summary'] + "</td></tr>";
                    tr[6] = "<tr><td><strong>Bug URL:</strong></td><td><a style='color: #08c' target='_blank' href=" + bug_link + ">" + bug_link + "</a></td></tr>";
                    for (i=0; i<tr.length; i++){
                        $('#jira-status-table').append(tr[i]);
                    }
                }
                else
                {
                    $('#bugStatusModal').append("<div id='jira-error'></div>");
                    $('#jira-error').append("<p><span class='ui-icon ui-icon-alert' style='float:left;'></span>" + data["error"] + "</p>");
                }
            }
        });

        $('#bugStatusModal').dialog({
            modal:true,
            minWidth: 600,
            buttons: {
                "OK": function() {
                    $(this).dialog("close");
                }
            },
            close: function() {
                $('#bugStatusModal').empty();
            }
        });

    },
    initialize:function(){
        common.setupCSRFAjaxPost();
        $(".pfbutton").live("click",result.pfClickListener);
        $(".resultdetails").live("click",result.resultClickListener);
        $(".testcasemodal").live("click",result.tcModalListener);
        $(".bugmodal").live("click",result.bugModalListener);
        $(".bugstatus").tooltip();
        $(".bugstatus").live("click",result.bugStatusModalListener);
        $("#resultfilter").show();
        $("#folder-label").hide();
        $("#select-folder-button").hide();
    },
    makeRowsWithData:function (tests, status) {
        var url_parameters = $.getUrlVars();
        // json data passed in from server must be "eval'ed"
        $("#id_table tbody").find("tr:gt(0)").remove(); //removes all rows (except head)

        // iterate through each testcase
        for (index in tests) {
            var path = $(location).attr('pathname').split("/");
            var tcName = tests[index]['fields']['name'];
            var link_create = '';
            if (status[tests[index]['pk']]["message"] == "Blocked" || status[tests[index]['pk']]["message"] == "Failed"){
                link_create = '<a href="#" class="bugmodal pfbutton btn btn-mini" id='+tests[index]['pk']+' data-status='+ status[tests[index]['pk']]["message"] +'>Link/Create</a>';
            }
            if (tests[index]['fields']['enabled'] == false){
                tcName += ' (Disabled)';
            }
            var column = [];
            column[0] = '<td width="1%"><input class="checkbox uneditable-input" type="checkbox" value='+tests[index]['pk']+'></td>';
            column[1] = '<td width="5%"><center><a href="#" class="resultdetails" id='+tests[index]['pk']+'><span class="badge '+ status[tests[index]['pk']]["type"]+'">' + status[tests[index]['pk']]["message"] + '</span></a></center></td>';
            if (url_parameters['search'] == 'true'){
                column[2] = '<td width="18%"><a href="/test_case/'+tests[index]['pk']+'">'+tests[index]['fields']['name']+'</a></td>';
            }
            else{
                column[2] = '<td width="18%"><a href="/test_case/'+tests[index]['pk']+'/?navigate=true&testplan=' + state.planid +'">'+tests[index]['fields']['name']+'</a></td>';
            }
            
            column[3] = '<td width="4%"><a href="#" class="testcasemodal" id='+tests[index]['pk']+'>Details</a></td>';
            if (tests[index]['fields']['default_assignee']){
              column[4] = '<td width="7%">'+tests[index]['fields']['default_assignee']+'</td>';
            } else {
              edit_url = "/test_case/"+tests[index]['pk']+"/edit/"
              column[4] = '<td width="7%"><a href="'+edit_url+'">Assign to</a></td>';
            }
            if (String(status[tests[index]['pk']]['bug_id']).toLowerCase() != "null" && status[tests[index]['pk']]['bug_id'] != ""){
              var bugs = status[tests[index]['pk']]['bug_id'].split(/[\s,]/);
              var bugs_link =''
              for (var i=0; i<bugs.length; i++) {
                if(bugs[i] != ""){
                  bugs_link += '<a href="#" class="bugstatus" title="Click to see Bug Details">' + bugs[i] + '</a><br />';
               }
              }
              column[5] = '<td width="13%">'+bugs_link+link_create+'</td>';
            }
            else {
                column[5] = '<td width="13%">' +link_create+ '</td>';
            }
            if (status[tests[index]['pk']]['note'] != ""){
              column[6] = '<td width="35%"><textarea style="width: 95%; height: 1.2em;">'+status[tests[index]['pk']]['note']+'</textarea></td>';
            } else {
              column[6] = '<td width="35%"><textarea style="width: 95%; height: 1.2em;"></textarea></td>';
            }
            column[7] = '<td width="17%">'+status[tests[index]['pk']]['timestamp']+'</td>';

            $("#id_table tbody:last").append('<tr></tr>');
            for (var i =0 ; i< column.length; i++){
                $("#id_table tbody tr:last").append(column[i]);
            }
            result.onselectall_listener();
        }
    },
    renderTestsTable:function(data){
        var tests = JSON.parse(data['tests']);
        var noOfTests = tests.length;

        $("#id_table").empty();
        var header = [];
        if (noOfTests != 0){
            header[0] = '<th><input class="checkbox uneditable-input" id="select-all" type="checkbox"></th>';
            header[1] = '<th> Status </th>';
            header[2] = '<th> Name </th>';
            header[3] = '<th> Details </th>';
            header[4] = '<th> Assignee </th>';
            header[5] = '<th> BUG ID</th>';
            header[6] = '<th> Comment </th>';
            header[7] = '<th> Date Run </th>';
            $("#id_table").append("<thead></thead>")
                          .append("<tbody></tbody>");
            $("#id_table thead").append('<tr></tr>');
            for (var i=0; i < header.length; i++){
                $("#id_table thead tr").append(header[i]);
            }
            result.makeRowsWithData(tests, data['status']);
            common.updatePaginate(data);
            $("#select-all").attr("checked", false);

            if (!connected){
                $('td:nth-child(6)').hide();
                $('th:nth-child(6)').hide();
            }
        }
        else{
            currfolder = foldertree.getActiveKey()||-100;
            if (currfolder != -100){
                $("#id_table").append("<p>Either this folder has tests in its subfolder or all its tests were deleted recently. Do a refresh to update the folder</p>");
            }
            $("#prevpage").addClass("disabled");
            $("#nextpage").addClass("disabled");
            $("#currpage a").empty();
            $("#currpage a").append("0");
        }
    }
};

$(function(){
    result.initialize();
    testcase.initialize();
    foldertree.initialize(testcase.onFolderChange);
    window.History.Adapter.bind(window,'statechange',result.stateChangeCallback);
    result.stateChangeCallback();
});

