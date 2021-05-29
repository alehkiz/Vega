var tags_r;
var visits_interval;
var visit_data;
var data_visit;
var plot_visit;
var plt;
var chart_plot_02_data;
var arr_data2;
var visit_plot;

function config(){
    moment.locale('pt-br');
}

function init_chart_doughnut() {

    if (typeof (Chart) === 'undefined') { return; }


    console.log('Gráfico de pizza');

    tags_r = function () {
        var tmp = null;
        console.log('teste1')
        $.ajax({
            'async': false,
            'type': "GET",
            'global': false,
            'dataType': 'json',
            'url': urls.d_tags,
            // 'data': { 'request': "", 'target': 'arrange_url', 'method': 'method_target' },
            'success': function (data) {
                tmp = data;
            }
        });
        return tmp;
    }()

    if ($('.canvasDoughnut').length) {


        var chart_doughnut_settings = {
            type: 'pie',
            tooltipFillColor: "rgba(51, 51, 51, 0.55)",
            data: tags_r
            ,
            options: {
                legend: false,
                responsive: false
            }
        }

        $('.canvasDoughnut').each(function () {

            var chart_element = $(this);
            var chart_doughnut = new Chart(chart_element, chart_doughnut_settings);

        });
    }

    tile_info = $(".x_content").find('.tile_info')
    tags_sum = tags_r.datasets[0].data.reduce((a, b) => a + b, 0)
    if (tile_info.length) {
        console.log('teste')
        $.each(tags_r.labels, function (i, obj) {
            tile_info.append('<tr>' +
                '<td>' +
                '<p><i class="fa fa-square ' + tags_r.datasets[0].backgroundColor[i] + '"></i>' + tags_r.labels[i] + ' </p>' +
                '</td>' +
                '<td>' + ((tags_r.datasets[0].data[i] / tags_r.totalQuestions) * 100).toFixed(2) + '%</td>' +
                '</tr>')
        });

    }

}

function init_daterangepicker() {

    if (typeof ($.fn.daterangepicker) === 'undefined') { return; }
    console.log('init_daterangepicker');

    var cb = function (start, end, label) {
        console.log(start.toISOString(), end.toISOString(), label);
        $('#reportrange span').html(start.format('DD/MM/YYYY') + ' - ' + end.format('DD/MM/YYYY'));
    };

    var optionSet1 = {
        startDate: moment().subtract(29, 'days'),
        endDate: moment(),
        minDate: '01/01/2021',
        maxDate: '12/31/2030',
        dateLimit: {
            days: 60
        },
        showDropdowns: true,
        showWeekNumbers: true,
        timePicker: false,
        timePickerIncrement: 1,
        timePicker12Hour: true,
        ranges: {
            // 'Hoje': [moment(), moment()],
            // 'Ontem': [moment().subtract(1, 'days'), moment().subtract(1, 'days')],
            'Últimos 7 dias': [moment().subtract(6, 'days'), moment()],
            'Últimos 30 dias': [moment().subtract(29, 'days'), moment()],
            'Este mês': [moment().startOf('month'), moment().endOf('month')],
            'Útimo mês': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')]
        },
        opens: 'left',
        buttonClasses: ['btn btn-default'],
        applyClass: 'btn-small btn-primary',
        cancelClass: 'btn-small',
        format: 'MM/DD/YYYY',
        separator: ' para ',
        locale: {
            applyLabel: 'Enviar',
            cancelLabel: 'Limpar',
            fromLabel: 'De',
            toLabel: 'Para',
            customRangeLabel: 'Customizar',
            daysOfWeek: ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'],
            monthNames: ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'],
            firstDay: 1
        }
    };

    $('#reportrange span').html(start_visit + ' - ' + end_visit);
    $('#reportrange').daterangepicker(optionSet1, cb);
    $('#reportrange').on('show.daterangepicker', function () {
        console.log("show event fired");
    });
    $('#reportrange').on('hide.daterangepicker', function () {
        console.log("hide event fired");
    });
    $('#reportrange').on('apply.daterangepicker', function (ev, picker) {
        console.log("apply event fired, start/end dates are " + picker.startDate.format('MMMM D, YYYY') + " to " + picker.endDate.format('MMMM D, YYYY'));
        visit_chart(picker.startDate.format('DD-MM-YYYY'), picker.endDate.format('DD-MM-YYYY'))
        
    });
    $('#reportrange').on('cancel.daterangepicker', function (ev, picker) {
        console.log("cancel event fired");
    });
    $('#options1').click(function () {
        $('#reportrange').data('daterangepicker').setOptions(optionSet1, cb);
    });
    $('#options2').click(function () {
        $('#reportrange').data('daterangepicker').setOptions(optionSet2, cb);
    });
    $('#destroy').click(function () {
        $('#reportrange').data('daterangepicker').remove();
    });

}


