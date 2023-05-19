let image_code_uuid = null;
    
    function generateUUID() {
        var d = new Date().getTime();
        if (window.performance && typeof window.performance.now === 'function') {
            d += performance.now(); //use high-precision timer if available
        }
        var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g,
            function (c) {
                var r = (d + Math.random() * 16) % 16 | 0;
                d = Math.floor(d / 16);
                return (c == 'x' ? r : (r & 0x3 | 0x8)).toString(16);
            });
        return uuid;
    }

    //
    function generateChapter() {
        image_code_uuid = generateUUID();
        // console.log(generateUUID())
        document.getElementById('captchaImage').src = '/get_captcha?image_code_uuid=' + image_code_uuid;

    }   //'jquery'

    layui.use(['form', 'layer', 'jquery'], function () {
        let $ = layui.jquery;
        let form = layui.form;
        
        generateChapter();
        document.getElementById('captchaImage').src = '/get_captcha?image_code_uuid=' + image_code_uuid;
 
        $('#captchaImage').click(function () {
            generateChapter();
        });

        $('.send_sms').click(function () {

            let data = {
                captcha_code: $('[name="captcha"]').val(),
                captcha_code_uuid: image_code_uuid,
                mobile: $('[name="Email"]').val(),
            };
            const options = {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            };

            fetch('/sms_code', options).then(function (response) {
                return response.json();
            }).then(function (result) {
                // {#console.log(result);#}
                if (result.status === 'fail') {
                    layer.msg(result.message);
                } else {
                    layer.msg(result.message);
                    var num = 60;
                    var t = setInterval(function () {
                        if (num === 1) {
                            clearInterval(t);
                            $('.send_sms').html(gettext('Codi de verificació'));
                        }
                    }, 1000);
                }
            });
        });

        var codeInput = document.querySelector('input[name="invitation_code"]');
        var registerButton = document.querySelector('button[lay-filter="register"]');

        registerButton.addEventListener('click', function (event) {
            event.preventDefault();

            if (codeInput.value === "1234") {
                register();
            } else {
                alert(gettext("Error"));
            }
        });

        async function register() {
            var nom = document.querySelector('input[name="nickname"]').value;
            var password = document.querySelector('input[name="password"]').value;
            var email = document.querySelector('input[name="Email"]').value;
            var mobile = document.querySelector('input[name="mobile"]').value;
        
            // Check if mobile already exists
            const checkMobileResponse = await fetch(`/check_mobile?mobile=${mobile}`);
            const checkMobileResult = await checkMobileResponse.json();
            if (checkMobileResult.status === 'fail') {
                alert(checkMobileResult.message);
                return;
            }
        
            // Check if name already exists
            const checkNameResponse = await fetch(`/check_name?nom=${nom}`);
            const checkNameResult = await checkNameResponse.json();
            if (checkNameResult.status === 'fail') {
                alert(checkNameResult.message);
                return;
            }
        
            var data = {
                mobile: mobile,
                nom: nom,
                password: password,
                email: email
            };
        
            const response = await fetch('/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
        
            const result = await response.json();
        
            if (result.status === 'success') {
                window.location.href = '/login'; 
            } else {
                alert(gettext("Registre incorrecte, el nom o el mòvil ja existeix.")); 
            }
        }
        
    })