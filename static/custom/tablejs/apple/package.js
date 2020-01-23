layui.use(['admin', 'form', 'upload', 'table'], ()=>{
  var $ = layui.$
  ,admin = layui.admin
  ,element = layui.element
  ,form = layui.form
  ,view = layui.view
  ,upload = layui.upload
  ,table = layui.table

  // 表格初始化
  table.init('packages_table', {
    elem: '#packages_table'
      // ,data: table_datas
      ,toolbar: "#packages_table_toolbar"
      ,defaultToolbar: ['filter', 'exports']
      ,title: '苹果账号表'
      ,limit: 20
      ,limits: [20, 50, 100, 500]
      ,cols: [[
        // {type: 'checkbox', fixed: 'left'}
        // ,{field:'name', title:'包名', sort:true, event: 'setSign'}
        ,{field:'id', title:'ID', sort:true}
        ,{field:'name', title:'包名', sort:true}
        ,{field:'count', title:'已安装次数', sort:true}
        ,{field:'version', title:'版本', sort:true}
        ,{field:'mini_version', title:'最低适配', sort:true}
        ,{field:'bundle_identifier', title:'bundleId', sort:true}
        ,{field:'ipa', title:'ipa', sort:true, hide: true}
        ,{field:'mobileconfig', title:'mobileconfig', sort:true}
        ,{field:'customer', title:'业主', sort:true}
        ,{field:'status', title:'状态', templet: '#switchpackageStatus', width: 150}
        ,{field:'operate', title:'操作', toolbar: '#packages_table_operatebar', fixed: 'right', width: 200}
      ]]
      ,height:530
      ,page: true
  })

  //监听锁定操作
  form.on('checkbox(switch_package_status)', function(obj){
    var data = JSON.parse(decodeURIComponent($(this).data('json')));
    
    if (obj.elem.checked){
      data.status = 1;
      var message = "账号状态 启用";
    }else {
      data.status = 0;
      var message = "账号状态 禁用";
    }

    var postData = { // 获取表单数据
      'records': [data],
      'id': data.id,
      'status': data.status,
    };

    loading1.call(this); // 打开 等待的弹层
    admin.req({
      url: '/apple/package/edit' //实际使用请改成服务端真实接口code == 1001
      ,method: "post" 
      ,data: JSON.stringify(postData)
      ,contentType: 'application/json'
      ,done: function(res){
        // 发送成功的提示
        layer.msg(res.msg, {
          offset: '15px'
          ,icon: 1
          ,time: 1500
        });
        // 更新原始表格中的数据
        for (var x in layui.setter.packages_table_data){
          if (layui.setter.packages_table_data[x].id == data.id){
            layui.setter.packages_table_data[x].status = data.status;
            break;
          }
        }

        table.reload('packages_table', {
          data: layui.setter.packages_table_data
        })


        layer.close(loading1_iii); // 关闭 等待的弹层

      },success:function(res){
        if (res.code == 1001){ // 登陆失效
          layer.msg(res.msg, {
            offset: '15px'
            ,icon: 1
            ,time: 1500
          })
        };
        layer.close(loading1_iii);
      }
      
    });

  });

  //监听单元格事件
  table.on('tool(packages_table)', function(obj){
    var data = obj.data;
    layui.data.package_data = data;
    if(obj.event === 'setSign'){
      admin.popup({
        title: '账号: ' + data.account + ' 创建证书'
        ,offset: "auto" // t: top
        ,area: ['700px', '550px']
        // ,id: 'LAY-popup-user-add'
        ,fixed: true
        // ,closeBtn: 1
        ,success: function(layero, index){
          view(this.id).render('apple/create/operate/index').done(function(){
            form.render(null, 'apple-account-form');
            
            //监听提交
            form.on('submit(apple-account-form-submit)', function(){

              loading1.call(this); // 打开 等待的弹层

              admin.req({
                url: '/apple/cer/create' //实际使用请改成服务端真实接口code == 1001
                ,method: "post" 
                ,data: {'id': data.id}
                // ,contentType: 'application/json'
                ,done: function(res){
                  // 发送成功的提示
                  layer.msg(res.msg, {
                    offset: '15px'
                    ,icon: 1
                    ,time: 3000
                  });
                  layer.close(loading1_iii); // 关闭 等待的弹层
                  // layer.close(index); //执行关闭 
                },success:function(res){
                  if (res.code == 1001){ // 登陆失效
                    layer.msg(res.msg, {
                      offset: '15px'
                      ,icon: 1
                      ,time: 1500
                    })
                  };
                  layer.close(loading1_iii);
                }
                
              });

              return false;


              // layer.close(index); //执行关闭 
            });
          });
        }
      });
    }else if(obj.event === 'mobileconfig_create'){
      loading1.call(this); // 打开 等待的弹层

      admin.req({
        url: '/apple/package/mobileconfig/create' //实际使用请改成服务端真实接口code == 1001
        ,method: "post" 
        ,data: {'id': data.id}
        // ,contentType: 'application/json'
        ,done: function(res){
          // 发送成功的提示
          layer.msg(res.msg, {
            offset: '15px'
            ,icon: 1
            ,time: 1500
          });
          // layui.setter.packages_table_data = res.data;
          // layui.setter.packages_table_postdata = postData;
          // table.reload('packages_table', {
          //   data: res.data
          // });
          layer.close(loading1_iii); // 关闭 等待的弹层
        },success:function(res){
          if (res.code == 1001){ // 登陆失效
            layer.msg(res.msg, {
              offset: '15px'
              ,icon: 1
              ,time: 1500
            })
          };
          layer.close(loading1_iii);
        }
        
      });

      return false;

    }
  });

});