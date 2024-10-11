#! /bin/bash

read -p "请输入第一张网卡的ip地址: " ip1
read -p "请输入第二张网卡的ip地址: " ip2

apt -y upgrade && apt -y update && apt install -y cpu-checker qemu-kvm libvirt-daemon-system libvirt-clients bridge-utils virtinst virt-manager python3-pip gunicorn mariadb-server

#检查网络联通
ping -c1 baidu.com >> /dev/null
if [ $(echo $? -ne 0) ];then
    echo "网络连接失败,请检查网络"
    exit 0
fi

#检查是否支持虚拟化
kvm-ok >> /dev/null
if [ $(echo $? -ne 0) ];then
    echo "宿主机不支持虚拟化"
    exit 0
fi

systemctl start libvirtd.service && systemctl enable libvirtd.service

net_name=$(ip a | grep -w "${ip2}" | awk '{print $NF}')
net=$(ip a | grep -w "${ip2}" | awk '{print $2}')

#配置桥接接口
cat >/etc/netplan/*.yaml<<EOF
network:
  ethernets:
    ${net_name}:
      dhcp4: no
  bridges:
    br0:
      interfaces: [${net_name}]
      dhcp4: no
      addresses: [${net}]
      parameters:
        stp: true
        forward-delay: 4
      nameservers:
        addresses: [114.114.114.114]
  version: 2
EOF
netplan apply
#生成br0桥接网路
touch /etc/netplan/virsh-br0-network.xml
cat >>/etc/netplan/virsh-br0-network.xml<< EOF
<network>
    <name>br0-network</name>
    <forward mode="bridge" />
    <bridge name="br0" />
</network>
EOF
#启动br0
virsh net-define /root/netplan/virsh-br0-network.xml && virsh net-start br0-network && virsh net-autostart br0-etwork

#安装数据库，配置免密登陆
systemctl start mariadb && systemctl enable mariadb
sed -i 's/^# \* Basic Settings$/skip-grant-tables/g' /etc/mysql/mariadb.conf.d/50-server.cnf
sed -i "s/127.0.0.1/0.0.0.0/g" /etc/mysql/mariadb.conf.d/50-server.cnf
systemctl restart mariadb
mysql -u root -e "create database EtStack;"

#安装flask所需的软件包
touch /root/requirements.txt 
cat >>/root/requirements.txt<< EOF
pymysql
flask
flask_sqlalchemy
EOF
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r /root/requirements.txt
if [ $(echo $? -ne 0) ];then
    pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r /root/requirements.txt
fi

#修改ttyd自定义地址
sed -i "s/<<ipaddress>>/${ip1}/g" function/dashboard.py
chmod +x ttyd
mv ttyd /usr/sbin/

nohup gunicorn -w 3 -b 0.0.0.0:80 app:app &
echo "数据库地址${ip1}:3306,用户为root,部署时已将数据库改为免密登录"
echo "EtStack部署完成，请在浏览器输入${ip1}以访问本系统的dashboard"
