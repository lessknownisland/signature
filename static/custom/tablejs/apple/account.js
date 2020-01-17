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
      ,defaultToolbar: ['filter']
      ,title: 'CF域名表'
      ,limit: 20
      ,limits: [20, 50, 100, 500]
      ,cols: [[
        {type: 'checkbox', fixed: 'left'}
        ,{field:'account', title:'账号', sort:true, event: 'setSign', width: 300}
        ,{field:'count', title:'剩余次数', sort:true, width: 100}
        ,{field:'p12', title:'p12', sort:true}
        ,{field:'cer_content', title:'证书文本', sort:true, templet: function(d){
            return d.cer_content;
          }}

        ,{field:'status', title:'状态', templet: '#switchAppleAccountStatus', unresize: true, sort:true, fixed: 'right'}
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
    if(obj.event === 'setSign'){
      admin.popup({
        title: '账号: ' + data.account
        ,offset: "auto" // t: top
        ,area: ['500px', '350px']
        ,id: 'LAY-popup-user-add'
        ,success: function(layero, index){
          view(this.id).render('apple/create/operate/index').done(function(){
            form.render(null, 'domain-add-form');
            
            //监听提交
            form.on('submit(domain-add-form-submit)', function(data){
              var postData = {
                'status': parseInt(data.field.domain_add_status),
                'cdn': data.field.domain_add_cdn,
                'cf': false,
                'product': parseInt(data.field.domain_add_product),
                'customer': parseInt(data.field.domain_add_customer),
                'group': parseInt(data.field.domain_add_group),
                'name': data.field.domain_add_name.split('\n').map(function (val) {
                    if (val.replace(/\s+/g, '') != ''){
                      return val.replace(/\s+/g, '');
                    }
                  }),
                'content': data.field.domain_add_content
              }

              if (data.field.domain_add_cf.length != 0){
                postData['cf'] = parseInt(data.field.domain_add_cf);
              }

              if (data.field.domain_add_cdn.length == 0){
                postData['cdn'] = []
              }else {
                postData['cdn'] = postData['cdn'].split(',').map(function (val) {return parseInt(val);})
              }

              // 验证域名的 name
              layui.each(postData['name'], function(index, item){
                var reg = /^(http:\/\/|https:\/\/)(.*[-a-zA-Z0-9]+.*\.[-a-zA-Z0-9]*[-a-zA-Z]+[-a-zA-Z0-9]*)((\/[0-9a-zA-Z_!~*\'().;?:@&=+$,%#-]+)+\/?)?$/;
                if (! reg.test(item)){
                  layer.msg(item + ': 域名URL格式不正确', {
                    offset: '15px'
                    ,shift: 6
                    ,icon: 5
                    ,time: 1500
                  });
                  return false;
                }
              });


              loading1.call(this); // 打开 等待的弹层

              admin.req({
                url: '/domainns/domain/add_records' //实际使用请改成服务端真实接口code == 1001
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
                  layer.close(loading1_iii); // 关闭 等待的弹层
                  layer.close(index); //执行关闭 
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
    }
  });

  //头工具栏事件
  table.on('toolbar(apple_accounts_table)', function(obj){
    var checkStatus = table.checkStatus(obj.config.id);
    switch(obj.event){
      case 'apple_account_add': // 新增域名
        admin.popup({
          title: '新增域名'
          ,offset: "t" 
          ,area: ['1000px', '700px']
          ,id: 'LAY-popup-user-add'
          ,success: function(layero, index){
            view(this.id).render('apple_accountns/list/add').done(function(){
              form.render(null, 'apple_account-add-form');
              
              //监听提交
              form.on('submit(apple_account-add-form-submit)', function(data){
                var postData = {
                  'status': parseInt(data.field.apple_account_add_status),
                  'cdn': data.field.apple_account_add_cdn,
                  'cf': false,
                  'product': parseInt(data.field.apple_account_add_product),
                  'customer': parseInt(data.field.apple_account_add_customer),
                  'group': parseInt(data.field.apple_account_add_group),
                  'name': data.field.apple_account_add_name.split('\n').map(function (val) {
                      if (val.replace(/\s+/g, '') != ''){
                        return val.replace(/\s+/g, '');
                      }
                    }),
                  'content': data.field.apple_account_add_content
                }

                if (data.field.apple_account_add_cf.length != 0){
                  postData['cf'] = parseInt(data.field.apple_account_add_cf);
                }

                if (data.field.apple_account_add_cdn.length == 0){
                  postData['cdn'] = []
                }else {
                  postData['cdn'] = postData['cdn'].split(',').map(function (val) {return parseInt(val);})
                }

                // 验证域名的 name
                layui.each(postData['name'], function(index, item){
                  var reg = /^(http:\/\/|https:\/\/)(.*[-a-zA-Z0-9]+.*\.[-a-zA-Z0-9]*[-a-zA-Z]+[-a-zA-Z0-9]*)((\/[0-9a-zA-Z_!~*\'().;?:@&=+$,%#-]+)+\/?)?$/;
                  if (! reg.test(item)){
                    layer.msg(item + ': 域名URL格式不正确', {
                      offset: '15px'
                      ,shift: 6
                      ,icon: 5
                      ,time: 1500
                    });
                    return false;
                  }
                });


                loading1.call(this); // 打开 等待的弹层

                admin.req({
                  url: '/apple_accountns/apple_account/add_records' //实际使用请改成服务端真实接口code == 1001
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
                    layer.close(loading1_iii); // 关闭 等待的弹层
                    layer.close(index); //执行关闭 
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
        
      break;
      case 'apple_account_edit': 
        layui.setter.apple_account_edit_datas = checkStatus.data;
        if (layui.setter.apple_account_edit_datas.length == 0){
          layer.msg('请至少选择一行数据', {
              offset: '15px'
              ,shift: 6
              ,icon: 5
              ,time: 1500
          });
          return false;
        }

        admin.popup({
          title: '修改域名'
          ,offset: "t" 
          ,area: ['1000px', '700px']
          ,id: 'LAY-popup-user-edit'
          ,success: function(layero, index){
            view(this.id).render('apple_accountns/list/edit').done(function(){
              form.render(null, 'apple_account-edit-form');
              
              //监听提交
              form.on('submit(apple_account-edit-form-submit)', function(data){
                var postData = {
                  'records': layui.setter.apple_account_edit_datas,
                  'status': parseInt(data.field.apple_account_edit_status),
                  'cdn': data.field.apple_account_edit_cdn,
                  'cf': false,
                  'product': parseInt(data.field.apple_account_edit_product),
                  'customer': parseInt(data.field.apple_account_edit_customer),
                  'group': parseInt(data.field.apple_account_edit_group),
                  'name': data.field.apple_account_edit_name.split('\n').map(function (val) {
                      if (val.replace(/\s+/g, '') != ''){
                        return val.replace(/\s+/g, '');
                      }
                    }),
                  'content': data.field.apple_account_edit_content,
                  'cdn_status': data.field.apple_account_cdn_status,
                  'cf_status': data.field.apple_account_cf_status,
                }

                if (data.field.apple_account_edit_cf.length != 0){
                  postData['cf'] = parseInt(data.field.apple_account_edit_cf);
                }

                if (data.field.apple_account_edit_cdn.length == 0){
                  postData['cdn'] = []
                }else {
                  postData['cdn'] = postData['cdn'].split(',').map(function (val) {return parseInt(val);})
                }

                if (postData['cdn_status'] == "on"){
                  postData['cdn_status'] = true;
                }else {
                  postData['cdn_status'] = false;
                }
                if (postData['cf_status'] == "on"){
                  postData['cf_status'] = true;
                }else {
                  postData['cf_status'] = false;
                }

                // 验证域名的 name
                is_continue = true;
                layui.each(postData['name'], function(index, item){
                  var reg = /^(http:\/\/|https:\/\/)(.*[-a-zA-Z0-9]+.*\.[-a-zA-Z0-9]*[-a-zA-Z]+[-a-zA-Z0-9]*)(((\/[0-9a-zA-Z_!~*\'().;?:@&=+$,%#-]+)+\/?)?|(\/)?)$/;
                  if (! reg.test(item)){
                    layer.msg(item + ': 域名URL格式不正确', {
                      offset: '15px'
                      ,shift: 6
                      ,icon: 5
                      ,time: 1500
                    });
                    is_continue = false;
                  }
                });

                if (! is_continue){ // 在layui.each 里面return false 不会退出执行，故写在外面
                  return false;
                }

                // 检查修改后，域名name的数量对比
                if (postData['name'].length != layui.setter.apple_account_edit_datas.length){
                  layer.msg('域名URL 和选中域名数量不一致，请检查', {
                    offset: '15px'
                    ,shift: 6
                    ,icon: 5
                    ,time: 1500
                  });
                  return false;
                }

                loading1.call(this); // 打开 等待的弹层

                admin.req({
                  url: '/apple_accountns/apple_account/edit_records' //实际使用请改成服务端真实接口code == 1001
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
                    layer.close(loading1_iii); // 关闭 等待的弹层
                    layer.close(index); //执行关闭 
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
      break;
      case 'apple_account_delete': 
      layui.setter.apple_account_delete_datas = checkStatus.data;
      if (layui.setter.apple_account_delete_datas.length == 0){
          layer.msg('请至少选择一行数据', {
            offset: '15px'
            ,shift: 6
            ,icon: 5
            ,time: 1500
        });
        return false;
      }

      admin.popup({
        title: '删除域名'
        ,offset: "t" 
        ,area: ['1000px', '700px']
        ,id: 'LAY-popup-user-delete'
        ,success: function(layero, index){
          view(this.id).render('apple_accountns/list/delete').done(function(){
            form.render(null, 'apple_account-delete-form');
            
            //监听提交
            form.on('submit(apple_account-delete-form-submit)', function(data){
              var postData = {
                'records': layui.setter.apple_account_delete_datas,
              }

              loading1.call(this); // 打开 等待的弹层

              admin.req({
                url: '/apple_accountns/apple_account/delete_records' //实际使用请改成服务端真实接口code == 1001
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

                  // 将删除的域名剔除数据列表
                  for (var x in layui.setter.apple_account_delete_datas){
                    for (var y in layui.setter.apple_accounts_table_data){
                      if (layui.setter.apple_account_delete_datas[x].id == layui.setter.apple_accounts_table_data[y].id){
                        layui.setter.apple_accounts_table_data.splice(y, 1)
                      }
                    }
                  }
                  table.reload('apple_accounts_table', {
                    data: layui.setter.apple_accounts_table_data
                  })

                  layer.close(loading1_iii); // 关闭 等待的弹层
                  layer.close(index); //执行关闭 
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


      break;

    };
    
  });

});