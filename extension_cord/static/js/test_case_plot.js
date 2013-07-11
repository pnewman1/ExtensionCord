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
/*
 For instructions on how to use the API of jqplot or how it looks like, here are some links:
 examples: http://www.jqplot.com/tests/
 api doc: http://www.jqplot.com/docs/files/usage-txt.html
 */
var casePlot = {
    XAXIS_TICK_INTERVAL: '1 week',
    createGraph: function (pass_list, fail_list, mindate, maxdate) {
        if (pass_list.length === 0){
            pass_list = [[null]];
        }
        if (fail_list.length === 0){
            fail_list = [[null]];
        }

        var yAxisTickInterval = 1;
        if (pass_list.length > 14 || fail_list.length>14){
            yAxisTickInterval = 10;
        }
        if (pass_list.length > 60 || fail_list.length>60){
            yAxisTickInterval = 50;
        }

        options = {
            title:{
                text:"Pass/Fail"
            },
            // uncomment next line for some pretty animations!
            //animate: !$.jqplot.use_excanvas,
            series:[
                { label:"Daily Pass Count", color:"#00ff01", markerOptions:{style:'filledSquare'} },
                { label:"Daily Fail Count", color:"#ff8000", markerOptions:{style:'circle'} },
            ],

            axes:{
                xaxis:{
                    renderer:$.jqplot.DateAxisRenderer,
                    tickOptions:{formatString:'%b %#d, %y'},
                    min:Number(mindate),
                    max:Number(maxdate),
                    tickInterval:casePlot.XAXIS_TICK_INTERVAL
                },
                yaxis:{
                    label:'Count',
                    min:0,
                    tickInterval:yAxisTickInterval
                },
            },

            legend:{
                show:true,
                placement:'outside',
            },

            highlighter:{
                show:true,
                sizeAdjust:7.5,
                formatString:'%s: %2$d'
            },
            cursor:{
                show:false
            }
        }
 //       try{
        $.jqplot("plot", [pass_list, fail_list], options);
 //       }catch(err){
//            if (err instanceof TypeError){
        //          $.jqplot('plot', [[null]], function() {  });
        //     }
        //     else{
        //         throw new Error( 'createGraph(): Invalid arguments passed to jqplot api')
        //     }
        // }
    },

}


$(document).ready(function () {
    casePlot.createGraph(pass_list, fail_list, mindate, maxdate);
})
