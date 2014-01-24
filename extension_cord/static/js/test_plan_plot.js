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
var planPlot = {
    XAXIS_TICK_INTERVAL: '1 week',
    options : {
            title:{
                text:"Pass/Fail"
            },
            // uncomment next line for some pretty animations!
            //animate: !$.jqplot.use_excanvas,
            series:[
                { label:"Daily Pass Count", color:"#00ff01", markerOptions:{style:'filledSquare'} },
                { label:"Aggregate Pass Count", color:"#0000ff", markerOptions:{style:'circle'}},
                { label:"Daily Fail Count", color:"#ff0000", markerOptions:{style:'circle'} },
                { label:"Aggregate Fail Count", color:"#ff8000", markerOptions:{style:'filledSquare'}},
            ],

            axes:{
                xaxis:{
                    renderer:$.jqplot.DateAxisRenderer,
                    tickOptions:{formatString:'%b %#d, %y'},
                },
                yaxis:{
                    label:'Count',
                    min:0,
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
    },
    createGraph: function (pass_list, agg_pass_list, fail_list, agg_fail_list, mindate, maxdate) {
        if (pass_list.length === 0){
            pass_list = [[null]];
        }
        if (fail_list.length === 0){
            fail_list = [[null]];
        }

        this.setJqplotOptions(pass_list, fail_list, mindate, maxdate);
        $.jqplot("plot", [pass_list, agg_pass_list, fail_list, agg_fail_list], this.options);
    },
    setJqplotOptions: function(pass_list, fail_list, mindate, maxdate){

        this.options.axes.xaxis.min = Number(mindate);
        this.options.axes.xaxis.max = Number(maxdate);
        this.options.axes.xaxis.tickInterval = this.XAXIS_TICK_INTERVAL;
        this.setYAxisTickInterval(max_results_count);

    },
    setYAxisTickInterval: function(elementCount){

        if (elementCount < 10){
            this.options.axes.yaxis.tickInterval = 1;

        } else if (elementCount > 10 && elementCount < 100){
            this.options.axes.yaxis.tickInterval = 10;

        } else if (elementCount > 100 && elementCount < 1000){
            this.options.axes.yaxis.tickInterval = 50;

        } else if (elementCount > 1000){
            this.options.axes.yaxis.tickInterval = 500;
        }
    }
}

$(document).ready(function () {
    var plot = Object.create(planPlot);
    plot.createGraph(pass_list, agg_pass_list, fail_list, agg_fail_list, mindate, maxdate);
    $("#tree-table").treetable({ expandable: true });
    console.log($("#tree-table").treetable("node", "3").children);
    $("#tree-table tbody").on("mousedown", "tr", function() {
      $(".selected").not(this).removeClass("selected");
      $(this).toggleClass("selected");
    });

})

