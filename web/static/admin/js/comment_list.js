function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(function () {
    var $a = $('.edit');  // 通过按钮
    var sId = 0;

    $a.click(function () {
        sHandler = 'edit';
        sId = $(this).parent().siblings().eq(0).html();
        let params = {
            "comment_id": sId,
        };
        //
        $.ajax({
            url: "/cms/comment/delete",
            type: "post",
            contentType: "application/json",
            data: JSON.stringify(params),
            success: function (response) {
                if (response.error_code === 0) {
                    location.reload(true);
                } else {
                    alert(response.msg);
                }
            }
        })

    });
})
// })