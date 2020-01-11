layui.use(['admin', 'form', 'formSelects', 'upload', 'table'], ()=>{
  var $ = layui.$
  ,admin = layui.admin
  ,element = layui.element
  ,form = layui.form
  ,upload = layui.upload
  ,table = layui.table
  ,formSelects = layui.formSelects;

  // 表格初始化
  table.init('cf_domains_table', {
    elem: '#cf_domains_table'
      // ,data: table_datas
      ,toolbar: "#cf_domains_table_toolbar"
      ,defaultToolbar: ['filter']
      ,title: 'CF域名表'
      ,limit: 20
      ,limits: [20, 50, 100, 500]
      ,cols: [[
        {type: 'checkbox', fixed: 'left'}
        ,{field:'cf_acc', title:'CF账号', width: 100,sort:true}
        ,{field:'zone', title:'主域名', sort:true}
        ,{field:'name', title:'域名记录', sort:true}
        ,{field:'type', title:'解析类型', width: 100, sort:true}
        ,{field:'content', title:'解析记录', sort:true}
        ,{field:'proxied', title:'是否开启CF转发', sort:true}
        ,{field:'record_id', title:'记录ID', hide: true}
        ,{field:'zone_id', title:'主域名ID', hide: true}
        ,{fixed: 'right', title:'操作', toolbar: '#cf_domains_table_bar'}
      ]]
      ,height:600
      ,page: true
  })

  //头工具栏事件
  table.on('toolbar(cf_domains_table)', function(obj){
    var checkStatus = table.checkStatus(obj.config.id);
    switch(obj.event){
      case 'cf_domain_search': // 检索已获取的表格数据
        // console.log(layui.setter.cf_domains_table_data);
        var tmp_data = [];
        var search_str = document.getElementById('cf_domain_search_input').value;
        if (! layui.setter.cf_domains_table_data){
          layer.msg('没有任何数据', {
            offset: '15px'
            ,shift: 6
            ,icon: 5
            ,time: 1500
          });
          return false;
        }
        for (index in layui.setter.cf_domains_table_data){
          var zone = layui.setter.cf_domains_table_data[index];
          if (zone['name'].indexOf(search_str) > -1 || zone['content'].indexOf(search_str) > -1){
            tmp_data.push(zone);
          }
        }
        table.reload('cf_domains_table', {
          elem: '#cf_domains_table'
          ,data: tmp_data
        });
        document.getElementById('cf_domain_search_input').value = search_str;
      break;
      case 'cf_domain_edit': 
        var data = checkStatus.data;
        if (data.length == 0){
          layer.msg('请至少选择一行数据', {
            offset: '15px'
            ,shift: 6
            ,icon: 5
            ,time: 1500
        });
        return false;
        }
        var index = layer.open({
          type: 1
          ,title: '请确认修改的参数'
          ,offset: "t" 
          ,area: ['750px', '600px']
          ,content: [
            '<table class="layui-table" id="cf_domains_edit_table" name="cf_domains_edit_table" lay-filter="cf_domains_edit_table"></table>',
            '<div class="layui-form" lay-filter="domain_edit_form">',
            '  <form class="layui-row layui-col-space10 layui-form-item">',
            '      <div class="layui-col-lg5">',
            '        <label class="layui-form-label">解析类型</label>',
            '        <div class="layui-input-block">',
            '            <select name="type" id="type" lay-verify="type" xm-select="type" xm-select-skin="warm" xm-select-height="50px" xm-select-radio>',
            '                <option value="A">A</option>',
            '                <option value="CNAME">CNAME</option>',
            '              </select>',
            '        </div>',
            '      </div>',
            '      <div class="layui-col-lg5">',
            '        <label class="layui-form-label">CF转发</label>',
            '        <div class="layui-input-block">',
            '          <select name="proxied" id="proxied" lay-verify="proxied" xm-select="proxied" xm-select-skin="default" xm-select-height="50px" xm-select-radio>',
            '              <option value="true">true</option>',
            '              <option value="false">false</option>',
            '          </select>',
            '        </div>',
            '      </div>',
            '  </from>',
            '  <div class="layui-form-item layui-col-lg10">',
            '    <label class="layui-form-label">解析记录</label>',
            '    <div class="layui-input-block">',
            '      <input type="text" id="content" name="content" lay-verify="content" placeholder="" autocomplete="off" class="layui-input">',
            '    </div>',
            '  </div>',
            '</div>'
            ].join("")
          ,btn: '提交'
          ,btnAlign: 'r' //按钮居中
          ,shade: 0 //不显示遮罩
          ,success: function(layero, index){
            form.render(null, 'domain_edit_form');
            formSelects.render('type');
            formSelects.render('proxied');

            // 初始化要编辑的表格
            table.render({
              elem: '#cf_domains_edit_table'
              ,data: data 
              ,toolbar: false
              ,cols: [[
                {field:'cf_acc', title:'CF账号'}
                ,{field:'zone', title:'主域名'}
                ,{field:'name', title:'域名记录', width: 200}
                ,{field:'type', title:'解析类型'}
                ,{field:'content', title:'解析记录', width: 250}
                ,{field:'proxied', title:'是否开启CF转发'}
                ,{field:'record_id', title:'记录ID', hide: true}
                ,{field:'zone_id', title:'主域名ID', hide: true}
              ]]
              ,page: false
              ,height: 250
            })
          }
          ,yes: function(){
            var postData = { // 获取表单数据
              'records': data,
              'type': formSelects.value('type', 'valStr'),
              'proxied': formSelects.value('proxied', 'valStr'),
              'content': document.getElementById('content').value
            };
        
            // 验证表单
            if (postData.type == ""){
              layer.msg('请选择解析类型', {
                  offset: '15px'
                  ,shift: 6
                  ,icon: 5
                  ,time: 1500
              });
              return false;
            }
            if (postData.proxied == ""){
              layer.msg('是否开启CF转发', {
                  offset: '15px'
                  ,shift: 6
                  ,icon: 5
                  ,time: 1500
              });
              return false;
            }
            if (postData.type == "A" && ! public.isIp(postData.content)){
              layer.msg('A记录，解析 IP不合法', {
                offset: '15px'
                ,shift: 6
                ,icon: 5
                ,time: 1500
              });
              return false;
            }else if (postData.type == "CNAME" && ! public.isDomain(postData.content)){
              layer.msg('CNAME记录，解析 别名不合法', {
                offset: '15px'
                ,shift: 6
                ,icon: 5
                ,time: 1500
              });
              return false;
            }
        
            loading1.call(this); // 打开 等待的弹层
        
            admin.req({
              url: '/domainns/cloudflare/update_records' //实际使用请改成服务端真实接口code == 1001
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
                // 当查询的主域名超过10 个，不自动刷新
                if (layui.setter.cf_domains_table_postdata.length < 10){
                  loading1.call(this); // 打开 等待的弹层
                  document.getElementById("cfDomainsSendButton").click();
                  layer.close(index); // 关闭当前页
                }
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
      break;

    };
    
  });

  //监听行工具事件
  table.on('tool(cf_domains_table)', function(obj){
    var data = obj.data;
    //console.log(obj)
    if(obj.event === 'cf_domain_del'){
      layer.confirm('删除：'+ data.name, 
        {
          icon: 3
          ,title:'危险操作，请三思一下'
        
        },function(index){

          loading1.call(this); // 打开 等待的弹层

          admin.req({
            url: '/domainns/cloudflare/delete_records' //实际使用请改成服务端真实接口code == 1001
            ,method: "post" 
            ,data: JSON.stringify([data])
            ,contentType: 'application/json'
            ,done: function(res){
              // 发送成功的提示
              layer.msg(res.msg, {
                offset: '15px'
                ,icon: 1
                ,time: 1500
              });

              // 更新原始表格中的数据
              for (x in layui.setter.cf_domains_table_data){
                if (layui.setter.cf_domains_table_data[x].record_id == data.record_id){
                  layui.setter.cf_domains_table_data.splice(x, 1);
                  break;
                }
              }

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
    } else if(obj.event === 'cf_domain_add'){
      var index = layer.open({
        type: 1
        ,title: '请填写相应的参数'
        ,offset: "t" 
        ,area: ['750px', '600px']
        ,content: [
          '<div class="layui-form" lay-filter="domain_add_form" style="margin-top: 20px;">',
          '  <div class="layui-form-item layui-col-lg10">',
          '    <label class="layui-form-label">主域名</label>',
          '    <div class="layui-input-block">',
          '      <input type="text" id="add_zone" name="add_zone" lay-verify="add_zone" placeholder="" autocomplete="off" class="layui-input" value='+data.zone+' disabled>',
          '    </div>',
          '  </div>',
          '  <div class="layui-form-item layui-col-lg10">',
          '    <label class="layui-form-label">记录前缀</label>',
          '    <div class="layui-input-block">',
          '      <textarea name="add_sub_domain" id="add_sub_domain" lay-verify="add_sub_domain" placeholder="主机记录前缀[例如：www]，每行一条" class="layui-textarea" style="height: 150px;" required></textarea>',
          '    </div>',
          '  </div>',
          '  <form class="layui-row layui-col-space10 layui-form-item">',
          '      <div class="layui-col-lg5">',
          '        <label class="layui-form-label">解析类型</label>',
          '        <div class="layui-input-block">',
          '            <select name="add_type" id="add_type" lay-verify="add_type" xm-select="add_type" xm-select-skin="warm" xm-select-height="50px" xm-select-radio>',
          '                <option value="A">A</option>',
          '                <option value="CNAME">CNAME</option>',
          '              </select>',
          '        </div>',
          '      </div>',
          '      <div class="layui-col-lg5">',
          '        <label class="layui-form-label">CF转发</label>',
          '        <div class="layui-input-block">',
          '          <select name="add_proxied" id="add_proxied" lay-verify="add_proxied" xm-select="add_proxied" xm-select-skin="default" xm-select-height="50px" xm-select-radio>',
          '              <option value="true">true</option>',
          '              <option value="false">false</option>',
          '          </select>',
          '        </div>',
          '      </div>',
          '  </from>',
          '  <div class="layui-form-item layui-col-lg10">',
          '    <label class="layui-form-label">解析记录</label>',
          '    <div class="layui-input-block">',
          '      <input type="text" id="add_content" name="add_content" lay-verify="add_content" placeholder="" autocomplete="off" class="layui-input">',
          '    </div>',
          '  </div>',
          '</div>'
          ].join("")
        ,btn: '提交'
        ,btnAlign: 'r' 
        ,shade: 0 //不显示遮罩
        ,success: function(layero, index){
          form.render(null, 'domain_add_form');
          formSelects.render('add_type');
          formSelects.render('add_proxied');
        }
        ,yes: function(){
          var postData = { // 获取表单数据
            'zone': data,
            'sub_domain': document.getElementById('add_sub_domain').value.split('\n'),
            'type': formSelects.value('add_type', 'valStr'),
            'proxied': formSelects.value('add_proxied', 'valStr'),
            'content': document.getElementById('add_content').value
          };
      
          for(var i = 0; i < postData['sub_domain'].length; i++) { 
            if(postData['sub_domain'][i].replace(/ /g, '') === ''){
                postData['sub_domain'].splice(i, 1);
            }else if (! public.isSubDomain(postData['sub_domain'][i])) {
              layer.msg(postData['sub_domain'][i] + ' 主机记录前缀不正确', {
                  offset: '15px'
                  ,shift: 6
                  ,icon: 5
                  ,time: 1500
              });
              return false;
            }
          }

          // 验证表单
          if (postData.sub_domain.length == 0){
            layer.msg('主机记录前缀不能为空', {
              offset: '15px'
              ,shift: 6
              ,icon: 5
              ,time: 1500
            });
            return false;
          }
          if (postData.type == ""){
            layer.msg('请选择解析类型', {
                offset: '15px'
                ,shift: 6
                ,icon: 5
                ,time: 1500
            });
            return false;
          }
          if (postData.proxied == ""){
            layer.msg('是否开启CF转发', {
                offset: '15px'
                ,shift: 6
                ,icon: 5
                ,time: 1500
            });
            return false;
          }
          if (postData.type == "A" && ! public.isIp(postData.content)){
            layer.msg('A记录，解析 IP不合法', {
              offset: '15px'
              ,shift: 6
              ,icon: 5
              ,time: 1500
            });
            return false;
          }else if (postData.type == "CNAME" && ! public.isDomain(postData.content)){
            layer.msg('CNAME记录，解析 别名不合法', {
              offset: '15px'
              ,shift: 6
              ,icon: 5
              ,time: 1500
            });
            return false;
          }
      
          loading1.call(this); // 打开 等待的弹层
      
          admin.req({
            url: '/domainns/cloudflare/add_records' //实际使用请改成服务端真实接口code == 1001
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
              // 当查询的主域名超过10 个，不自动刷新
              if (layui.setter.cf_domains_table_postdata.length < 10){
                // table.reload('cf_domains_table');
                loading1.call(this); // 打开 等待的弹层
                document.getElementById("cfDomainsSendButton").click();
                layer.close(index); // 关闭当前页
              }
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
    }
  });

});