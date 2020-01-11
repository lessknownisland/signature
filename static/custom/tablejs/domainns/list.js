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
  table.init('domains_table', {
    elem: '#domains_table'
      // ,data: table_datas
      ,toolbar: "#domains_table_toolbar"
      ,defaultToolbar: ['filter']
      ,title: 'CF域名表'
      ,limit: 20
      ,limits: [20, 50, 100, 500]
      ,cols: [[
        {type: 'checkbox', fixed: 'left'}
        ,{field:'name', title:'域名', sort:true, width: 300}
        ,{field:'product', title:'产品', sort:true, templet: function(d){
          return d.product[1];
        }}
        ,{field:'customer', title:'客户', sort:true, templet: function(d){
          return d.customer[1];
        }}
        ,{field:'group', title:'所属组', sort:true, templet: function(d){
          return d.group.group;
        }}
        ,{field:'cdn', title:'CDN', sort:true, templet: function(d){
            var list = [];
            for (var index in d.cdn){
              var item = d.cdn[index];
              list.push(item.name+"_"+item.account)
            }
            return list.join('<br>');
          }}
        ,{field:'cf', title:'CloudFlare', sort:true, templet: function(d){
            var list = [];
            for (var index in d.cf){
              var item = d.cf[index];
              list.push(item.name+"_"+item.account)
            }
            return list.join('<br>');
          }}
        ,{field:'content', title:'备注', sort:true}
        ,{field:'status', title:'状态', templet: '#switchDomainStatus', unresize: true, sort:true, fixed: 'right'}
      ]]
      ,height:530
      ,page: true
  })

  //监听锁定操作
  form.on('checkbox(switch_domain_status)', function(obj){
    var data = JSON.parse(decodeURIComponent($(this).data('json')));
    
    if (obj.elem.checked){
      data.status = 1;
      var message = "域名状态 启用";
    }else {
      data.status = 0;
      var message = "域名状态 禁用";
    }

    var postData = { // 获取表单数据
      'records': [data],
      'name': [data.name],
      'status': data.status,
      'product': data.product[0],
      'customer': data.customer[0],
      'group': data.group.id,
      'content': data.content,
      'cdn_status': false,
      'cf_status': false,
    };

    loading1.call(this); // 打开 等待的弹层
    admin.req({
      url: '/domainns/domain/edit_records' //实际使用请改成服务端真实接口code == 1001
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
        for (var x in layui.setter.domains_table_data){
          if (layui.setter.domains_table_data[x].id == data.id){
            layui.setter.domains_table_data[x].status = data.status;
            break;
          }
        }

        table.reload('domains_table', {
          data: layui.setter.domains_table_data
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

  //头工具栏事件
  table.on('toolbar(domains_table)', function(obj){
    var checkStatus = table.checkStatus(obj.config.id);
    switch(obj.event){
      case 'domain_add': // 新增域名
        admin.popup({
          title: '新增域名'
          ,offset: "t" 
          ,area: ['1000px', '700px']
          ,id: 'LAY-popup-user-add'
          ,success: function(layero, index){
            view(this.id).render('domainns/list/add').done(function(){
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
        
      break;
      case 'domain_edit': 
        layui.setter.domain_edit_datas = checkStatus.data;
        if (layui.setter.domain_edit_datas.length == 0){
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
            view(this.id).render('domainns/list/edit').done(function(){
              form.render(null, 'domain-edit-form');
              
              //监听提交
              form.on('submit(domain-edit-form-submit)', function(data){
                var postData = {
                  'records': layui.setter.domain_edit_datas,
                  'status': parseInt(data.field.domain_edit_status),
                  'cdn': data.field.domain_edit_cdn,
                  'cf': false,
                  'product': parseInt(data.field.domain_edit_product),
                  'customer': parseInt(data.field.domain_edit_customer),
                  'group': parseInt(data.field.domain_edit_group),
                  'name': data.field.domain_edit_name.split('\n').map(function (val) {
                      if (val.replace(/\s+/g, '') != ''){
                        return val.replace(/\s+/g, '');
                      }
                    }),
                  'content': data.field.domain_edit_content,
                  'cdn_status': data.field.domain_cdn_status,
                  'cf_status': data.field.domain_cf_status,
                }

                if (data.field.domain_edit_cf.length != 0){
                  postData['cf'] = parseInt(data.field.domain_edit_cf);
                }

                if (data.field.domain_edit_cdn.length == 0){
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
                if (postData['name'].length != layui.setter.domain_edit_datas.length){
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
                  url: '/domainns/domain/edit_records' //实际使用请改成服务端真实接口code == 1001
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
      case 'domain_delete': 
      layui.setter.domain_delete_datas = checkStatus.data;
      if (layui.setter.domain_delete_datas.length == 0){
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
          view(this.id).render('domainns/list/delete').done(function(){
            form.render(null, 'domain-delete-form');
            
            //监听提交
            form.on('submit(domain-delete-form-submit)', function(data){
              var postData = {
                'records': layui.setter.domain_delete_datas,
              }

              loading1.call(this); // 打开 等待的弹层

              admin.req({
                url: '/domainns/domain/delete_records' //实际使用请改成服务端真实接口code == 1001
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
                  for (var x in layui.setter.domain_delete_datas){
                    for (var y in layui.setter.domains_table_data){
                      if (layui.setter.domain_delete_datas[x].id == layui.setter.domains_table_data[y].id){
                        layui.setter.domains_table_data.splice(y, 1)
                      }
                    }
                  }
                  table.reload('domains_table', {
                    data: layui.setter.domains_table_data
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