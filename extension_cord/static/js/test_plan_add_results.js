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
        var data = [];
        $("#id_table td input:checked").each(function() {
            var row = [];
            row.push(this.value);
            row.push($(this).closest("tr").find("textarea:eq(0)").val());
            row.push($(this).closest("tr").find("textarea:eq(1)").val());
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
    initialize:function(){
        common.setupCSRFAjaxPost();
        $(".pfbutton").live("click",result.pfClickListener);
        $(".resultdetails").live("click",result.resultClickListener);
        $(".testcasemodal").live("click",result.tcModalListener); 
        $("#resultfilter").show();
        $("#folder-label").hide();
        $("#select-folder-button").hide();
    },
    makeRowsWithData:function (tests, status) {
        // json data passed in from server must be "eval'ed"
        $("#id_table tbody").find("tr:gt(0)").remove(); //removes all rows (except head)

        // iterate through each testcase
        for (index in tests) {
            var tcName = tests[index]['fields']['name'];
            if (tests[index]['fields']['enabled'] == false){
                tcName += ' (Disabled)';
            }
            var column = [];
            column[0] = '<td><input class="checkbox uneditable-input" type="checkbox" value='+tests[index]['pk']+'></td>';
            column[1] = '<td><center><a href="#" class="resultdetails" id='+tests[index]['pk']+'><span class="badge '+ status[tests[index]['pk']]["type"]+'">' + status[tests[index]['pk']]["message"] + '</span></a></center></td>';
            column[2] = '<td><a href="/test_case/'+tests[index]['pk']+'">'+tests[index]['fields']['name']+'</a></td>';
            column[3] = '<td><a href="#" class="testcasemodal" id='+tests[index]['pk']+'>Details</a></td>';
            if (status[tests[index]['pk']]['default_assignee'] != ""){
              column[4] = '<td>'+tests[index]['fields']['default_assignee']+'</td>';
            } else {
              column[4] = '<td><textarea rows="1"></textarea></td>';
            }
            if (String(status[tests[index]['pk']]['bug_id']).toLowerCase() != "null" && status[tests[index]['pk']]['bug_id'] != ""){
              var bugs = status[tests[index]['pk']]['bug_id'].split(/[\s,]/);
              var bugs_link =''
              for (var i=0; i<bugs.length; i++) {
                if(bugs[i] != ""){ 
                  bugs_link += '<a href="'+bug_url+bugs[i]+'">' + bugs[i] + '</a><br />';
                }
              }
              column[5] = '<td><textarea rows="1">'+status[tests[index]['pk']]['bug_id']+'</textarea><br />'+bugs_link+'</td>';   
            } else {
              column[5] = '<td><textarea rows="1"></textarea></td>';
            }
            if (status[tests[index]['pk']]['note'] != ""){
              column[6] = '<td><textarea rows="2">'+status[tests[index]['pk']]['note']+'</textarea></td>';
            } else {
              column[6] = '<td><textarea rows="2"></textarea></td>';
            }
            column[7] = '<td>'+status[tests[index]['pk']]['timestamp']+'</td>'; 

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
            header[5] = '<th> BUG ID </th>';
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

