function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(function () {
    $("#article_add").submit(function (e) {
        e.preventDefault()
        // 添加文章
        $(this).ajaxSubmit({
            url: "/article/add",
            type: "post",
            // contentType:"application/json",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            success: function (response) {
                if (response.error_code === 0) {
                    // 返回上一页，刷新数据
                    location.href = document.referrer;
                } else {
                    alert(response.errmsg);
                }
            }
        })
    })
});

// 点击取消，返回上一页
function cancel() {
    history.go(-1)
}