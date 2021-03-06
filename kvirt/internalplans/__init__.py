haproxy = """
#jinja2: lstrip_blocks: True
parameters:
 template: CentOS-7-x86_64-GenericCloud.qcow2
 name: haproxy
 nets:
 - default
 vms: []

loadbalancer_{{ ports | join('+') }}:
 type: profile
 template: {{ template }}
 nets: {{ nets }}

{{ name }}:
 profile: loadbalancer_{{ ports | join('+') }}
 files:
  - path: /root/haproxy.cfg
    content:   |
      global
         log         127.0.0.1 local2
         chroot      /var/lib/haproxy
         pidfile     /var/run/haproxy.pid
         maxconn     4000
         user        haproxy
         group       haproxy
         nbproc 4
         daemon
      defaults
        mode        http
        log         global
        option      dontlognull
        # option      httpclose
        # option      httplog
        # option      forwardfor
        # option      redispatch
        stats enable
        stats uri /stats
        stats realm HAProxy\ Statistics
        stats auth admin:password
        timeout connect 10000
        timeout client 300000
        timeout server 300000
        maxconn     60000
        retries     3
      {%- for port in ports %}
      listen {{ name }}_{{ port }} *:{{ port }}
      {%- if port in [80, 443] %}
        mode http
        # option httpchk HEAD {{ checkpath }} HTTP/1.0
      {%- else %}
        mode tcp
      {%- endif %}
        balance roundrobin
        cookie JSESSIONID prefix
        {%- for vm in vms %}
        server {{ vm.name }} {{ vm.ip }}:{{ port }} cookie A check
        {%- endfor %}
       {%- endfor %}
 cmds:
  - yum -y install haproxy
  - sed -i "s/SELINUX=enforcing/SELINUX=permissive/" /etc/selinux/config
  - setenforce 0
  - cp /root/haproxy.cfg /etc/haproxy
  - systemctl start haproxy
  - systemctl enable haproxy
"""

gcpupload = """
#jinja2: lstrip_blocks: True
parameters:
 template: centos-7
 name: gcpupload
 net: default
 bucket: xxx
 url: http://download.cirros-cloud.net/0.4.0/cirros-0.4.0-x86_64-disk.img

gcpupload:
 template: {{ template }}
 nets:
 - {{ net }}
 disks:
 - 10
 cmds:
 - curl {{ url }} > {{ url | basename }}.gz
 - gsutil cp {{ url | basename }}.gz gs://{{ bucket }}
 - poweroff
"""
