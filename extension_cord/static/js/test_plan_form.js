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
var createPlan = {
    required_fields:['name','creator','enabled', 'start_date'],
    initialize:function(){
        $(".dates input").datepicker();
        common.makeRequiredLabel(createPlan.required_fields);
        $('[rel=tooltip]').tooltip();

    },
    //Validate Test Plan Form
    validate:function () {
        // this is in common.js
        var validateForm = common.validateForm(createPlan.required_fields);
        if (!validateForm){
            $('html, body').animate({ scrollTop: 0 }, 0);
            $("#invalid_form").show(); 
        }
        return validateForm;
    },
};

$(function(){
    createPlan.initialize();
});






