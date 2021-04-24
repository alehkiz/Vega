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
    end_visit = moment().format('DD-MM-YYYY')
    accordion_link = false;
    like_link = false;
    save_link = false;
    load_modal = true;
    config();
    visit_chart(start_visit, end_visit);
    // init_charts();
    init_chart_doughnut();
    init_daterangepicker();

    if ($("#delete-modal").length) {
        removeModal = new bootstrap.Modal($("#delete-modal")[0], {});
    }

    if ($(".progress .progress-bar")[0]) {
        $('.progress .progress-bar').progressbar();
    }
    $('.accordion-button').click(function (e) {
        if (accordion_link === true) {
            return false;
        }
        if ($($(this).attr('data-bs-target')).length > 0) {
            return false;
        }
        h2_obj = $(this).parent();
        button_accordion = $("#" + this.id);
        // console.log(this.id);
        var id = h2_obj.attr('id');
        var split_id = id.split('_');
        var question_id = split_id[1];
        var target = $(this).attr('data-bs-target');
        var url = button_accordion.attr('href');

        $.ajax({
            url: url,
            type: 'post',
            dataType: 'json',
            // async: false,
            headers: {
                'X-CSRFToken': $CSRF_TOKEN
            },
            beforeSend: function () {
                accordion_link = true;
            },
            complete: function () {
                accordion_link = false;
            },
            success: function (data) {
                // console.log(data)
                // console.log(id)
                accordion_link = false;
                h2_obj.parent().append('<div id="flush-collapse_' + question_id + '" class="accordion-collapse collapse accordion-border"' +
                    'aria-labelledby="flush-heading_' + question_id + '" data-bs-parent="#accordionFlushQuestion">')
                $('#flush-collapse_' + question_id).append('<div class="accordion-head">' +
                    '<div class="accordion-head-info">' +
                    '</div>' +
                    '</div>'
                )
                accordion_collapse = $('#flush-collapse_' + question_id);
                head_info = $('#flush-collapse_' + question_id).find(".accordion-head-info")
                head_info.append(question_id + ' ')
                if (!data.update_at || !data.updater) {
                    head_info.append('Criado ' + data.create_time_elapsed + ' por ' + data.author)
                }
                else {
                    head_info.append('Atualizado ' + data.update_at + ' por ' + data.updater)
                }

                accordion_collapse.append('<div class="accordion-head-buttons"></div>\n')
                accordion_buttons = accordion_collapse.find('.accordion-head-buttons')
                if (data.url_edit !== undefined) {
                    accordion_buttons.append('<a class="edit text-decoration-none" id="edit_' + question_id + '"' +
                        'href="' + data.url_edit + '">' +
                        '<i class="fas fa-edit"></i>' +
                        '</a>\n');
                }

                if (data.like_action !== undefined) {
                    like_icon = data.like_action == 'like' ? 'far' : 'fas';
                    accordion_buttons.append(
                        '<a class="like-button ' + data.like_action + '" id="like_' + question_id + '"' +
                        'href="' + data.url_like + '">' +
                        '<i class="' + like_icon + ' fa-heart"></i></a>\n'
                    );
                }
                if (data.save_action !== undefined) {
                    save_icon = data.save_action == 'save' ? 'far' : 'fas';
                    accordion_buttons.append(
                        '<a class="save-button ' + data.save_action + '" id="save_' + question_id + '"' +
                        'href="' + data.url_save + '">' +
                        '<i class="' + save_icon + ' fa-save"></i></a>\n'
                    );
                }


                accordion_collapse.append(
                    '<div class="accordion-body">' + data.answer + '</div>'
                );
                accordion_collapse.append(
                    '<div class="accordion-footer"></div>'
                );

                // $('.accordion-footer').append('<span class="badge bg-secondary">' +item+'</span>')
                data.tags.forEach(item => $('.accordion-footer').append('<span class="badge bg-secondary">' + item + '</span>\n'))

                $(target).collapse();

            },
            error: function (data) {
                accordion_link = false;
            }
        });
        return false;
    });


});

