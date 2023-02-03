$(document).ready(function () {

    // like and unlike click

    accordion_link = false;
    like_link = false;
    save_link = false;
    load_modal = true;

    if ($("#delete-modal").length) {
        removeModal = new bootstrap.Modal($("#delete-modal")[0], {});
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
                h2_obj.parent().append('<div id="flush-collapse_' + question_id + '" class="accordion-collapse collapse border border-1 rounded mb-3"' +
                    'aria-labelledby="flush-heading_' + question_id + '" data-bs-parent="#accordionFlushQuestion">')
                $('#flush-collapse_' + question_id).append('<div class="accordion-head">' +
                    '<div class="accordion-head-info">' +
                    '</div>' +
                    '</div>'
                )
                accordion_collapse = $('#flush-collapse_' + question_id);
                $('#flush-collapse_' + question_id).find('.accordion-head').append('<div class="float-end text-muted">ID:' + question_id + '</div> ')
                head_info = $('#flush-collapse_' + question_id).find(".accordion-head-info")
                if (!data.update_at) {
                    head_info.append('Respondido ' + data.answered_at + ' visualizado ' + data.views + ' vezes')
                } else {
                    head_info.append('Atualizado ' + data.update_at + ', visualizado ' + data.views + ' vezes')
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

                accordion_buttons.append(
                    '<a class="save-button" id="view_' + question_id + '"' +
                    'href="' + data.url_view + '" target="_blank">' +
                    '<i class="fas fa-eye"></i></a>\n'
                )


                accordion_collapse.append(
                    '<div class="accordion-body">' + data.answer + '</div>'
                );
                accordion_collapse.append(
                    '<div class="accordion-footer"></div>'
                );
                data.topics.forEach(function (element) {
                    if (element.includes('Retaguarda')) {
                        accordion_collapse.find('.accordion-footer').append('<span class="badge bg-primary ms-2 float-end">' + element + '</span>\n')
                    }
                    if (element.includes('SAC')) {
                        accordion_collapse.find('.accordion-footer').append('<span class="badge bg-success ms-2 float-end">' + element + '</span>\n')
                    }
                    if (element.includes('Linha de Frente')) {
                        accordion_collapse.find('.accordion-footer').append('<span class="badge ms-2 float-end" style="background-color: black;color: white;">' + element + '</span>\n')
                    }
                }
                );
                // $('.accordion-footer').append('<span class="badge bg-secondary">' +item+'</span>')
                data.tags.forEach(item => accordion_collapse.find('.accordion-footer').append('<span class="badge bg-secondary">' + item + '</span>\n'))

                $(target).collapse();

            },
            error: function (data) {
                if (data.status == 404) {
                    if (!button_accordion.hasClass('bg-danger')) {
                        button_accordion.addClass('bg-danger')
                        button_accordion.append('<span class="badge bg-secondary mx-3">Não encontrado</span>\n')

                    }
                }
                if (data.status == 500) {
                    if (!button_accordion.hasClass('bg-danger')) {
                        button_accordion.addClass('bg-danger')
                        button_accordion.append('<span class="badge bg-secondary mx-3">Erro no servidor</span>\n')

                    }
                }
                accordion_link = false;

            }
        });
        return false;
    });





    // h2_obj.parent().append('<div id="flush-collapse_' + question_id + '" class="accordion-collapse collapse border border-1 rounded mb-3"' +
    // 'aria-labelledby="flush-heading_' + question_id + '" data-bs-parent="#accordionFlushQuestion">')
    // $('#flush-collapse_' + question_id).append('<div class="accordion-head">' +
    //     '<div class="accordion-head-info">' +
    //     '</div>' +
    //     '</div>'
    // )
    var down = false;
    var notifications = $('.bell')

    // $('.bell').click(function (e) {
    //     console.log('clicado')
    //     var color = $(this).text();
    //     console.log("licado")
    //     if (down) {
    //         //$('#notification_box').css('height', '0px');
    //         // $('#notification_box').css('opacity', '0');
    //         // $('#notification_box').css('display', 'none');
    //         // $('#notification_box').css('visibility', 'hidden');
    //         down = false;
    //     } else {
    //         console.log('Ativar')
    //         //$('#notification_box').css('height', 'auto');
    //         // $('#notification_box').css('opacity', '1');
    //         // $('#notification_box').css('display', 'block');
    //         // $('#notification_box').css('visibility', 'visible');
    //         down = true;
    //     }

    // });

    $('#bell-dropdown').on('shown.bs.dropdown', function () {
        notifications = $('#notification_box')

        url = $('#bell').attr('href')
        // console.log(url)
        $.ajax({
            url: url,
            type: 'get',
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
                data.forEach(function (element) {
                    notifications.append(
                        '<a href="' + element.url + '" class="notification-link" id="notification-' + element.id + '">' +
                        '<div class="notifications-item">' +
                        '<div class="text">' +
                        '<h6>' + element.title + '</h6>' +
                        '<p>' + element.content + '</p>' +
                        '</div>' +
                        '</div>' +
                        '</a>')
                    console.log(element.content)
                }
                )

                // $(target).collapse();

            },
            error: function (data) {
                if (data.status == 404) {
                    if (!button_accordion.hasClass('bg-danger')) {
                        button_accordion.addClass('bg-danger')
                        button_accordion.append('<span class="badge bg-secondary mx-3">Não encontrado</span>\n')

                    }
                }
                if (data.status == 500) {
                    if (!button_accordion.hasClass('bg-danger')) {

                    }
                }
            }
        });
    });

    $('#bell-dropdown').on('hidden.bs.dropdown', function () {
        var notifications = $('#notification_box')
        notifications.html("");
    });










    $.ajax({ 
        url: "/api/notifications/autoload",
        type: 'get',
        dataType: 'json',
        headers: {
            'X-CSRFToken': $CSRF_TOKEN
        },
        context: document.body,
        success: function(data){
            data.forEach(function (element) {
            console.log(data)
            toast = $('#toast-'+element.subtopic)
            // if (element.level == 'warning') {
            //     toast.removeClass('text-white')
            //     toast.addClass('bg-'+element.level+ ' text-dark')
                
            // }
            // else {
            //     toast.addClass('bg-'+element.level)
            // }
            toast.addClass('bg-'+element.level)
            toast_title = toast.find('#toast-title')
            toast_title.text(element.title)
            toast_elapsed_time = toast.find('#toast-time')
            toast_elapsed_time.text(element.created_elapsed_time)
            toast_content = toast.find('#toast-content')
            toast_content.empty()
            toast_content.append(element.content)
            toast_content.append('<span class="badge bg-secondary mx-1">'+ element.subtopic +'</span><span class="badge bg-primary mx-1">Automática</span>')
            toast.toast('show');
            });        
        }
    });

    if (getCookie('bg') == 'black') {
        change_background();
    }

    let darkBackground = document.querySelector('body');
    let darkModeBtn = document.getElementById('darkModeBtn');
    let btnIcon = document.getElementById('btnIcon');
    let codeButton = document.getElementsByClassName('code-btn');

    darkModeBtn.addEventListener('click', function(e) {
        e.preventDefault();
        change_background()

    });
    


});

