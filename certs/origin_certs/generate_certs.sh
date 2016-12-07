#!/bin/bash

CER_FILE=apns_$1.cer
P12_FILE=apns_$1.p12
OUT_FILE=doordu_$1.pem

openssl x509 -in $CER_FILE -inform der -out apns_$1_cer.pem
openssl pkcs12 -nocerts -out apns_$1_key.pem -in $P12_FILE
cat apns_$1_cer.pem apns_$1_key.pem > $OUT_FILE
