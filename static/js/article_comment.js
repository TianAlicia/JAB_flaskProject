layui.use(['jquery'], function() {
    var $ = layui.jquery;


    $('.comment_form_logout').click(function() {
        layui.layer.msg('Necessita log in');
        //
        setTimeout(function() {
            location.href = '/login?next=' + location.pathname;
        }, 1500);
    });
    //
    $('.comment_form').submit(function(e) {

        let comment = $('.comment_input').val();
        if (!comment) {
            layui.layer.msg(gettext('Cal contingut'));
        } else {

            fetch('/article/article_comment', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    article_id: article_id,
                    comment: comment,
                }),
            }).then(function(response) {
                return response.json();
            }).then(function(ret) {
                console.log(ret);
                if (ret.status === 'success') {
                    layui.layer.msg(ret.message);
                    setTimeout(function() {
                        location.reload();
                    }, 1000);
                } else {
                    layui.layer.msg(ret.message);
                }

            });
        }
        e.preventDefault();
    });


    $('.comment_reply').click(function(e) {
        $(this).parents('.comment-details').siblings('.reply_form').show();
    });
    //
    $('.reply_form').submit(function(e) {
        let comment = $(this).find('.reply_input').val();
        let comment_id = $(this).attr('data-commit-id');
        if (!comment) {
            layui.layer.msg(gettext('Pone contenido'));
        } else {
            //
            fetch('/article/article_comment', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    article_id: article_id,
                    comment: comment,
                    parent_id: comment_id,
                    //
                }),
            }).then(function(response) {
                return response.json();
            }).then(function(ret) {
                console.log(ret);
                if (ret.status === 'success') {
                    layui.layer.msg(ret.message);
                    setTimeout(function() {
                        location.reload();
                    }, 1000);
                } else {
                    layui.layer.msg(ret.message);
                }

            });
        }
        e.preventDefault();
    });
});
