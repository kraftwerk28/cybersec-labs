#!/usr/bin/env sh
tmp=${1:-ca-tmp}
mkdir -p $tmp

DEF_ROOT_NAME=RootCA
DEF_SRV_NAME=localhost
DEF_TERM=365
read -p "Name of root cert ($DEF_ROOT_NAME): " root
read -p "Name of server cert ($DEF_SRV_NAME): " srv
read -p "Certificates term in days ($DEF_TERM): " term
root=${root:-$DEF_ROOT_NAME}
srv=${srv:-$DEF_SRV_NAME}
term=${term:-$DEF_TERM}

read -p "Country name: " country
read -p "State: " state
read -p "Location: " location
read -p "Organization: " organization
read -p "Organizational Unit: " organizational_unit
read -p "Common name ($DEF_SRV_NAME): " common_name
read -p "Email address: " email
common_name=${common_name:-$DEF_SRV_NAME}

subjstr="\
/C=$country\
/ST=$state\
/L=$location\
/O=$organization\
/OU=$organizational_unit\
/CN=$common_name\
/emailAddress=$email"

openssl genrsa -des3 -out $tmp/$root.key 2048
openssl req -x509 -new -nodes \
  -key $tmp/$root.key \
  -sha256 -days $term \
  -subj $subjstr \
  -out $tmp/$root.pem

openssl genrsa -out $tmp/$srv.key 2048
openssl req -new \
  -subj $subjstr \
  -key $tmp/$srv.key \
  -out $tmp/$srv.csr

cat <<-EOF > $tmp/$srv.ext
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment
subjectAltName = @alt_names
[alt_names]
DNS.1 = $srv
IP.1 = 192.168.0.101
IP.2 = 192.168.0.102
IP.3 = 192.168.0.103
IP.4 = 192.168.0.104
IP.5 = 192.168.0.105
IP.6 = 192.168.0.106
IP.7 = 192.168.0.107
IP.8 = 192.168.0.108
IP.9 = 192.168.0.109
IP.10 = 192.168.0.110
IP.11 = 127.0.0.1
EOF

openssl x509 -req \
  -in $tmp/$srv.csr \
  -CA $tmp/$root.pem \
  -CAkey $tmp/$root.key \
  -CAcreateserial \
  -out $tmp/$srv.crt \
  -days $term \
  -sha256 \
  -extfile $tmp/$srv.ext
