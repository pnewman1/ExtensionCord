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
var testcase_summary = {    
    renderTestsTable:function (data){
        testcase_summary.makeRowsWithData(data['tests']);
        common.updatePaginate(data);
    },
    makeRowsWithData:function (testcases) {  

        $("#id_table").find("tr:gt(0)").remove(); //removes all rows (except head)
        
        // json data passed in from server must be "eval'ed"
        var t = eval( "("+testcases+")" );
        // iterate through each testcase
        for (index in t) {
            var tcName = t[index]['fields']['name'];
            if (t[index]['fields']['enabled'] == false){
                tcName += ' (Disabled)';
            }
            
            var tcPk = t[index]['pk'];
            var desc = t[index]['fields']['description'];
            
            var newRow = "";
            newRow += '<tr>';
            newRow += '<td> <input type="checkbox" class="checkbox" value=' + String(tcPk) + ' name=events_list' + '> </td>'
            newRow += '<td>' + tcPk + '</td>';

            newRow += common.getNameTD(tcPk, tcName, desc);

            newRow += '<td>' + t[index]['fields']['design_steps'].length + '</td>';
            newRow += '<td>' + t[index]['fields']['priority'] + '</td>';
            newRow += '<td><a href="./' + String(tcPk) + '/result/">View</a></td>';
            newRow += '</tr>';

            $('#id_table > tbody:last').append(newRow);

            common.addDescShowHideHandlers(tcPk, desc);
        }
        $(document).ready(function() 
           { 
              $("#id_table").tablesorter({
                headers: {
                    0: { sorter: false }
                }
              }); 
              $("#id_table td:nth-child(1),th:nth-child(1)").hide();
           } 
        ); 
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
            success: testcase_summary.renderTestsTable
        });
    }
};

$(function(){
    testcase.initialize();
    foldertree.initialize(testcase.onFolderChange);
    window.History.Adapter.bind(window,'statechange',testcase_summary.stateChangeCallback);
    testcase_summary.stateChangeCallback();
});

