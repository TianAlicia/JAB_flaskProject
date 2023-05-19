layui.use(['jquery'], function() {
    var $ = layui.jquery;

    $('.collection').click(function() {
        fetch('/article/article_collect', {
            method: 'post',
            headers: {
                'content-type': 'application/json',
            },
            body: JSON.stringify({
                'action': 'collect',
                'article_id': article_id,
            }),
        }).then(function(res) {
            return res.json();
        }).then(function(ret) {
            console.log(ret);
            if (ret.code === 0) {
                layui.layer.msg(ret.message);
            } else if (ret.code === 4101) {
                layui.layer.msg(gettext('Cal fer Login'));
                // 调转到登录页面
                setTimeout(function() {
                    location.href = '/login?next=' + location.pathname;
                }, 1500);
            }
        });
    });

    $('.collected').on({
        mouseover: function() {
            $(this).find('.out').hide();
            $(this).find('.over').show();
        },
        mouseout: function() {
            $(this).find('.out').show();
            $(this).find('.over').hide();
        },
        click: function() {
            fetch('/article/article_collect', {
                method: 'post',
                headers: {
                    'content-type': 'application/json',
                },
                body: JSON.stringify({
                    'action': 'cancel_collect',
                    'article_id': article_id,
                }),
            }).then(function(res) {
                return res.json();
            }).then(function(ret) {
                console.log(ret);
                if (ret.code === 0) {
                    layui.layer.msg(ret.message);
                } else if (ret.code === 4101) {
                    layui.layer.msg(gettext('Cal fer Login'));
                    //
                    setTimeout(function() {
                        location.href = '/login?next=' + location.pathname;
                    }, 1500);
                }
            });
        },
    });
});
