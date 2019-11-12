$(function () {
    testEditor = editormd.markdownToHTML("editormd-content", {
        htmlDecode: "style,script,iframe", //可以过滤标签解码
        emoji: true,
        taskList: true,
        tex: true,               // 默认不解析
        flowChart: true,         // 默认不解析
        sequenceDiagram: true, // 默认不解析
        codeFold: true

    });
});