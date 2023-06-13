#!/bin/bash

echo ""
echo "Generate the private key"
echo ""
openssl genpkey -algorithm RSA -out client.key

echo ""
echo "##################### Create a Certificate Signing Request (CSR) for the CA #####################"
echo ""
openssl req -new -key client.key -out client.csr
openssl req -new -x509 -sha256 -key client.key -out client.crt -days 365

echo ""
echo "Generate a private key and certificate signing request (CSR) for the blockchain"
echo ""
openssl genpkey -algorithm RSA -out server.key


echo ""
echo "##################### Create the CSR for the blockchain #####################"
echo ""

openssl req -newkey rsa:2048 -nodes -keyout server.key -out server.csr -config openssl.cnf
openssl x509 -req -in server.csr -CA client.crt -CAkey client.key -CAcreateserial -out server.crt -extensions v3_req -extfile openssl.cnf -days 365


rm server.csr
rm client.csr
rm client.key

mv server.crt ./server
mv server.key ./server
mv client.crt ./clients