$(document).on('click', '.notification-link', function () {
    url = $(this).attr('href');
    id = $(this).attr('id').split('-')[1]
    $.ajax({
        url: url,
        type: 'get',
        dataType: 'json',
        beforeSend: function () {
            like_link = false;
        },
        complete: function () {
            like_link = false;
        },
        success: function (data) {
            toast = $('#toast-general')
            toast_title = toast.find('#toast-title')
            toast_title.text(data.title)
            toast_elapsed_time = toast.find('#toast-time')
            toast_elapsed_time.text(data.created_elapsed_time)
            toast_content = toast.find('#toast-content')
            toast_content.empty()
            toast_content.append(data.content)
            toast_content.append('<br><br><span class="badge bg-secondary">'+ data.subtopic +'</span>')
            toast.toast('show');
        },
        error: function (data) {
            like_link = false;
        }
    })
    return false;
})

$(document).on('click', '#toast-close', function(e){
    $('.toast').toast('hide')
})
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
    var question_id = split_id[1];

    if ($(this).hasClass('like')) {
        action = 'like';
        invert = 'unlike';
    } else if ($(this).hasClass('unlike')) {
        action = 'unlike';
        invert = 'like'
    } else {
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
    } else if ($(this).hasClass('unsave')) {
        action = 'unsave';
        invert = 'save'
    } else {
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
            save_link = false;
        }
    });
    return false;
});

