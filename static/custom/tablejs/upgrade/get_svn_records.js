$(function () {
    svn.operateInit();
});

window.svn_list = {'item': []}

//操作
var svn = {
    //初始化按钮事件
    operateInit: function () {
        //this.GetSvnRecords();
        //this.getItemsValue();
    },

    GetSvnRecords: function(data, value){
        var postData = data;
        toastr.info("正在获取数据，请耐心等待返回...");

        postData['key'] = value;

        if (public.isStrinList('gray_env', postData['codeEnv'])){
            url = "/upgrade/get_svn_records";
            value = false;
        }else if(postData['codeEnv'][0] == 'online_env'){
            url = "/upgrade/get_svn_lock_records";
            value = true;
        }

        $.ajax({
            url: url,
            type: "post",
            contentType: 'application/json',
            data: JSON.stringify(postData),
            success: function (datas, status) {
                //alert(datas);
                var data = eval(datas);
                initData = [];
                $.each(data, function (index, item) { 
                    initData.push({
                        'revision':   item.revision,
                        'date':       item.date,
                        'author':     item.author,
                        'log':        item.log,
                        'changelist': item.changelist,
                    })
                });
                //console.log(initData);
                tableInit.myViewModel.load(initData.sort(public.compare('revision', value)));
                toastr.success('数据获取成功！');
                public.disableButtons(['btn_commit_upgrade'], false);
            },
            error:function(msg){
                alert("获取项目失败！");
                public.disableButtons(['btn_commit_upgrade'], true);
                return false;
            }
        });
    },
    
    selectpicker: function docombjs() {
        $('.selectpicker').selectpicker({
            style: 'btn-default',
            //width: "auto",
            size: 15,
            showSubtext:true,
        });
    },
};