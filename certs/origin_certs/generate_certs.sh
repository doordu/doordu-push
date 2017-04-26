#!/bin/bash

openssl x509 -in $1 -inform der -out apns.cer.pem
openssl pkcs12 -nocerts -out apns.p12.pem -in $2
cat apns.cer.pem apns.p12.pem > $3
rm apns.cer.pem apns.p12.pem $1 $2
