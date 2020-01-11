#-_- coding: utf-8 -_-

from django.urls import path
from django.conf.urls import url
# from signature.domainns.reflesh_customer import DomainnsRefleshExecuteCdn, DomainnsRefleshExecuteProject

channel_routing = [
    # 域名缓存清理
    # path('domainns/reflesh/execute/cdn', DomainnsRefleshExecuteCdn),
    # path('domainns/reflesh/execute/project', DomainnsRefleshExecuteProject),
    # url(r'/saltstack/reflesh/execute/cdn', DomainnsRefleshExecuteCdn),
    # path('ws/table/<slug:table_id>/', TableConsumer),
    # route_class(SaltstackRefleshExecuteCdn, path=r"^/saltstack/reflesh/execute/cdn"),
    # route_class(SaltstackRefleshExecute, path=r"^/saltstack/reflesh/execute"),

    # #/saltstack/command/
    # route_class(SaltstackCommandDeploy, path=r"^/saltstack/command/deploy"),
    # route_class(SaltstackCommandExecute, path=r"^/saltstack/command/execute"),

    # #/servers/update
    # route_class(ServersUpdate, path=r"^/servers/update"),

    # #/upgrade/
    # route_class(UpgradeExecute, path=r"^/upgrade/execute$"),
    # route_class(RemoteExecute, path=r"^/upgrade/remote_execute"),
    # route_class(ApacheConfig, path=r"^/upgrade/deploy/apache_config"),
    # ##专业盘彩票
    # route_class(UpgradeExecuteZypFront, path=r"^/upgrade/execute/zypfront"),

    # #/dns/dnspod/record
    # route_class(DnsDnspodRecordUpdate, path=r"^/dns/dnspod/record/update"),
    # route_class(DnsDnspodRecordAdd, path=r"^/dns/dnspod/record/add"),

    # #/dns/cloudflare/record
    # route_class(DnsCloudflareRecordUpdate, path=r"^/dns/cloudflare/record/update"),
    # route_class(DnsCloudflareRecordAdd, path=r"^/dns/cloudflare/record/add"),
]