function gd(year, month, day) {
    return new Date(year, month - 1, day).getTime();
}


function visit_chart(start, end) {

    if (typeof ($.plot) === 'undefined') { return; }

    console.log('init_flot_chart');
    var randNum = function () {
        return (Math.floor(Math.random() * (1 + 40 - 20))) + 20;
    };

    visits_interval = function () {
        var tmp = null;
        console.log('aqui')
        $.ajax({
            'async': false,
            'type': "POST",
            'global': false,
            headers: {
                "X-CSRFToken": $CSRF_TOKEN,
            },
            'dataType': 'json',
            'url': urls.d_visit_interval,
            // 'data': { 'year':2021, 'month': 4},
            'data': { 'start': start, 'end': end},
            'success': function (data) {
                tmp = data;
            },
            'error': function (data){
                console.log('Não foi possível recuperar dados de visitas');
            }
        });
        return tmp;
    }()


    visit_data = [];

    for (let key in visits_interval) {
        visit_data.push([new Date(visits_interval[key][0]).getTime(), parseInt(visits_interval[key][1])])
    }
    
    var chart_plot_01_settings = {
        series: {

            lines: {
                show: false,
                fill: true,
                lineWidth: 2,
                steps: false
            },
            splines: {
                show: true,
                tension: 0.4,
                lineWidth: 1,
                fill: 0.4
            },
            points: {
                radius: 2,
                show: true
            },
            shadowSize: 2
        },
        legend: {
            position: "ne",
            margin: [0, -25],
            noColumns: 0,
            labelBoxBorderColor: null,
            labelFormatter: function (label, series) {
                return label + '&nbsp;&nbsp;';
            },
            width: 40,
            height: 1
        },
        grid: {
            show: true,
            aboveData: true,
            color: "#3f3f3f",
            labelMargin: 10,
            axisMargin: 0,
            borderWidth: 0,
            borderColor: null,
            minBorderMargin: 5,
            clickable: true,
            hoverable: true,
            autoHighlight: true,
            mouseActiveRadius: 100
        },
        colors: ["orange", "blue"],
        xaxis: {
            tickColor: "rgba(51, 51, 51, 0.06)",
            tickLength: 10,
            axisLabel: "Date",
            axisLabelUseCanvas: true,
            axisLabelFontSizePixels: 12,
            axisLabelFontFamily: 'Verdana, Arial',
            axisLabelPadding: 10,
            mode: "time",
            minTickSize: [1, "day"],
            timeformat: "%d/%m/%y",
            min: visit_data[0][0],
            max: visit_data[visit_data.length-1][0],
            // mode: "categories"
        },
        yaxis: {
            ticks: 10,
            tickColor: "rgba(51, 51, 51, 0.06)"
        },
        tooltip: {
            show: true,
            content: "%x - %y acessos",
            xDateFormat: "%d/%m/%y",
        },
    }


 

    if ($("#chart_plot_01").length) {
        console.log('Plot1');

        visit_plot = $.plot($("#chart_plot_01"), [{
            // label: 'Acessos',
            data: visit_data
        }], chart_plot_01_settings);
    }
}
















$(document).ready(function () {

    // like and unlike click
    start_visit = moment().subtract(7, 'days').format('DD-MM-YYYY')
    end_visit = moment().add(1, 'days').format('DD-MM-YYYY')
    config();
    visit_chart(start_visit, end_visit);
    // init_charts();
    init_chart_doughnut();
    init_daterangepicker();

});
