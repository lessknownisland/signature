from django.contrib import admin
from customer.models   import CustomerTb

# CustomerTb admin model
class CustomerTbAdmin(admin.ModelAdmin):
    # 需要显示的字段信息
    list_display = ('id', 'name', 'create_time', 'status')

    # 设置哪些字段可以点击进入编辑界面，默认是第一个字段
    list_display_links = ('id', 'name', 'create_time', 'status')

admin.site.register(CustomerTb, CustomerTbAdmin)