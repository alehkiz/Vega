$(document).ready(function () {

    // like and unlike click
    

    

    $('.accordion-button').click(function (e) {
        h2_obj = $(this).parent()
        // console.log(h2_obj)
        var id = h2_obj.attr('id');
        var split_id = id.split('_');
        var question_id = split_id[1];

        // console.log(e)
        var target = $(this).attr('data-bs-target')
        var url = $(this).attr('href')
        // console.log(url)
        if ($(target).length > 0) {
            return false;
        }
        $.ajax({
            url: url,
            type: 'post',
            dataType: 'json',
            headers: {
                'X-CSRFToken': $CSRF_TOKEN
            },
            success: function (data) {
                // console.log(data)
                // console.log(id)
                h2_obj.parent().append('<div id="flush-collapse_' + question_id + '" class="accordion-collapse collapse accordion-border"' +
                    'aria-labelledby="flush-heading_' + question_id + '" data-bs-parent="#accordionFlushQuestion">')
                $('#flush-collapse_' + question_id).append('<div class="accordion-head">' +
                    '<div class="accordion-head-info">' +
                    '</div>' +
                    '</div>'
                )
                accordion_collapse = $('#flush-collapse_' + question_id);
                head_info = $('#flush-collapse_' + question_id).find(".accordion-head-info")
                if (!data.update_at || !data.updater) {
                    head_info.append('Criado '+ data.create_at + ' por ' + data.author)
                }
                else{
                    head_info.append('Atualizado ' + data.update_at + ' por ' + data.updater)
                }

                accordion_collapse.append('<div class="accordion-head-buttons"></div>')
                accordion_buttons = accordion_collapse.find('.accordion-head-buttons')
                if (data.url_edit !== null){
                    accordion_buttons.append('<a class="edit text-decoration-none" id="edit_'+question_id+'"'+
                        'href="'+data.url_edit+'">'+
                        '<i class="fas fa-edit"></i>'+
                        '</a>');
                }
                like_icon = data.like_action == 'like' ? 'far' : 'fas';
                save_icon = data.save_action == 'save' ? 'far' : 'fas';

                accordion_buttons.append(
                    '<a class="like-button '+data.like_action+'" id="like_'+question_id+'"'+
                        'href="'+data.url_like+'">'+
                        '<i class="'+like_icon+' fa-heart"></i></a>'
                )

                accordion_buttons.append(
                    '<a class="save-button '+data.save_action+'" id="save_'+question_id+'"'+
                    'href="'+data.url_save+'">'+
                    '<i class="'+save_icon+' fa-save"></i></a>'
                    )

                accordion_collapse.append(
                    '<div class="accordion-body">'+data.answer+'</div>'
                )
                $(target).collapse()

            }

        });
        return false;
    });


});


$(document).on('click', ".like, .unlike", function (e) {
    var link = $(this)
    var id = this.id;
    var split_id = id.split("_");
    var action = split_id[0];
    var link_href = $(this).attr('href');
    if (link_href == "#") {
        return false;
    }
    $(this).attr('href', '#');
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
        success: function (data) {
            $("#" + id).removeClass(action);
            $("#" + id).addClass(invert);
            i = $('#' + id).children();
            link.attr('href', link_href);
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
            console.log('Erro')
        }
    });
    return false;
});



$(document).on('click', ".save, .unsave", function (e) {
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
        success: function (data) {
            $("#" + id).removeClass(action);
            $("#" + id).addClass(invert);
            i = $('#' + id).children()
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
            console.log('Erro')
        }
    });
    return false;
});