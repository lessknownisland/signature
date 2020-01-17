from django.contrib import admin
from alioss.models  import AliossBucketTb

# AliossBucketTb admin model
class AliossBucketTbAdmin(admin.ModelAdmin):
    # 需要显示的字段信息
    list_display = ('id', 'bucket_name', 'access_keyid', 'access_keysecret', 'main_host', 'vpc_host', 'status')

    # 设置哪些字段可以点击进入编辑界面，默认是第一个字段
    list_display_links = ('id', 'bucket_name', 'access_keyid', 'access_keysecret', 'status')

admin.site.register(AliossBucketTb, AliossBucketTbAdmin)