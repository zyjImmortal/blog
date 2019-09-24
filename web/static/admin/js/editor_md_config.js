$(function () {
    testEditor = editormd("editormd", {
        width: "90%",
        height: 720,
        watch: false,
        toolbar: true,
        codeFold: true,
        // searchReplace: true,
        placeholder: "Enjoy coding!",
        htmlDecode: true,
        // htmlDecode : "style,script,iframe,sub,sup|on*"
        ocm: true, // Using [TOCM]
        tex: true, // 开启科学公式TeX语言支持，默认关闭
        flowChart: true, // 开启流程图支持，默认关闭
        // value: (localStorage.mode) ? $("#" + localStorage.mode.replace("text/", "") + "-code").val() : $("#html-code").val(),
        // theme: (localStorage.theme) ? localStorage.theme : "default",
        // mode: (localStorage.mode) ? localStorage.mode : "text/html",
        path: '../../static/admin/editor-md/lib/',
        saveHTMLToTextarea: true,
        previewCodeHighlight: true,
        toolbarIcons: function () {
            // Or return editormd.toolbarModes[name]; // full, simple, mini
            // Using "||" set icons align right.
            return ["undo", "redo", "|", "bold", "italic", "quote", "uppercase", "lowercase", "|", "h1", "h2", "h3", "h4", "|", "list-ul", "list-ol", "hr", "|", "link", "image", "code", "code-block", "table", "html-entities", "|", "watch", "preview", "fullscreen", "clear", "|", "help"]
        }
    });
});