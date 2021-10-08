


function gd(year, month, day) {
    return new Date(year, month - 1, day).getTime();
}


function init_flot_chart() {

    if (typeof ($.plot) === 'undefined') { return; }

    console.log('init_flot_chart');
    var randNum = function () {
        return (Math.floor(Math.random() * (1 + 40 - 20))) + 20;
    };

    var arr_data1 = [
        [gd(2012, 1, 1), 17],
        [gd(2012, 1, 2), 74],
        [gd(2012, 1, 3), 6],
        [gd(2012, 1, 4), 39],
        [gd(2012, 1, 5), 20],
        [gd(2012, 1, 6), 85],
        [gd(2012, 1, 7), 7]
    ];

    var arr_data2 = [
        [gd(2012, 1, 1), 82],
        [gd(2012, 1, 2), 23],
        [gd(2012, 1, 3), 66],
        [gd(2012, 1, 4), 9],
        [gd(2012, 1, 5), 119],
        [gd(2012, 1, 6), 6],
        [gd(2012, 1, 7), 9]
    ];

    var arr_data3 = [
        [0, 1],
        [1, 9],
        [2, 6],
        [3, 10],
        [4, 5],
        [5, 17],
        [6, 6],
        [7, 10],
        [8, 7],
        [9, 11],
        [10, 35],
        [11, 9],
        [12, 12],
        [13, 5],
        [14, 3],
        [15, 4],
        [16, 9]
    ];

    var chart_plot_02_data = [];

    var chart_plot_03_data = [
        [0, 1],
        [1, 9],
        [2, 6],
        [3, 10],
        [4, 5],
        [5, 17],
        [6, 6],
        [7, 10],
        [8, 7],
        [9, 11],
        [10, 35],
        [11, 9],
        [12, 12],
        [13, 5],
        [14, 3],
        [15, 4],
        [16, 9]
    ];


    for (var i = 0; i < 30; i++) {
        chart_plot_02_data.push([new Date(Date.today().add(i).days()).getTime(), randNum() + i + i + 10]);
    }


    var chart_plot_01_settings = {
        series: {
            lines: {
                show: false,
                fill: true
            },
            splines: {
                show: true,
                tension: 0.4,
                lineWidth: 1,
                fill: 0.4
            },
            points: {
                radius: 0,
                show: true
            },
            shadowSize: 2
        },
        grid: {
            verticalLines: true,
            hoverable: true,
            clickable: true,
            tickColor: "#d5d5d5",
            borderWidth: 1,
            color: '#fff'
        },
        colors: ["rgba(38, 185, 154, 0.38)", "rgba(3, 88, 106, 0.38)"],
        xaxis: {
            tickColor: "rgba(51, 51, 51, 0.06)",
            mode: "time",
            tickSize: [1, "day"],
            //tickLength: 10,
            axisLabel: "Date",
            axisLabelUseCanvas: true,
            axisLabelFontSizePixels: 12,
            axisLabelFontFamily: 'Verdana, Arial',
            axisLabelPadding: 10
        },
        yaxis: {
            ticks: 8,
            tickColor: "rgba(51, 51, 51, 0.06)",
        },
        tooltip: false
    }

    var chart_plot_02_settings = {
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
        series: {
            lines: {
                show: true,
                fill: true,
                lineWidth: 2,
                steps: false
            },
            points: {
                show: true,
                radius: 4.5,
                symbol: "circle",
                lineWidth: 3.0
            }
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
        colors: ['#96CA59', '#3F97EB', '#72c380', '#6f7a8a', '#f7cb38', '#5a8022', '#2c7282'],
        shadowSize: 0,
        tooltip: true,
        tooltipOpts: {
            content: "%s: %y.0",
            xDateFormat: "%d/%m",
            shifts: {
                x: -30,
                y: -50
            },
            defaultTheme: false
        },
        yaxis: {
            min: 0
        },
        xaxis: {
            mode: "time",
            minTickSize: [1, "day"],
            timeformat: "%d/%m/%y",
            min: chart_plot_02_data[0][0],
            max: chart_plot_02_data[20][0]
        }
    };

    var chart_plot_03_settings = {
        series: {
            curvedLines: {
                apply: true,
                active: true,
                monotonicFit: true
            }
        },
        colors: ["#26B99A"],
        grid: {
            borderWidth: {
                top: 0,
                right: 0,
                bottom: 1,
                left: 1
            },
            borderColor: {
                bottom: "#7F8790",
                left: "#7F8790"
            }
        }
    };


    if ($("#chart_plot_01").length) {
        console.log('Plot1');

        $.plot($("#chart_plot_01"), [arr_data1, arr_data2], chart_plot_01_settings);
    }


    if ($("#chart_plot_02").length) {
        console.log('Plot2');

        $.plot($("#chart_plot_02"),
            [{
                label: "Email Sent",
                data: chart_plot_02_data,
                lines: {
                    fillColor: "rgba(150, 202, 89, 0.12)"
                },
                points: {
                    fillColor: "#fff"
                }
            }], chart_plot_02_settings);

    }

    if ($("#chart_plot_03").length) {
        console.log('Plot3');


        $.plot($("#chart_plot_03"), [{
            label: "Registrations",
            data: chart_plot_03_data,
            lines: {
                fillColor: "rgba(150, 202, 89, 0.12)"
            },
            points: {
                fillColor: "#fff"
            }
        }], chart_plot_03_settings);

    };

}
















$(document).ready(function () {

    // like and unlike click

    accordion_link = false;
    like_link = false;
    save_link = false;
    load_modal = true;
    init_flot_chart();

    if ($("#delete-modal").length){
        removeModal = new bootstrap.Modal($("#delete-modal")[0], {});
    }
    $('.accordion-button').click(function (e) {
        if (accordion_link === true){
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
            beforeSend: function(){
                accordion_link = true;
            },
            complete: function(){
                accordion_link = false;
            },
            success: function (data) {
                // console.log(data)
                // console.log(id)
                accordion_link = false;
                h2_obj.parent().append('<div id="flush-collapse_' + question_id + '" class="accordion-collapse collapse border border-1 rounded mb-3"' +
                    'aria-labelledby="flush-heading_' + question_id + '" data-bs-parent="#accordionFlushQuestion">')
                $('#flush-collapse_' + question_id).append('<div class="accordion-head">' +
                    '<div class="accordion-head-info">' +
                    '</div>' +
                    '</div>'
                )
                accordion_collapse = $('#flush-collapse_' + question_id);
                $('#flush-collapse_' + question_id).find('.accordion-head').append('<div class="float-end text-muted">ID:'+question_id + '</div> ')
                head_info = $('#flush-collapse_' + question_id).find(".accordion-head-info")
                if (!data.update_at) {
                    head_info.append('Respondido ' + data.answered_at)
                }
                else {
                    head_info.append('Atualizado ' + data.update_at)
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
                data.tags.forEach(item => accordion_collapse.find('.accordion-footer').append('<span class="badge bg-secondary">' +item+'</span>\n'))

                $(target).collapse();
                
            },
            error: function(data){
                if (data.status == 404){
                    if (!button_accordion.hasClass('bg-danger')){
                        button_accordion.addClass('bg-danger')
                        button_accordion.append('<span class="badge bg-secondary mx-3">Não encontrado</span>\n')

                    }
                }
                if (data.status == 500){
                    if (!button_accordion.hasClass('bg-danger')){
                        button_accordion.addClass('bg-danger')
                        button_accordion.append('<span class="badge bg-secondary mx-3">Erro no servidor</span>\n')

                    }
                }
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
        beforeSend: function(){
            like_link = false;
        },
        complete: function(){
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
    if (save_link === true){
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
        beforeSend: function(){
            save_link = true;
        },
        complete: function(){
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

$(document).on('click', ".remove", function(e){
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

$(document).on('click', "#confirm-delete", function(e){
    bt_confirm_delete = $("#" + e.currentTarget.id)
    confirm_delete_href = bt_confirm_delete.attr('href')
    
    $.ajax({
        url:confirm_delete_href,
        type:'post',
        data: {confirm: true},
        dataType: 'json',
        headers: {
            "X-CSRFToken": $CSRF_TOKEN,
        },
        success: function(data){
            // console.log(data);
            // var teste = new bootstrap.Modal(document.getElementById("delete-modal"), {});
            removeModal.toggle();
            if (data.status === 'success'){
                // $('.table').find("#"+data.id).remove()
            }
            // console.log(data)
        }
    });
    // console.log(confirm_delete_href)

});

$("#delete-modal").on("show.bs.modal", function(e) {
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
    if(iFrameID) {
          // here you can make the height, I delete it first, then I make it again
          iFrameID.height = "";
          iFrameID.height = iFrameID.contentWindow.document.body.scrollHeight + "px";
    }   
}














