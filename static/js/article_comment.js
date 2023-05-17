layui.use(['jquery'], function() {
    var $ = layui.jquery;

    // 登录之后发表评论
    $('.comment_form_logout').click(function() {
        layui.layer.msg('Necessita log in');
        // 调转到登录页面
        setTimeout(function() {
            location.href = '/login?next=' + location.pathname;
        }, 1500);
    });
    // 评论
    $('.comment_form').submit(function(e) {

        let comment = $('.comment_input').val();
        if (!comment) {
            layui.layer.msg('pone conntenido');
        } else {
            // 请求后端接口发表评论
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
                /*
                * 评论成功之后需要更新评论数据
                * 1. 动态更新
                * 2. 直接刷新页面
                * */
            });
        }
        e.preventDefault();  // 阻止默认的
    });

    // 点击回复显示二级回复表单
    $('.comment_reply').click(function(e) {
        $(this).parents('.comment-details').siblings('.reply_form').show();
    });
    // 二级回复
    $('.reply_form').submit(function(e) {
        let comment = $(this).find('.reply_input').val();
        let comment_id = $(this).attr('data-commit-id');
        if (!comment) {
            layui.layer.msg('Pone contenido');
        } else {
            // 请求后端接口发表评论
            fetch('/article/article_comment', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    article_id: article_id,
                    comment: comment,
                    parent_id: comment_id,
                    // 二级提交需要父评论的 id
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
                /*
                * 评论成功之后需要更新评论数据
                * 1. 动态更新
                * 2. 直接刷新页面
                * */
            });
        }
        e.preventDefault();  // 阻止默认的
    });
});
