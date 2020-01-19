echo "start mobileConfig sh"
echo $1
echo $2
openssl smime -sign -in $1 -out $2 -signer /root/InnovCertificates.pem -certfile /root/root.crt.pem -outform der -nodetach
echo "end mobileConfig sh"