$(document).on('click', ".like, .unlike", function (e) {
    if (like_link === true) {
        return false;
    }
    var link = $(this)
    var id = this.id;
    var split_id = id.split("_");
    var action = split_id[0];
    var link_href = $(this).attr('href');
    like_link = true;

    // $(this).attr('href', '#');
    var question_id = split_id[1];

    if ($(this).hasClass('like')) {
        action = 'like';
        invert = 'unlike';
    }
    else if ($(this).hasClass('unlike')) {
        action = 'unlike';
        invert = 'like'
    }
    else {
        action = false;
    }
    // AJAX Request
    $.ajax({
        url: link_href,
        type: 'post',
        data: { action: action },
        dataType: 'json',
        headers: {
            "X-CSRFToken": $CSRF_TOKEN,
        },
        beforeSend: function () {
            like_link = false;
        },
        complete: function () {
            like_link = false;
        },
        success: function (data) {
            $("#" + id).removeClass(action);
            $("#" + id).addClass(invert);
            i = $('#' + id).children();
            like_link = false
            i.toggleClass(function () {

                if ($(this).hasClass('fas')) {
                    $(this).removeClass('fas')
                    return 'far'
                } else {
                    $(this).removeClass('far')
                    return 'fas'
                }
            });
        },
        error: function (data) {
            // console.log('Erro');
            like_link = false;
        }
    });
    // link.attr('href', link_href);
    return false;
});



$(document).on('click', ".save, .unsave", function (e) {
    if (save_link === true) {
        return false;
    }
    save_link = true;
    var id = this.id;
    var split_id = id.split("_");
    var action = split_id[0];
    var question_id = split_id[1];
    if ($(this).hasClass('save')) {
        action = 'save';
        invert = 'unsave';
    }
    else if ($(this).hasClass('unsave')) {
        action = 'unsave';
        invert = 'save'
    }
    else {
        action = false;
    }
    // AJAX Request
    $.ajax({
        url: this.href,
        type: 'post',
        data: { action: action },
        dataType: 'json',
        headers: {
            "X-CSRFToken": $CSRF_TOKEN,
        },
        beforeSend: function () {
            save_link = true;
        },
        complete: function () {
            save_link = false;
        },
        success: function (data) {
            $("#" + id).removeClass(action);
            $("#" + id).addClass(invert);
            i = $('#' + id).children();
            save_link = false;
            i.toggleClass(function () {

                if ($(this).hasClass('fas')) {
                    $(this).removeClass('fas')
                    return 'far'
                } else {
                    $(this).removeClass('far')
                    return 'fas'
                }
            });
        },
        error: function (data) {
            // console.log('Erro');
            save_link = false;
        }
    });
    return false;
});

$(document).on('click', ".remove", function (e) {
    // e.preventDefault();
    // if (load_modal === false){
    //     return false
    // }
    // load_modal = false;

    // console.log(removeModal)

    remove_link = true;
    var remove_href = $(this).attr('href');
    remove_confirm = $("#delete-modal").find('.delete')
    // console.log(remove_confirm)
    remove_confirm.attr('href', remove_href)
    removeModal.show();

    // $.ajax({
    //     url: remove_href,
    //     type: 'post',
    //     data: {confirm: true},
    //     dataType: 'json',
    //     headers: {
    //         "X-CSRFToken": $CSRF_TOKEN,
    //     },
    //     beforeSend: function(){
    //         remove_link = false;
    //     },
    //     success: function(data){
    //         remove_link = true;

    //         console.log(data)
    //     }
    // });


});

$(document).on('click', "#confirm-delete", function (e) {
    bt_confirm_delete = $("#" + e.currentTarget.id)
    confirm_delete_href = bt_confirm_delete.attr('href')

    $.ajax({
        url: confirm_delete_href,
        type: 'post',
        data: { confirm: true },
        dataType: 'json',
        headers: {
            "X-CSRFToken": $CSRF_TOKEN,
        },
        success: function (data) {
            // console.log(data);
            // var teste = new bootstrap.Modal(document.getElementById("delete-modal"), {});
            removeModal.toggle();
            if (data.status === 'success') {
                $('.table').find("#" + data.id).remove()
            }
            // console.log(data)
        }
    });
    // console.log(confirm_delete_href)

});

$("#delete-modal").on("show.bs.modal", function (e) {
    // if (load_modal === false){
    //     e.preventDefault();
    // }
    // console.log(e.currentTarget.id)

    // e.preventDefault()
    var link = $(e.relatedTarget);
    // console.log(e)    
    // var myModal = new bootstrap.Modal(document.getElementById(e.currentTarget.id), {});
    // console.log(e.currentTarget.id)
    // console.log(myModal)
    // setTimeout(
    //     function() 
    //     {
    //       console.log('aqui')
    //     }, 5000);
    // $(this).find(".modal-body").load(link.attr("href"));
    // load_modal = false
    // myModal.show()
    // load_modal = true;
});

function iframeLoaded(frame_id) {
    var iFrameID = document.getElementById(frame_id.id);
    console.log('aqui')
    console.log(frame_id.id)
    console.log(iFrameID)
    if (iFrameID) {
        // here you can make the height, I delete it first, then I make it again
        iFrameID.height = "";
        iFrameID.height = iFrameID.contentWindow.document.body.scrollHeight + "px";
    }
}














