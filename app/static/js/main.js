$(document).ready(function () {

    // like and unlike click

    accordion_link = false;
    like_link = false;
    save_link = false;
    load_modal = true;


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
                    head_info.append('Criado ' + data.create_at + ' por ' + data.author)
                }
                else {
                    head_info.append('Atualizado ' + data.update_at + ' por ' + data.updater)
                }

                accordion_collapse.append('<div class="accordion-head-buttons"></div>')
                accordion_buttons = accordion_collapse.find('.accordion-head-buttons')
                if (data.url_edit !== undefined) {
                    accordion_buttons.append('<a class="edit text-decoration-none" id="edit_' + question_id + '"' +
                        'href="' + data.url_edit + '">' +
                        '<i class="fas fa-edit"></i>' +
                        '</a>');
                }

                if (data.like_action !== undefined) {
                    like_icon = data.like_action == 'like' ? 'far' : 'fas';
                    accordion_buttons.append(
                        '<a class="like-button ' + data.like_action + '" id="like_' + question_id + '"' +
                        'href="' + data.url_like + '">' +
                        '<i class="' + like_icon + ' fa-heart"></i></a>'
                    );
                }
                if (data.save_action !== undefined) {
                    save_icon = data.save_action == 'save' ? 'far' : 'fas';
                    accordion_buttons.append(
                        '<a class="save-button ' + data.save_action + '" id="save_' + question_id + '"' +
                        'href="' + data.url_save + '">' +
                        '<i class="' + save_icon + ' fa-save"></i></a>'
                    );
                }


                accordion_collapse.append(
                    '<div class="accordion-body">' + data.answer + '</div>'
                );
                $(target).collapse();
                
            },
            error: function(data){
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
            console.log('Erro');
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
            console.log('Erro');
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
    var removeModal = new bootstrap.Modal(document.getElementById("delete-modal"), {});
    console.log(removeModal)
    
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
            console.log(data)
        }
    });
    console.log(confirm_delete_href)

});

$("#delete-modal").on("show.bs.modal", function(e) {
    // if (load_modal === false){
    //     e.preventDefault();
    // }
    console.log(e.currentTarget.id)
    
    // e.preventDefault()
    var link = $(e.relatedTarget);
    console.log(e)    
    var myModal = new bootstrap.Modal(document.getElementById(e.currentTarget.id), {});
    console.log(e.currentTarget.id)
    console.log(myModal)
    setTimeout(
        function() 
        {
          console.log('aqui')
        }, 5000);
    // $(this).find(".modal-body").load(link.attr("href"));
    // load_modal = false
    // myModal.show()
    // load_modal = true;
});