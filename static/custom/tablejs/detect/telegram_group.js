$(function () {
    operate.operateInit();
});

// 全局变量
window.modal_results = document.getElementById("OperateRestartresults");
window.modal_footer = document.getElementById("progressFooter");
window.modal_head = document.getElementById("progress_head");
window.group = []

//升级所用到的全局变量
window.upgrade_postData = {};

//初始化fileinput
var FileInput = function (group) {
    var oFile = new Object();

    //初始化fileinput控件（第一次初始化）
    oFile.Init = function(ctrlName, uploadUrl) {
    var control = $('#' + ctrlName);

    //初始化上传控件的样式
    control.fileinput({
        language: 'zh', //设置语言
        uploadUrl: uploadUrl, //上传的地址
        allowedFileExtensions: ['jpg', 'gif', 'png'],//接收的文件后缀
        showUpload: true, //是否显示上传按钮
        showCaption: false,//是否显示标题
        browseClass: "btn btn-primary", //按钮样式     
        //dropZoneEnabled: false,//是否显示拖拽区域
        //minImageWidth: 50, //图片的最小宽度
        //minImageHeight: 50,//图片的最小高度
        //maxImageWidth: 1000,//图片的最大宽度
        //maxImageHeight: 1000,//图片的最大高度
        //maxFileSize: 0,//单位为kb，如果为0表示不限制文件大小
        //minFileCount: 0,
        maxFileCount: 10, //表示允许同时上传的最大文件个数
        enctype: 'multipart/form-data',
        validateInitialCount:true,
        previewFileIcon: "<i class='glyphicon glyphicon-king'></i>",
        msgFilesTooMany: "选择上传的文件数量({n}) 超过允许的最大数值{m}！",
        uploadIcon: '',
        uploadTitle: '发送',
        uploadLabel: '发送',
        // ajaxSettings: {data: JSON.stringify({
        //     'group': group,
        // }),},
    });

    //导入文件上传完成之后的事件
    $("#txt_file").on("fileuploaded", function (event, data, previewId, index) {
        // $("#uploadimgs").modal("hide");
        // var data = data.response.lstOrderImport;
        // if (data == undefined) {
        //     toastr.error('文件格式类型不正确');
        //     return;
        // }
        //1.初始化表格
        // var oTable = new TableInit();
        // oTable.Init(data);
        // $("#div_startimport").show();

    });
    }
    return oFile;
};

//操作
var operate = {
    //初始化按钮事件
    operateInit: function () {
        this.DisplayPanel();
        //this.Getform();
        //this.Submit();
        //this.showSelectedValue();
        //this.Exe();
    },

    DisplayPanel: function (){
        $("#command_panel").bind('click',function () {
            that = document.getElementById("command_form")
            if (that.style.display == "none"){
                that.style.display = "inline";
                document.getElementById('command_panel').innerHTML = "-";
                document.getElementById('command_panel').title = "隐藏";
            }else {
                that.style.display = "none";
                document.getElementById('command_panel').innerHTML = "+";
                document.getElementById('command_panel').title = "展开";
            }
        });
    },

    Uploadimgs: function(){
        // 获取要发送信息的群组
        group = public.showSelectedValue('telegram_group', false)
        // console.log(group)
        if (group.length == 0 ){
            alert('请选择对应的telegram群组！');
            return false;
        }

        // 获取要@的部门或者组
        atUsers = public.showSelectedValue('telegram_atusers', false)
        // console.log(atUsers)

        // 获取信息文本
        text = document.getElementById('textarea_telegram_text').value

        //0.初始化fileinput
        var oFileInput = new FileInput(group);
        oFileInput.Init("txt_file", "/message/telegram/uploadimgs?group=" + group +"&text=" + text + "&atUsers=" + atUsers);

        $('#uploadimgs').modal('show');
    },

    Submit: function(submit){
        // 获取要发送信息的群组
        group = public.showSelectedValue('telegram_group', false)
        // console.log(group)
        if (group.length == 0 ){
            alert('请选择对应的telegram群组！');
            return false;
        }

        // 获取要@的部门或者组
        atUsers = public.showSelectedValue('telegram_atusers', false)
        // console.log(atUsers)

        // 获取信息文本
        text = document.getElementById('textarea_telegram_text').value
        // console.log(text)

        if (text.length == 0){
            alert('信息不能为空！');
            return false;
        }

        var postData = {
            'group':   group,
            'atUsers': atUsers,
            'text':    text
        }

        $('#runprogress').modal('show');
        modal_results.innerHTML = "";
        modal_footer.innerHTML = "";
        $("#progress_bar").css("width", "30%");
        modal_head.innerHTML = "操作进行中，请勿刷新页面......";

        $.ajax({
            url: "/message/telegram/sendgroupmessage",
            type: "post",
            data: JSON.stringify(postData),
            success: function (data, status) {
                if (status == 1){
                    toastr.success(data);
                }else {
                    toastr.warning(data);
                }
                modal_head.innerHTML = "执行完成...";
                $("#progress_bar").css("width", "100%");
                $('#OperateRestartresults').append('<p>执行完成......</p>' );
                //console.log('websocket已关闭');
                setTimeout(function(){$('#runprogress').modal('hide');}, 1000);
            },
            error: function(XMLHttpRequest, textStatus, errorThrown){
                if (XMLHttpRequest.status == 0){
                    toastr.error('后端服务不响应', '错误')
                }else {
                    toastr.error(XMLHttpRequest.responseText, XMLHttpRequest.status)
                }
                modal_head.innerHTML = "与服务器连接失败...";
                $('#OperateRestartresults').append('<p>连接失败......</p>' );
                setTimeout(function(){$('#runprogress').modal('hide');}, 1000);

                //console.info(XMLHttpRequest)
                //alert(XMLHttpRequest.status+': '+XMLHttpRequest.responseText);
                //tableInit.myViewModel.refresh();
            }
        });

        return false;
    },

};