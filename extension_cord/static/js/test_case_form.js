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
var endsWith = function(string1, string2, ignorecase) {
    return string1.length - (
      ignorecase !== true ? string1.lastIndexOf(string2) :
        string1.toLowerCase().lastIndexOf(string2.toLowerCase())
    ) === string2.length;
};

testcaseform = {
    testcaseID: current_testcase_id,
    datatype: "local",
    designstepstable : 
    {
        prevkey:null,
        designsteps:[],
        colNames:['Id', 'Step Number', 'Procedure', 'Expected', 'Comments'],
        colModel:[
            {name:'id',index:'id', hidden: true,  maxlength:"5"},
            {name:'step_number',index:'step_number', editable: true,  
                sortable: false, maxlength:"5", width:50},
            {name:'procedure',index:'procedure', width:150, editable: true, edittype:"textarea",
                sortable: false, editoptions: {rows:"2", maxlength: 5000 }} ,
            {name:'expected',index:'expected', width:80, editable: true, edittype:"textarea",
                sortable: false, editoptions: {rows:"2",  maxlength: 5000}},
            {name:'comments',index:'comments', width:150, editable: true, edittype:"textarea",
                sortable: false, editoptions:{rows:"2",  maxlength: 3000}}
        ],
        pager: '#designstepsgridpager',
        jsondataformat:{
            root:"data",
            page: "currpage",
            total: "totalpages",
            records: "totalrecords",
            cell: "",
            id: "0"
        },
        parameters:{
            edit:true,
            refresh:true,
            del:true,
            search:false,
        },
        afterSubmit:function(data){
            testcaseform.designstepstable.designsteps.push(data.responseText);
            var url = "/ajax_designsteps/"+testcaseform.testcaseID+"/fetch/";
            var params1 = testcaseform.designstepstable.designsteps||null;
        if (clone == true){
            params1 = $('#designstepstable').jqGrid('getDataIDs'); // get updated IDs
            params1.push(data.responseText);
        }
            url = encodeURI(url + "?designsteps=" + params1.toString());
            $("#designstepstable").jqGrid('setGridParam',{url:url}).trigger("reloadGrid");
            return true;
        },
    },
    uploadstable : 
    {
        prevkey:null,
        uploads:[],
        colNames:['Id', 'Caption', 'URL'],
        colModel:[
            {name:'id', index:'id', width:20, editable: false, sortable: false},
            {name:'caption', index:'caption', width:100, editable: true,  
                sortable: false, editoptions:{rows:"3",  maxlength: 250}},
            {name:'url', index:'url', width:100, editable: false, sortable:false, 
                formatter:function(cellvalue, options, rowObject) {
                    if(endsWith(cellvalue,".png",true) || 
                        endsWith(cellvalue,".gif",true) || 
                        endsWith(cellvalue,"jpg",true) || 
                        endsWith(cellvalue,"bmp",true)
                    ) {
                        return "<a href='" + MEDIA_URL + cellvalue + "'>" +
                            "<img src=" + MEDIA_URL + cellvalue + " href='" + MEDIA_URL + cellvalue + "' alt=" + cellvalue + " title=" + cellvalue + " />" + "</a>";
                    } else {
                        return "<a href='" + MEDIA_URL + cellvalue + "'>" + cellvalue + "</a>";
                    }
                } 
            }
        ],
        pager: '#uploadsgridpager',
        jsondataformat:{
            root:"data",
            page: "currpage",
            total: "totalpages",
            records: "totalrecords",
            cell: "",
            id: "0"
        },
        parameters:{
            edit:true,
            refresh:true,
            del:true,
            search:false,
            add:false,
        },
        afterSubmit:function(data){
            testcaseform.uploadstable.uploads.push(data.responseText);
            var url = "/ajax_testcase_uploads/"+testcaseform.testcaseID+"/fetch/";
            var params1 = testcaseform.uploadstable.uploads||null;
            url = encodeURI(url + "?uploads=" + params1.toString());
            $("#uploadstable").jqGrid('setGridParam',{url:url}).trigger("reloadGrid");
            return true;
        },
    },
    getDataType:function(){
        var datatype = "json";
        if (clone==true){
            datatype = "local";
        }
        else{
            datatype = "json";
        }
        return datatype;
    },
    loadLocalDataForCloning:function(){
        if (clone == true){
            for(var i=0;i<gridData.length;i++){
	        $("#designstepstable").jqGrid('addRowData',gridData[i]['id'],gridData[i]);
            }
        }
    },
    onFolderChange:function(){
    },
    init:function(){
        common.setupCSRFAjaxPost();
        $("#designstepstable").jqGrid({
            url:"/ajax_designsteps/"+testcaseform.testcaseID+"/fetch/",
            datatype: testcaseform.getDataType(),
            colModel:testcaseform.designstepstable.colModel,
            colNames:testcaseform.designstepstable.colNames,
            jsonReader : testcaseform.designstepstable.jsondataformat,
            pager:testcaseform.designstepstable.pager,
            pginput:false,
            pgbuttons: false,
            autowidth: true,
            height: 'auto',
            editurl: '/ajax_designsteps/'+testcaseform.testcaseID+"/edit/",
            caption: "Design Steps"
        });
        $("#designstepstable").jqGrid('navGrid',testcaseform.designstepstable.pager,
            testcaseform.designstepstable.parameters, //options
            {height:380,reloadAfterSubmit:true,afterSubmit:testcaseform.designstepstable.afterSubmit}, // edit options
            {height:380,reloadAfterSubmit:true,afterSubmit:testcaseform.designstepstable.afterSubmit}, // add options
            {reloadAfterSubmit:false}, // del options
            {} // search options
        );
        $("#uploadstable").jqGrid({
            url:"/ajax_testcase_uploads/"+testcaseform.testcaseID+"/fetch/",
            datatype:"json",
            colModel:testcaseform.uploadstable.colModel,
            colNames:testcaseform.uploadstable.colNames,
            jsonReader:testcaseform.uploadstable.jsondataformat,
            pager:testcaseform.uploadstable.pager,        
            pginput:false,
            pgbuttons:false,
            autowidth:true,
            height:'auto',
            editurl:'/ajax_testcase_uploads/'+testcaseform.testcaseID+"/edit/",
            caption:"Uploads"
        });
        $("#uploadstable").jqGrid('navGrid',testcaseform.uploadstable.pager,
            testcaseform.uploadstable.parameters, //options
            {height:380,reloadAfterSubmit:true,afterSubmit:testcaseform.uploadstable.afterSubmit}, // edit options
            {height:380,reloadAfterSubmit:true,afterSubmit:testcaseform.uploadstable.afterSubmit}, // add options
            {reloadAfterSubmit:false}, // del options
            {} // search options
        );
         if (clone == true){
            testcaseform.loadLocalDataForCloning();
        }

        $("#designstepstable").jqGrid('setGridParam',{datatype:"json"}); //make sure that the datatype is json after the initial load

        $( "#change-folder-dialog" ).dialog({
            autoOpen: false,
            height: 675,
            width: 370,
            modal: true,
            buttons: {
                "Select": function() {
                    var node = $("#root").dynatree("getActiveNode");
                    $( "#folder_name" ).text(node.data.title + " (after you submit this form)");
                    $( "#id_folder" ).val(node.data.key);
                    $( this ).dialog( "close" );
                },
                Cancel: function() {
                    $( this ).dialog( "close" );
                }
            },
            close: function() {
            }
        });
        $( "#change-folder-button" ) .click(function(event) { event.preventDefault(); $( "#change-folder-dialog" ).dialog( "open" ); });
    },
    required_fields :['name','enabled','is_automated','author','folder'],
    validate: function () {
        var designstepIds = $('#designstepstable').jqGrid('getDataIDs');
        $('<input />').attr('type', 'hidden')
            .attr('name', 'designsteplist')
            .attr('value', designstepIds)
            .appendTo('#Form');
        var uploadIds = $('#uploadstable').jqGrid('getDataIDs');
        $('<input />').attr('type', 'hidden')
            .attr('name', 'uploadlist')
            .attr('value', uploadIds)
            .appendTo('#Form');
        var validateForm = common.validateForm(testcaseform.required_fields);
        if (!validateForm){
            $('html, body').animate({ scrollTop: 0 }, 0);
            $("#invalid_form").show(); 
        }
        return validateForm;
    },
    makeRequired:function () {
        common.makeRequiredLabel(testcaseform.required_fields);
    }
}
$(function(){
    testcaseform.init();
    foldertree.initialize(testcaseform.onFolderChange);
    testcaseform.makeRequired();
})
