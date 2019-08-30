$(function () {

    // 打开登录框
    $('.login_btn').click(function () {
        $('.login_form_con').show();
    });

    // 点击关闭按钮关闭登录框或者注册框
    $('.shutoff').click(function () {
        $(this).closest('form').hide();
    });

    // 隐藏错误
    $(".login_form #mobile").focus(function () {
        $("#login-mobile-err").hide();
    });
    $(".login_form #password").focus(function () {
        $("#login-password-err").hide();
    });

    $(".register_form #register_username").focus(function () {
        $("#register-username-err").hide();
    });
    $(".register_form #register_email").focus(function () {
        $("#register-email-err").hide();
    });
    $(".register_form #smscode").focus(function () {
        $("#register-sms-code-err").hide();
    });
    $(".register_form #password").focus(function () {
        $("#register-password-err").hide();
    });


    // 点击输入框，提示文字上移
    // animate执行css属性，实现自定义动画，返回jQuery对象，siblings获取兄弟元素
    $('.form_group').on('click focusin', function () {
        $(this).children('.input_tip').animate({
            'top': -5,
            'font-size': 12
        }, 'fast').siblings('input').parent().addClass('hotline');
    });

    // 输入框失去焦点，如果输入框为空，则提示文字下移
    $('.form_group input').on('blur focusout', function () {
        $(this).parent().removeClass('hotline');
        var val = $(this).val();
        if (val == '') {
            $(this).siblings('.input_tip').animate({'top': 22, 'font-size': 14}, 'fast');
        }
    });


    // 打开注册框
    $('.register_btn').click(function () {
        $('.register_form_con').show();
        // generateImageCode()
    })


    // 登录框和注册框切换
    $('.to_register').click(function () {
        $('.login_form_con').hide();
        $('.register_form_con').show();
        // generateImageCode()
    })

    // 登录框和注册框切换
    $('.to_login').click(function () {
        $('.login_form_con').show();
        $('.register_form_con').hide();
    })

    // 根据地址栏的hash值来显示用户中心对应的菜单
    var sHash = window.location.hash;
    if (sHash != '') {
        var sId = sHash.substring(1);
        var oNow = $('.' + sId);
        var iNowIndex = oNow.index();
        $('.option_list li').eq(iNowIndex).addClass('active').siblings().removeClass('active');
        oNow.show().siblings().hide();
    }

    // 用户中心菜单切换
    var $li = $('.option_list li');
    var $frame = $('#main_frame');

    $li.click(function () {
        if ($(this).index() == 5) {
            $('#main_frame').css({'height': 900});
        }
        else {
            $('#main_frame').css({'height': 660});
        }
        $(this).addClass('active').siblings().removeClass('active');
        $(this).find('a')[0].click()
    })

    // TODO 登录表单提交
    $(".login_form_con").submit(function (e) {
        e.preventDefault()
        var mobile = $(".login_form #mobile").val();
        var username = $(".login_form #musername").val();
        var password = $(".login_form #password").val();

        if (!username) {
            $("#login-username-err").show();
            return;
        }

        if (!password) {
            $("#login-password-err").show();
            return;
        }

        // 发起登录请求
    });


    // TODO 注册按钮点击
    $(".register_form_con").submit(function (e) {
        // 阻止默认提交操作
        e.preventDefault();

        // 取到用户输入的内容
        let mobile = $("#register_mobile").val();
        let username = $("#register_username").val();
        let email = $("#register_email").val();
        let smscode = $("#smscode").val();
        let password = $("#register_password").val();

        if (!username) {
            $("#register-username-err").show();
            return;
        }
        if (!email) {
            $("#register-email-err").show();
            return;
        }
        if (!smscode) {
            $("#register-sms-code-err").show();
            return;
        }
        if (!password) {
            $("#register-password-err").html("请填写密码!");
            $("#register-password-err").show();
            return;
        }

        if (password.length < 6) {
            $("#register-password-err").html("密码长度不能少于6位");
            $("#register-password-err").show();
            return;
        }

        // 发起注册请求
        let params = {
            "username":username,
            "email":email,
            "image_code":""
        };
        $.ajax({
            url:""
        })
    })
});

// let imageCodeId = "";
//
// // TODO 生成一个图片验证码的编号，并设置页面中图片验证码img标签的src属性
// function generateImageCode() {
//     imageCodeId = generateUUID();
//     let url = '/passport/image_code?imageCodeId=' + imageCodeId;
//     // 设置src属性，就会自动向这个url发送请求
//     $(".get_pic_code").attr("src", url);
// }

// 发送短信验证码
function sendSMSCode() {
    // 校验参数，保证输入框有数据填写
    $(".get_code").removeAttr("onclick");
    let email = $("#register_email").val();
    let username = $("#register_username").val();
    if (!email && !username) {
        $("#register-mobile-err").html("请填写正确的邮箱！");
        $("#register-mobile-err").show();
        $(".get_code").attr("onclick", "sendSMSCode();");
        return;
    }
    let imageCode = $("#imagecode").val();
    if (!imageCode) {
        $("#image-code-err").html("请填写验证码！");
        $("#image-code-err").show();
        $(".get_code").attr("onclick", "sendSMSCode();");
        return;
    }

    // TODO 发送邮箱验证码
    let params = {
        "username":username,
        "email":email,
        "image_code":imageCode,
        "image_code_id":imageCodeId
    };
    $.ajax({
        url:"/passport/mail",
        type:"post",
        data:JSON.stringify(params),
        contentType:"application/json",
        success:function (response) {
            if (response.errno === "0"){
                let num = 60;
                let t = setInterval(function () {
                    if (num === 1){
                        clearInterval(t);
                        $(".get_code").html("点击获取验证码");
                        $(".get_code").attr("onclick", "sendSMSCode();");
                    } else{
                        num -= 1;
                        // 设置a标签显示的内容
                        $(".get_code").html(num + "秒");
                    }
                }, 1000)
            } else {
                alert(response.errmsg)
                $(".get_code").attr("onclick", "sendSMSCode();");
            }
        }
    })
}

// 调用该函数模拟点击左侧按钮
function fnChangeMenu(n) {
    var $li = $('.option_list li');
    if (n >= 0) {
        $li.eq(n).addClass('active').siblings().removeClass('active');
        // 执行 a 标签的点击事件
        $li.eq(n).find('a')[0].click()
    }
}

// 一般页面的iframe的高度是660
// 新闻发布页面iframe的高度是900
function fnSetIframeHeight(num) {
    var $frame = $('#main_frame');
    $frame.css({'height': num});
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

function generateUUID() {
    var d = new Date().getTime();
    if (window.performance && typeof window.performance.now === "function") {
        d += performance.now(); //use high-precision timer if available
    }
    var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        var r = (d + Math.random() * 16) % 16 | 0;
        d = Math.floor(d / 16);
        return (c == 'x' ? r : (r & 0x3 | 0x8)).toString(16);
    });
    return uuid;
}
