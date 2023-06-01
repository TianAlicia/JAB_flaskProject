layui.use(function() {
  let form = layui.form;
  let $ = layui.jquery;
  let captchaPath = '/get_captcha';
  let imageCodeId = '';

  // 点击按钮更新验证码
  $('#captchaImage').click(function() {
    // 浏览器要发起图片验证码请求/image_code?imageCodeId=xxxxx
    imageCodeId = generateUUID();
    document.getElementById('captchaImage').src = captchaPath + '?image_code_uuid=' +
        imageCodeId;
  });

  // 定时器，定时更新验证码
  setInterval(function() {
    imageCodeId = generateUUID();
    document.getElementById('captchaImage').src = captchaPath + '?image_code_uuid=' +
        imageCodeId;
  }, 50 * 1000);

  imageCodeId = generateUUID();
  document.getElementById('captchaImage').src = captchaPath + '?image_code_uuid=' +
      imageCodeId;

  async function login(data) {
    data['captcha_code_uuid'] = imageCodeId;
    data['next'] = getUrlParam('next');
    const options = {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    };
    const response = await fetch('/login', options);
    return await response.json();
  }

  form.on('submit(login)', async function(data) {
    const result = await login(data.field);
    if (result.status === 'success') {
      layui.layer.msg(result.message);

      // 定时两秒之后跳转
      setInterval(function() {
        window.location.href = result.next ? result.next : '/';
      }, 2000);
    } else {
      layui.layer.msg(result.message);
    }
    return false;
  });

});
