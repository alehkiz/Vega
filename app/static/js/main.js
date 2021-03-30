$(document).ready(function () {

    // like and unlike click
    $(".like, .unlike").click(function (e) {
        var link = $(this)
        var id = this.id;
        var split_id = id.split("_");
        var action = split_id[0];
        var link_href = $(this).attr('href');
        if (link_href == "#"){
            return false;
        }
        $(this).attr('href', '#');
        var question_id = split_id[1];

        if ($(this).hasClass('like')){
            action = 'like';
            invert = 'unlike';
        }
        else if ($(this).hasClass('unlike')){
            action = 'unlike';
            invert = 'like'
        }
        else{
            action = false;
        }
        // AJAX Request
        $.ajax({
            url: link_href,
            type: 'post',
            data: { action:action },
            dataType: 'json',
            headers: {
                "X-CSRFToken": $CSRF_TOKEN,
            },
            success: function (data) {
                $("#" + id).removeClass(action);
                $("#" + id).addClass(invert);
                i = $('#' + id).children();
                link.attr('href', link_href);
                i.toggleClass(function(){

                    if ($(this).hasClass('icon-heart-empty')){
                        $(this).removeClass('icon-heart-empty')
                        return 'icon-heart'
                    } else {
                        $(this).removeClass('icon-heart')
                        return 'icon-heart-empty'
                    }
                });
            },
            error: function(data){
                console.log('Erro')
            }
        });
        return false;
    });

    $(".save, .unsave").click(function (e) {
        var id = this.id;
        var split_id = id.split("_");
        var action = split_id[0];
        var question_id = split_id[1];
        if ($(this).hasClass('save')){
            action = 'save';
            invert = 'unsave';
        }
        else if ($(this).hasClass('unsave')){
            action = 'unsave';
            invert = 'save'
        }
        else{
            action = false;
        }
        // AJAX Request
        $.ajax({
            url: this.href,
            type: 'post',
            data: { action:action },
            dataType: 'json',
            headers: {
                "X-CSRFToken": $CSRF_TOKEN,
            },
            success: function (data) {
                $("#" + id).removeClass(action);
                $("#" + id).addClass(invert);
                i = $('#' + id).children()
                // i.toggleClass(function(){

                //     if ($(this).hasClass('icon-heart-empty')){
                //         $(this).removeClass('icon-heart-empty')
                //         return 'icon-heart'
                //     } else {
                //         $(this).removeClass('icon-heart')
                //         return 'icon-heart-empty'
                //     }
                // });
            },
            error: function(data){
                console.log('Erro')
            }
        });
        return false;
    });


});