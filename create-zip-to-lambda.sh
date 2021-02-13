#!/bin/bash
# Packed following as: https://dev.to/razcodes/how-to-create-a-lambda-using-python-with-dependencies-4846
source config.conf
python3 -m venv venv
source venv/bin/activate

pip3 -r requeriments.txt

cd venv/lib/python3.8/site-packages

zip -r9 ${OLDPWD}/${ANDROID_SENTIMENT}.zip .
cd $OLDPWD
zip -g ${ANDROID_SENTIMENT}.zip ${ANDROID_SENTIMENT}.py
