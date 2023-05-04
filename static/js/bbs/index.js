layui.use(function() {
  let $ = layui.$;
  let laypage = layui.laypage;
  let current_cid = 0; // 当前分类 id
  let current_page = 1; // 当前页
  let total_page = 1;  // 总页数
  let data_querying = true;   // 是否正在向后台获取数据

  // 首页分类切换
  $('.menu li').click(function() {
    let click_cid = $(this).attr('data-cid');
    $('.menu li').each(function() {
      $(this).removeClass('active');
    });
    // 设置当前标签别选中并且高亮
    $(this).addClass('active');

    if (click_cid !== current_cid) {
      // 记录当前分类id
      current_cid = click_cid;
      // 重置分页参数
      current_page = 1;
      total_page = 1;
      update_news_data();
    }
  });

  // 请求并加载新的数据
  function update_news_data() {
    // TODO 更新新闻数据
    let params = {
      'cid': current_cid,
      'page': current_page,
    };
    $.get('/article_list', params,
        function(resp_data) {
          // 数据加载完毕，设置【正在加载数据】的变量为 false 代表当前没有在加载数据
          data_querying = false;

          if (resp_data.status === 'success') {
            // 给总页数据赋值
            total_page = resp_data.total_page;
            // 代表请求成功
            // 清除已有数据
            if (current_page === 1) {
              $('.article_list').html('');
            }
            // 添加请求成功之后返回的数据
            // 显示数据
            for (let i = 0; i < resp_data.newsList.length; i++) {
              let news = resp_data.newsList[i];
              let content = `
                            <div class="layui-card article">
                                <div class="layui-card-header">
                                    <a href="/article/${article.id}" class="news_pic">
                                        <img src="${article.index_image_url}">
                                    </a>
                                </div>
                                <div class="layui-card-body">
                                    <a href="/article/${article.id}" class="news_title">${article.title}</a>
                                    <a href="/article/${article.id}}" class="news_detail">
                                        ${article.digest}
                                    </a>
                                    <div class="author_info">
                                        <div class="author">
                                            <img src="../assets/images/person.png" alt="author">
                                            <a href="/user/${article.user_id}">正心</a>
                                        </div>
                                        <div class="time">${article.create_time}</div>
                                    </div>
                                </div>
                            </div>`;
              $('.articles').append(content);
            }
          } else {
            // 请求失败
            // {#layer.msg(resp_data.message)#}
            layer.msg('请求数据失败');
          }
        });
  }

  // 自定义首页、尾页、上一页、下一页文本
  // 分页展示数据
  laypage.render({
    elem: 'pagination'
    , count: 100
    , curr: 1
    , first: '首页'
    , last: '尾页'
    , limit: 10
    , prev: '<em>←</em>'
    , next: '<em>→</em>'
    , jump: function(obj, first) {
      if (!first) {
        if (obj.curr !== parseInt(getUrlParam('page'))) {
          window.location.href = changeHref(window.location.href, 'page',
              obj.curr);
        }
      }
    },
  });
});
