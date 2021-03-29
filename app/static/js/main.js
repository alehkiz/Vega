$(document).ready(function () {

    // like and unlike click
    $(".like, .unlike").click(function (e) {
        var id = this.id;   // Getting Button id
        console.log(this.href)
        var split_id = id.split("_");

        var text = split_id[0];
        var question_id = split_id[1];  // questionid
        if ($(this).hasClass('like')){
            action = 'like';
        }
        else if ($(this).hasClass('unlike')){
            action = 'unlike';
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
                console.log('aqui')
                console.log(data)
                var like = data['like'];
                var unlike = data['unlike'];

                $("#like_" + question_id).json(data);        // setting likes
                $("#unlike_" + question_id).json(data);    // setting unlikes
                 

            },
            error: function(data){
                alert('erro')
            }
        });
        return false;
    });

});