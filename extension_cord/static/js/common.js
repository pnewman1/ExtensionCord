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
var BindArg = function(i) {
    this.index = i;
};

var expandArgs = function(args, arguments, start) {
    if (start == null) start = 0;
    for (var i=0; i < args.length; ++i) {
        if (args[i] && args[i].constructor == BindArg) {
            var arg = args[i].index;
            if (arg > 0 && arg <= arguments.length) {
                args[i] = arguments[arg - 1];
                if (arg > start)
                    start = arg;
            } else {
                args[i] = null;
            }
        }
    }
    return start;
};
var bind = function(f)
{
    if (f === null) return function() {};
    var args = Array.prototype.slice.call(arguments);
    args.shift();
    return function () {
        var argsCopy = args.slice(0);
        var start = expandArgs(argsCopy, arguments);
        return f.apply(null, argsCopy.concat(Array.prototype.slice.call(arguments, start)));
    };
};

$.extend({
  getUrlVars: function(){
    var vars = [], hash;
    var hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
    for(var i = 0; i < hashes.length; i++)
    {
      hash = hashes[i].split('=');
      vars.push(hash[0]);
      vars[hash[0]] = hash[1];
    }
    return vars;
  },
  getUrlVar: function(name){
    return $.getUrlVars()[name];
  }
});

