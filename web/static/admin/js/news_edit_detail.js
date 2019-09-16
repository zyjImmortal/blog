function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(function(){
    $(".news_edit").submit(function (e) {
        e.preventDefault()
        // TODO 新闻编辑提交
        $(this).ajaxSubmit({
            url: "",
            type:"post",
            headers:{
                "X-CSRFToken": getCookie("csrf_token")
            },
            success:function (response) {
                if (resp.errno === "0") {
                    // 返回上一页，刷新数据
                    location.href = document.referrer;
                } else {
                    alert(resp.errmsg);
                }
            }
        })
    })
});

// 点击取消，返回上一页
function cancel() {
    history.go(-1)
}