$(document).on('click', ".remove", function (e) {

    remove_link = true;
    var remove_href = $(this).attr('href');
    remove_confirm = $("#delete-modal").find('.delete')
    // console.log(remove_confirm)
    remove_confirm.attr('href', remove_href)
    removeModal.show();

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
            removeModal.toggle();
            if (data.status === 'success') {

            }
        }
    });

});

$("#delete-modal").on("show.bs.modal", function (e) {
    var link = $(e.relatedTarget);

});

function iframeLoaded(frame_id) {
    var iFrameID = document.getElementById(frame_id.id);
    // console.log('aqui')
    // console.log(frame_id.id)
    // console.log(iFrameID)
    if (iFrameID) {
        // here you can make the height, I delete it first, then I make it again
        iFrameID.height = "";
        iFrameID.height = iFrameID.contentWindow.document.body.scrollHeight + "px";
    }
}


function create_toast(){
    html = '<div class="toast text-white bg-danger hide" data-bs-autohide="false" id="toast-general">' +
            '<div class="toast-header">'+
            '<svg class="bd-placeholder-img rounded me-2" width="20" height="20" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" preserveAspectRatio="xMidYMid slice" focusable="false">'+
            '<rect width="100%" height="100%" fill="#f17a0a"></rect>'+
            '</svg>'+
            '<strong class="me-auto"  id="toast-title"></strong>'+
            '<small id="toast-time"></small>'+
            '<button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>'+
            '</div>'+
            '<div class="toast-body" id="toast-content">'+
            '</div>'+
            '</div>'
    return html
}




function change_background(){
    let darkBackground = document.querySelector('body');
    let darkModeBtn = document.getElementById('darkModeBtn');
    let btnIcon = document.getElementById('btnIcon');
    darkBackground.classList.toggle('darkbackground');

    if (darkBackground.classList.contains('darkbackground')){
        document.querySelectorAll(".bg-light").forEach(function(elem) {
            elem.classList.replace("bg-light", "bg-dark");
            elem.classList.replace("text-dark", "text-white");
            codemirror = document.getElementsByClassName('CodeMirror');
            if (codemirror.length === 1){
                codemirror[0].classList.add("bg-dark", 'text-white')
            }
        })
        btnIcon.classList.replace("fa-moon", "fa-sun");
    } else {
        document.querySelectorAll(".bg-dark").forEach(function(elem) {
            elem.classList.replace("bg-dark", "bg-light");
            elem.classList.replace("text-white", "text-dark");
        });
        btnIcon.classList.replace("fa-sun", "fa-moon");//classList.toggle('fa-moon');
    };
    bg = darkBackground.classList.contains('darkbackground') ? 'black' : 'white';
    console.log(bg)
    setCookie('bg', bg);
    // if (darkBackground.classList.contains('darkbackground')){
    //     btnIcon.classList.toggle('fa-moon');
    // }else{
    //     btnIcon.classList.toggle('fa-sun');
    // }
    // $.ajax({
    //     url: url_bg,
    //     type: 'post',
    //     data: { confirm: true },
    //     dataType: 'json',
    //     headers: {
    //         "X-CSRFToken": $CSRF_TOKEN,
    //     },
    //     success: function (data) {
    //         console.log(data)
    //         if (data.value === true) {
    //             console.log("Fim")
    //             if (darkBackground.classList.contains('darkbackground')){
    //                 url_bg.replace('dark', 'white')
    //                 btnIcon.classList.toggle('fa-moon');
    //             }else{
    //                 btnIcon.classList.toggle('fa-sun');
    //                 url_bg.replace('white', 'dark');
    //             }
    //         }
    //         darkModeBtn.setAttribute('href', url_bg);

    //     }
    // });
}

function getCookie(name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for(var i=0;i < ca.length;i++) {
        var c = ca[i];
        while (c.charAt(0)==' ') c = c.substring(1,c.length);
        if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
    }
    return false;
}

function setCookie(name,value,days) {
    var expires = "";
    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days*24*60*60*1000));
        expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + (value || "")  + expires + "; path=/";
}