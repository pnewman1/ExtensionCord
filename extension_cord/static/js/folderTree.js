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
var state = {};
var foldertree = {
    ROOT_NODE_FAKE_KEY:-100,
    folderName:"Root",

    getActiveKey:function () {
        var node = $("#root").dynatree("getActiveNode");
        var key = foldertree.ROOT_NODE_FAKE_KEY;
        if (node !== null) {
            key = node.data.key;
        }
        return key;
    },

    deleteFolderClicked:function () {
        $("#delete-folder").dialog( "open" );
    },

    updateTips:function ( t ) {
        $(".validateTips").text( t ).addClass( "ui-state-highlight" );
        setTimeout(function() {
            $(".validateTips").removeClass( "ui-state-highlight", 1500 );
        }, 500 );
    },

    checkLength:function ( o, n, min, max ) {
        if ( o.val().length > max || o.val().length < min ) {
            o.addClass( "ui-state-error" );
            foldertree.updateTips( "Length of " + n + " must be between " +
                                   min + " and " + max + "." );
            return false;
        } else {
            return true;
        }
    },

    initialize:function ( pageCallback ) {
        
        allFields = $( [] ).add( $("#newfoldername"), $("#addtoroot") );
        
        $("#delete-folder").dialog({
            autoOpen:false,
            height:300,
            width:350,
            modal:true,
            
            open: function( event, ui ){	
				$(".validateTips").empty();
                var node = $("#root").dynatree("getActiveNode");
				foldertree.updateTips("Are you sure you want to delete folder " + node.data.title + "?");
            },
            
            buttons:{
                "Confirm":function(){
					
                    var node = $("#root").dynatree("getActiveNode");
                    var dataString = '&key='+ node.data.key;
                    
                    $.ajax({
                        type:"GET",
                        url:"/ajax_deletefolder/",
                        dataType:"json",
                        data:dataString,
                        cache:false,
                        success:function(data){
                            if (data["deleted"]){
                                node.remove();
                                common.fireAlert(data["message"], "alert-success");
                            }
                            else{
                                $("#dfolder").addClass("ui-state-error");
                                foldertree.updateTips("Unable to delete the folder");
                                common.fireAlert(data["message"], "alert-error");
                            }
                        }
                    });
                    $( this ).dialog( "close" );
                },
                "Cancel": function() {
                    $( this ).dialog( "close" );
                }
            },
            close: function(){}
        });

        $("#rename-folder").dialog({
            autoOpen:false,
            height:300,
            width:350,
            modal:true,
            
            open: function( event, ui ){	
				$(".validateTips").empty();
                var node = $("#root").dynatree("getActiveNode");
				foldertree.updateTips("Are you sure you want to rename folder " + node.data.title + "?");
			    $("#renamefoldername").attr("value", node.data.title);
            },
            
            buttons:{
                "Confirm":function(){
					
                    var node = $("#root").dynatree("getActiveNode");
                    var folder_name = $("#renamefoldername").val();
                    var dataString = '&name='+folder_name+'&key='+ node.data.key;
                    
                    $.ajax({
                        type:"GET",
                        url:"/ajax_renamefolder/",
                        dataType:"json",
                        data:dataString,
                        cache:false,
                        success:function(data){
                            if (data["renamed"]){
                                node.data.title = folder_name;
                                node.render();
                                common.fireAlert(data["message"], "alert-success");
                            }
                            else{
                                $("#dfolder").addClass("ui-state-error");
                                foldertree.updateTips("Unable to rename the folder");
                                common.fireAlert(data["message"], "alert-error");
                            }
                        }
                    });
                    $( this ).dialog( "close" );
                },
                "Cancel": function() {
                    $( this ).dialog( "close" );
                }
            },
            close: function(){}
        });
        $( "#create-dialog" ).dialog({
			
            autoOpen: false,
            height: 300,
            width: 350,
            modal: true,

            open: function( event, ui ){	
				$(".validateTips").empty();
				foldertree.updateTips("Please enter the folder name to create:");
            },            
            
            
            buttons: {
                "Create Folder": function() {
                    var bValid = true;
                    allFields.removeClass( "ui-state-error" );

                    bValid = bValid && foldertree.checkLength( $("#newfoldername") , "username", 3, 150 );

                    if ( bValid ) {
                        var node = $("#root").dynatree("getActiveNode");
                        var folder_name = encodeURI( $("#newfoldername").val() );
                        
                        if ( (node !== null) && ( $("#addtoroot").attr("checked") !== "checked" ) ) {
                            var folder_parent = encodeURI(node.data.key);
                        } else {
                            node = $("#root").dynatree("getRoot");
                            var folder_parent = -9;
                        }

                        var dataString = '&name='+folder_name+'&parent='+folder_parent;
                        $.ajax({
                            type:"GET",
                            url:"/ajax_addfolder/",
                            dataType:"json",
                            data:dataString,
                            cache:false,
                            success:function(data){
                                if (data["added"]){
                                    node.addChild(data["child"]);
                                    node.expand();
                                    common.fireAlert(data["message"], data["alertType"]);
                                } else {
                                    $("#dfolder").addClass("ui-state-error");
                                    foldertree.updateTips("Unable to add the folder");
                                    common.fireAlert(data["message"], "alert-error");
                                }
                            }
                        });
                        $( this ).dialog( "close" );
                    }
                },
                Cancel: function() {
                    $( this ).dialog( "close" );
                }
            },
            close: function() {
                allFields.val( "" ).removeClass( "ui-state-error" );
            }
        });

        $( "#button-delete" ) .click(function(event) { event.preventDefault(); $( "#delete-folder" ).dialog( "open" ); });
        $( "#button-rename" ) .click(function(event) { event.preventDefault(); $( "#rename-folder" ).dialog( "open" ); });
        $(' #button-add') .click(function(event){ event.preventDefault(); $( "#create-dialog" ).dialog( "open" ); });

        $("#root").dynatree({
            children:foldertree.treechildren,
            persist: false,
            onActivate: function(node) {
                    var folderParents = new Array();
                    function createPath(node) {
                        if (node !== null) {
                            var title = node.data.title;
                            folderParents.push(title);
                        }
                    }

                    try {
                        node.visitParents(createPath,true);
                        folderParents = folderParents.reverse();
                        foldertree.folderName = folderParents[1];
                        if(folderParents.length > 2){ 
                            foldertree.folderName += " // " + folderParents[folderParents.length-1];
                        }
                        
                    }
                    catch(e) {
                        foldertree.folderName = "Root";
                    }

                    var node = $("#root").dynatree("getActiveNode");

                    if (state.planid && !state.add) {
                        paramMap = { key: node.data.key, testplan_id: state.planid };
                    } else {
                        paramMap = { key: node.data.key };
                    }
                    $.when(
                        $.ajax({
                            type:"GET",
                            url:"/ajax_folders/",
                            dataType:"json",
                            data:paramMap,
                            cache:false,
                            success:function(childJson){
                                if (node.countChildren() <= 1){
                                    node.addChild(childJson.node_list);
                                }
                                pageCallback.call(this);
                            }
                        })
                    ).done(
                        function() {
                            node.expand(true);

                            //this is a hacky workaround that will be improved upon sooner or later
                            if (typeof testcase !== 'undefined'){
                                pageCallback.call(this);
                            }
                        }
                    );
            },

            onRender: function(node, nodeSpan) {
                var nodekey=node.data.key.toString();
                if (nodekey.indexOf("hack") !== -1) {
                    $(nodeSpan).css("display", "none");
                }
            },

            onDeactivate:function (node){
                node.expand(false);
            }
        });
        
        // get potential starting node from querystring
        var urlkey = $.getUrlVar('key') || foldertree.ROOT_NODE_FAKE_KEY;
        
        if (state.planid && !state.add) {
            paramMap = { key: urlkey, mode: "all", testplan_id: state.planid };
        } else {
            paramMap = { key: urlkey, mode: "all" };
        }

        $.ajax({
            type:"GET",
            url:"/ajax_folders/",
            dataType:"json",
            data:paramMap,
            cache:false,
            success:foldertree.buildFromLeaf
        });
    },

    buildFromLeaf: function(childJson) {
        foldertree.buildFromLeafHelper(childJson);
        $("#root").dynatree("getTree").activateKey(childJson.id);
    },

    buildFromLeafHelper: function(childJson) {
        if(!childJson.parent_id) {
            $("#root").dynatree("getRoot").addChild(childJson.node_list);
        } else {
            paramMap = { key:childJson.parent_id };
            if(childJson.testplan_id) {
                paramMap.testplan_id = state.planid;
            }
            $.ajax({
                async:false,
                type:"GET",
                url:"/ajax_folders/",
                dataType:"json",
                data:paramMap,
                cache:false,
                success:function(data) {
                    foldertree.buildFromLeafHelper(data);
                    var node = $("#root").dynatree("getTree").selectKey(childJson.id.toString());
                    node.addChild(childJson.node_list);
                }
            });
        }
    }
};
