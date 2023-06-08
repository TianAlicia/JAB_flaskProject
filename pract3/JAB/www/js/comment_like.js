layui.use(['jquery'], function() {
    var $ = layui.jquery;
    $('.comment_up').click(function() {
        let comment_id = $(this).
            parents('.comment-details').
            siblings('.reply_form').
            attr('data-commit-id');

        // has_comment_up
        let action = $(this).hasClass('has_comment_up') ? 'remove' : 'add';
        fetch('/article/comment_like', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({comment_id: comment_id, action: action}),
        }).then(function(response) {
            return response.json();
        }).then(function(ret) {
            if (ret.status === 'success') {
                location.reload();
            } else {
                layui.layer.msg(ret.message);
            }
        });
    });
});
