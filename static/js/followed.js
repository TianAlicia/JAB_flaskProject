layui.use(['jquery', 'layer'], function() {
    var $ = layui.jquery;
    var layer = layui.layer;
    $('.focus').click(function() {
        let user_id = $(this).parents('.author_card').attr('data-userid');
        let that = this;
        fetch('/article/followed_user', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({'user_id': user_id, action: 'follow'}),
        }).then(function(response) {
            return response.json();
        }).then(function(ret) {
            console.log(ret);
            layer.msg(ret.message);
            $(that).hide().siblings('.focused').show();
        });
    });

    $('.focused').click(function() {
        let user_id = $(this).parents('.author_card').attr('data-userid');
        let that = this;
        fetch('/article/followed_user', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({'user_id': user_id, action: 'unfollow'}),
        }).then(function(response) {
            return response.json();
        }).then(function(ret) {
            console.log(ret);
            layer.msg(ret.message);
            $(that).hide().siblings('.focus').show();
        });
    });
});
