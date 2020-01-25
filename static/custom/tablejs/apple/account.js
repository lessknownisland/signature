layui.use(['admin', 'form', 'formSelects', 'upload', 'table'], ()=>{
  var $ = layui.$
  ,admin = layui.admin
  ,element = layui.element
  ,form = layui.form
  ,view = layui.view
  ,upload = layui.upload
  ,table = layui.table
  ,formSelects = layui.formSelects;

  // 表格初始化
  table.init('apple_accounts_table', {
    elem: '#apple_accounts_table'
      // ,data: table_datas
      ,toolbar: "#apple_accounts_table_toolbar"
      ,defaultToolbar: ['filter', 'exports']
      ,title: '苹果账号表'
      ,limit: 20
      ,limits: [20, 50, 100, 500]
      ,cols: [[
        {type: 'checkbox', fixed: 'left'}
        ,{field:'id', title:'ID', sort:true}
        ,{field:'account', title:'账号', sort:true, width: 300}
        ,{field:'count', title:'剩余次数', sort:true, width: 100}
        ,{field:'cer_id', title:'cer_id', sort:true, event: 'setSign', width: 150, style:'background-color: #FFB800; color: #fff;', templet: function(d){
          if (!d.cer_id){
            return "创建证书";
          }else {
            return d.cer_id;
          }
        }}
        ,{field:'bundleId', title:'bundleId', sort:true}
        ,{field:'bundleIds', title:'bundleIds', sort:true}
        ,{field:'p12', title:'p12', sort:true}
        ,{field:'cer_content', title:'证书文本', sort: true, hide: true}
        ,{field:'status', title:'状态', templet: '#switchAppleAccountStatus', width: 150}
        ,{field:'operate', title:'操作', toolbar: '#apple_accounts_table_operatebar', fixed: 'right', width: 300}
        ,{field:'operate', title:'危险操作', toolbar: '#apple_accounts_table_dangerousoperatebar', fixed: 'right', width: 100}
      ]]
      ,height:530
      ,page: true
  })

  //监听锁定操作
  form.on('checkbox(switch_apple_account_status)', function(obj){
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
      url: '/apple/account/edit' //实际使用请改成服务端真实接口code == 1001
      ,method: "post" 
      ,data: JSON.stringify(postData)
      ,contentType: 'application/json'
      ,done: function(res){
        // 发送成功的提示
        layer.msg(message, {
          offset: '15px'
          ,icon: 1
          ,time: 1500
        });
        // 更新原始表格中的数据
        for (var x in layui.setter.apple_accounts_table_data){
          if (layui.setter.apple_accounts_table_data[x].id == data.id){
            layui.setter.apple_accounts_table_data[x].status = data.status;
            break;
          }
        }

        table.reload('apple_accounts_table', {
          data: layui.setter.apple_accounts_table_data
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
  table.on('tool(apple_accounts_table)', function(obj){
    var data = obj.data;
    layui.data.apple_account_data = data;
    if(obj.event === 'setSign'){

      // var oss_bucket = layui.data.apple_account_oss_bucket.getValue();

      // if (oss_bucket.length !== 1){
      //   layer.msg('请选择Oss Bucket', { // 如果证书文本不存在，则提示
      //     offset: '15px'
      //     ,icon: 1
      //     ,time: 1500
      //   })
      //   return false;
      // }

      admin.popup({
        title: '账号: ' + data.account + ' 创建新证书'
        ,offset: "auto" // t: top
        ,area: ['700px', '550px']
        // ,id: 'LAY-popup-user-add'
        ,fixed: true
        // ,closeBtn: 1
        ,success: function(layero, index){
          view(this.id).render('apple/create/operate/index').done(function(){
            form.render(null, 'apple-account-form');
            
            //监听提交
            form.on('submit(apple-account-createcer-form)', function(form_data){

              loading1.call(this); // 打开 等待的弹层

              admin.req({
                url: '/apple/cer/create' //实际使用请改成服务端真实接口code == 1001
                ,method: "post" 
                ,data: {
                    'id': data.id,
                    'csr': form_data.field.apple_csr,
                    // 'oss_bucket_id': oss_bucket[0].value,
                  }
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
    }else if(obj.event === 'base64_cer'){
      if (!data.cer_content){
        layer.msg('证书文本为空，请先创建证书', { // 如果证书文本不存在，则提示
          offset: '15px'
          ,icon: 1
          ,time: 1500
        })
        return false;
      }

      // 下面开始将证书文本加密成cer 文件
      // console.log(atob(data.cer_content));
      var cer = public.converBase64toBlob(data.cer_content)
      public.createAndDownloadFile(data.cer_id+'.cer', cer);
    }else if(obj.event === 'upload_p12'){

      var oss_bucket = layui.data.apple_account_oss_bucket.getValue();

      if (oss_bucket.length !== 1){
        layer.msg('请选择Oss Bucket', { // 如果证书文本不存在，则提示
          offset: '15px'
          ,icon: 1
          ,time: 1500
        })
        return false;
      }

      admin.popup({
        title: '账号: ' + data.account + ' 上传p12'
        ,offset: "auto" // t: top
        ,area: ['700px', '550px']
        // ,id: 'LAY-popup-user-add'
        ,fixed: true
        // ,closeBtn: 1
        ,success: function(layero, index){
          view(this.id).render('apple/create/operate/uploadp12').done(function(){
            form.render(null, 'apple-account-uploadp12-form');

            upload.render({
              elem: '#apple_account_uploadp12_choose'
              ,url: '/apple/p12/upload' 
              ,data: {
                  'id': data.id,
                  'oss_bucket_id': oss_bucket[0].value,
                }
              ,auto: false
              ,accept: 'file'
              ,exts: 'p12'
              ,size: 10 // 限制文件大小，10kb
              //,multiple: true
              ,bindAction: '#apple_account_uploadp12_send'
              ,before: function(){
                loading1.call(this);
              }
              ,done: function(res){
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
                },error: function(){
                  layer.close(loading1_iii);
                }
                
            });

          });
        }
      });
    }else if(obj.event === 'apple_account_delete'){
      layer.confirm('删除：'+ data.account, {
          icon: 3
          ,title:'危险操作，请三思一下'
        },function(index){

          loading1.call(this); // 打开 等待的弹层

          admin.req({
            url: '/apple/account/delete' //实际使用请改成服务端真实接口code == 1001
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

              layer.close(loading1_iii); // 关闭 等待的弹层
              layer.close(index);
              obj.del(); // 删除行
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
    }else if(obj.event === 'test_connect'){

      loading1.call(this); // 打开 等待的弹层

      admin.req({
        url: '/apple/account/testconnect' //实际使用请改成服务端真实接口code == 1001
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

    }
  });

});