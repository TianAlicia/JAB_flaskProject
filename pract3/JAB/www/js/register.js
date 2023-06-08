layui.use(function () {
        let form = layui.form;
        let $ = layui.jquery;
        let captchaPath = '/auth/getCaptcha'; /*图片验证的访问地址*/
        let imageCodeId = '';  /*定义图片验证码的 uuid */


        // {#点击按钮更新验证码#}
        $('#captchaImage').click(function () {
            // {#浏览器要发起图片验证码请求/image_code?imageCodeId=xxxxx#}
            update_captcha_image();
        });

        // {#更新验证码的方法#}
        function update_captcha_image() {
            imageCodeId = generateUUID();
            document.getElementById('captchaImage').src = captchaPath + '?image_code=' + imageCodeId;
        }

        // {#定时器，定时更新验证码#}
        setInterval(update_captcha_image, 50 * 1000);


        // {#每次进入页面之后,自动刷新验证码#}
        update_captcha_image();

        $('.send_sms').click(function () {
            // {#发送收集短信#}
            console.log('请求发送短信');
            let data = {
                image_code: $('[name="captcha"]').val(),
                image_code_id: imageCodeId,
                mobile: $('[name="mobile"]').val(),
            };
            const options = {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            };

            fetch('/auth/sms_code', options).then(function (response) {
                return response.json();
            }).then(function (result) {
                // {#console.log(result);#}
                if (result.status === 'fail') {
                    // {#代表发送失败#}
                    layer.msg(result.message);
                } else {
                    layer.msg(result.message);
                    // {#代表发送成功#}
                    var num = 60;
                    var t = setInterval(function () {
                        // {#代表倒计时结束#}
                        if (num === 1) {
                            // {#清除倒计时#}
                            clearInterval(t);
                            // {#设置显示内容#}
                            $('.send_sms').html(gettext('Fes click per obtenir el codi'));
                            // {#添加点击事件#}
                            // $('.send_sms').attr('onclick', 'sendSMSCode();');
                        } else {
                            num -= 1;
                            // {#设置 a 标签显示的内容#}
                            $('.send_sms').html(num + gettext('Segon'));
                        }
                    }, 1000);
                }
            });
        });

        async function register(data) {
            data['image_code'] = imageCodeId
            const options = {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            }
            const response = await fetch('/register', options)
            return await response.json()
        }

        // 监听登录表单的提交事件
        form.on('submit(register)', async function (data) {
            const result = await register(data.field)
            if (result.status === 'success') {
                window.location.href = '/login'
            } else {
                layui.layer.msg(result.message)
                update_captcha_image()
            }
            return false
        })
    });