var common={
    csrfSafeMethod:function (method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    },
    sameOrigin:function(url) {
        // test that a given url is a same-origin URL
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    },
    getCookie:function(name) {
            var cookieValue = null;
            if (document.cookie && document.cookie != '') {
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = jQuery.trim(cookies[i]);
                    // Does this cookie string begin with the name we want?
                    if (cookie.substring(0, name.length + 1) == (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
    },
    setupCSRFAjaxPost: function(){
        var csrftoken = common.getCookie('csrftoken');

        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!common.csrfSafeMethod(settings.type) && common.sameOrigin(settings.url)) {
                    // Send the token to same-origin, relative URLs only.
                    // Send the token only if the method warrants CSRF protection
                    // Using the CSRFToken value acquired earlier
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });
    },

    updatePaginate:function (data){
        var has_prev = data['has_prev'];
        var has_next = data['has_next'];
        var start_index = data['start_index'];
        var end_index = data['end_index'];
        var counts = data['total_count'];
        var curr_page = data['curr_page'];
        // innerString is going to be the complete HTML code which will create the pagination buttons on the bottom of the table

        // create the back arrow button.
        // if your at the first page, the back arrow button should be disabled
        if (has_prev) {
            $("#prevpage").val(curr_page-1);
            $("#prevpage").toggleClass("disabled", false);
        } else { //back arrow button enabled
            $("#prevpage").toggleClass("disabled", true);
        }

        var currString="";
        // create the current greyed out page button
        if (counts == 0){
            currString = "0";
        }
        else{
            currString = String(start_index) + '-' + String(end_index)+' of '+String(counts);
        }

        $("#currpage a").html(currString);

        // create the forward arrow button.
        // if your at the last page, the forward arrow button should be disabled
        if (has_next) {
            $("#nextpage").val(curr_page+1);
            $("#nextpage").toggleClass("disabled",false);
        } else {
            $("#nextpage").toggleClass("disabled",true);
        }
    },


    verifyTable:function (table_id) {

        var selector = "#" + table_id + " tbody";
        // check if "tr" exists in the html, which identifies if any rows exist in the tbody
        // if no rows exist in the table, alert and error
        if ( $(selector).html().indexOf("tr") == -1) {
            alert( "The table is empty, please add to it before submitting" )
            return false;
        }

        // if number of selected inputs is less than half than the number of selections, the user hasn't checked all option
        // i.e. every option has 2 choices, but only 1 can be selected. so half the options must be selected to be a valid form
        var required_checks = $(selector+" input").length / 2
        var checked = $(selector+" input:checked").length
        if (checked < required_checks ){
            alert("Some radio selections weren't selected. Please make sure they are all checked or remove them from the table.")
            return false;
        }
        return true;
    },

    // validates a form based on required_array
    // if the field is left blank it makes the label red and redirects user to top of the page
    validateForm:function (required_array){
        var name;
        var field;
        var valid = true;
        // for each field in required_array check to make sure that it isn't empty in the form
        // if it, make it red and return the user to the top of the page
        for (index in required_array) {
            name = required_array[index];
            label_id = "label_"+name
            field = document.forms["Form"][name].value;
            if (field == "" || field==null) {
                valid = valid&&false;
                document.getElementById(label_id).style.color="red";
            }

            else { // else the field should be black if the user has entered it correctly
                valid = valid&&true;
                document.getElementById(label_id).style.color="black";
            }
        }
        return valid;
    },
    timeout:null,
    closeAlert:function(alertType){
        alertType = typeof alertType !== 'undefined' ? alertType : "alert-success";
        $("#alert p").empty();
        $("#alert").removeClass(alertType);
        $("#alert").hide();
    },
    fireAlert:function(message, alertType){
        var a = common.timeout&&clearTimeout(common.timeout);
        alertType = typeof alertType !== 'undefined' ? alertType : "alert-success";
        $("#alert").addClass(alertType);
        $("#alert p").empty();
        $("#alert p").append(message);
        $("#alert").show();
        common.timeout = setTimeout(function(){
            common.closeAlert();
        },5000);
    },

    // makes required fields in a form bold with an asterisk
    // required_array is a list of required names of fields
    makeRequiredLabel:function (required_array){
        var name;
        // for each field in required_array check to make sure that it isn't empty in the form
        // if it, make it red and return the user to the top of the page
        for (index in required_array) {
            name = required_array[index];
            label_id = "label_"+name
            document.getElementById(label_id).innerHTML = document.getElementById(label_id).innerHTML.bold()
        }
    },
    hasDesc:function(desc) { 
        return (desc && desc != 'None' && $.trim(desc).length); 
    },
    getNameTD:function(tcPk, tcName, desc) {
        var row = '<td width="100%">';
        if(common.hasDesc(desc)) {
            row += '<i id="showdetail_link_' + tcPk + '" style="margin-right:10px;" class="icon-plus"/>'
            + '<i id="hidedetail_link_' + tcPk + '" style="margin-right:10px;display:none;" class="icon-minus"/>';
        } else {
            row += '<i style="margin-right:10px;" class="icon-minus"/>';
        }
        row += '<a href="/test_case/' + tcPk + '/">' + tcName + '</a>';
        if(common.hasDesc(desc)) {
            row += '<div id="description_' + tcPk + '" style="display:none;margin-left:40px;">' + desc + '</div>';
        }
        row += '</td>';
        return row;
    },
    addDescShowHideHandlers:function(tcPk, desc) {
        if(common.hasDesc(desc)) {
            var showdelegate = bind(function(i, event) {
                event.preventDefault();
                $("#showdetail_link_"+i).hide();
                $("#hidedetail_link_"+i).show();
                $("#description_"+i).fadeIn();
                return false; 
            },tcPk);

            var hidedelegate = bind(function(i, event) {
                event.preventDefault();
                $("#hidedetail_link_"+i).hide();
                $("#showdetail_link_"+i).show();
                $("#description_"+i).hide();
                return false; 
            },tcPk);

            $('#showdetail_link_'+tcPk).click(showdelegate);
            $('#hidedetail_link_'+tcPk).click(hidedelegate);
        }
    },
    makeRowsWithData:function (testcases) {

        $("#id_table").find("tr:gt(0)").remove(); //removes all rows (except head)

        // json data passed in from server must be "eval'ed"
        var tests = eval( "("+testcases+")" );
        // iterate through each testcase
        for (index in tests) {
            var tcName = tests[index]['fields']['name'];
            if (tests[index]['fields']['enabled'] == false){
                tcName += ' (Disabled)';
            }

            var tcPk = tests[index]['pk'];
            var desc = tests[index]['fields']['description'];
            var newRow = '<tr>'
                + '<td><input type="checkbox" value='+ tcPk +'></input></td>'
                + '<td>' + tcPk + '</td>';
                
            newRow += common.getNameTD(tcPk, tcName, desc);

            if (tests[index]['fields']['priority']){
                newRow += '<td>' + tests[index]['fields']['design_steps'].length + '</td>'
                    + '<td>' + tests[index]['fields']['priority'] + '</td>'
                    + '</tr>';
            }
            else
            {
                newRow += '<td>' + tests[index]['fields']['design_steps'].length + '</td>'
                    + '<td></td>'
                    + '</tr>';
             
            }

            $('#id_table > tbody:last').append(newRow);

            common.addDescShowHideHandlers(tcPk, desc);
        }
    }
}
