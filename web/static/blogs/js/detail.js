function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

function updateCommentCount() {
    var length = $(".comment_list").length;
    console.log(length);
    $(".comment_count").html(length + "条评论");
}


$(function () {
    updateCommentCount();
    // 打开登录框
    $('.comment_form_logout').click(function () {
        $('.login_form_con').show();
    });

    // 收藏
    $(".collection").click(function () {


    });

    // 取消收藏
    $(".collected").click(function () {


    })

    // 评论提交
    $(".comment_form").submit(function (e) {
        e.preventDefault();
        let articleId = $(this).attr("data-article-id");
        let article_comment = $(".comment_input").val();

        if (!article_comment) {
            alert('请输入评论内容');
            return
        }
        let params = {
            "article_id": articleId,
            "content": article_comment
        };
        $.ajax({
            url: "/comment/add",
            type: "post",
            contentType: "application/json",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            data: JSON.stringify(params),
            success: function (resp) {
                if (resp.error_code === 0) {
                    var comment = resp.data;
                    // 拼接内容
                    var comment_html = '';
                    comment_html += '<div class="comment_list">';
                    comment_html += '<div class="person_pic fl">';
                    if (comment.user.avatar_url) {
                        comment_html += '<img src="' + comment.user.avatar_url + '" alt="用户图标">'
                    } else {
                        comment_html += '<img src="../../static/blogs/images/person01.png" alt="用户图标">'
                    }
                    comment_html += '</div>';
                    comment_html += '<div class="user_name fl">' + comment.user.nick_name + '</div>';
                    comment_html += '<div class="comment_text fl">';
                    comment_html += comment.content;
                    comment_html += '</div>';
                    comment_html += '<div class="comment_time fl">' + comment.create_time + '</div>';

                    comment_html += '<a href="javascript:;" class="comment_up fr" data-commentid="' + comment.id + '" data-article-id="' + comment.article_id + '">赞</a>';
                    comment_html += '<a href="javascript:;" class="comment_reply fr">回复</a>';
                    comment_html += '<form class="reply_form fl" data-commentid="' + comment.id + '" data-article-id="' + articleId + '">';
                    comment_html += '<textarea class="reply_input"></textarea>';
                    comment_html += '<input type="button" value="回复" class="reply_sub fr">';
                    comment_html += '<input type="reset" name="" value="取消" class="reply_cancel fr">';
                    comment_html += '</form>';

                    comment_html += '</div>';
                    // 拼接到内容的前面
                    $(".comment_list_con").prepend(comment_html);
                    // 让comment_sub 失去焦点
                    $('.comment_sub').blur();
                    // 清空输入框内容
                    $(".comment_input").val("");
                    updateCommentCount();
                } else {
                    alert(resp.msg)
                }
            }
        })
    });

    $('.comment_list_con').delegate('a,input', 'click', function () {

        var sHandler = $(this).prop('class');

        if (sHandler.indexOf('comment_reply') >= 0) {
            $(this).next().toggle();
        }

        if (sHandler.indexOf('reply_cancel') >= 0) {
            $(this).parent().toggle();
        }

        if (sHandler.indexOf('comment_up') >= 0) {
            var $this = $(this);
            if (sHandler.indexOf('has_comment_up') >= 0) {
                // 如果当前该评论已经是点赞状态，再次点击会进行到此代码块内，代表要取消点赞
                $this.removeClass('has_comment_up')
            } else {
                $this.addClass('has_comment_up')
            }
        }

        if (sHandler.indexOf('reply_sub') >= 0) {
            var $this = $(this)
            var article_id = $this.parent().attr('data-article-id')
            var parent_id = $this.parent().attr('data-commentid')
            var comment = $this.prev().val();

            if (!comment) {
                alert('请输入评论内容')
                return
            }
            var params = {
                "article_id": article_id,
                "content": comment,
                "parent_id": parent_id
            }
            $.ajax({
                url: "/comment/add",
                type: "post",
                contentType: "application/json",
                headers: {
                    "X-CSRFToken": getCookie("csrf_token")
                },
                data: JSON.stringify(params),
                success: function (resp) {
                    if (resp.error_code === 0) {
                        var comment = resp.data
                        // 拼接内容
                        var comment_html = ""
                        comment_html += '<div class="comment_list">'
                        comment_html += '<div class="person_pic fl">'
                        if (comment.user.avatar_url) {
                            comment_html += '<img src="' + comment.user.avatar_url + '" alt="用户图标">'
                        } else {
                            comment_html += '<img src="../../static/blogs/images/person01.png" alt="用户图标">'
                        }
                        comment_html += '</div>'
                        comment_html += '<div class="user_name fl">' + comment.user.nick_name + '</div>'
                        comment_html += '<div class="comment_text fl">'
                        comment_html += comment.content
                        comment_html += '</div>'
                        comment_html += '<div class="reply_text_con fl">'
                        comment_html += '<div class="user_name2">' + comment.parent.user.nick_name + '</div>'
                        comment_html += '<div class="reply_text">'
                        comment_html += comment.parent.content
                        comment_html += '</div>'
                        comment_html += '</div>'
                        comment_html += '<div class="comment_time fl">' + comment.create_time + '</div>'

                        comment_html += '<a href="javascript:;" class="comment_up fr" data-commentid="' + comment.id + '" data-article-id="' + comment.article_id + '">赞</a>'
                        comment_html += '<a href="javascript:;" class="comment_reply fr">回复</a>'
                        comment_html += '<form class="reply_form fl" data-commentid="' + comment.id + '" data-article-id="' + article_id + '">'
                        comment_html += '<textarea class="reply_input"></textarea>'
                        comment_html += '<input type="button" value="回复" class="reply_sub fr">'
                        comment_html += '<input type="reset" name="" value="取消" class="reply_cancel fr">'
                        comment_html += '</form>'

                        comment_html += '</div>'
                        $(".comment_list_con").prepend(comment_html)
                        // 请空输入框
                        $this.prev().val('')
                        // 关闭
                        $this.parent().hide();
                        updateCommentCount()
                    } else {
                        alert(resp.msg)
                    }
                }
            })
        }
    });

    // 关注当前新闻作者
    $(".focus").click(function () {

    })

    // 取消关注当前新闻作者
    $(".focused").click(function () {

    })
})