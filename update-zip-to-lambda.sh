#!/bin/bash
# Packed following as: https://dev.to/razcodes/how-to-create-a-lambda-using-python-with-dependencies-4846
source config.conf

zip -u ${ANDROID_SENTIMENT}.zip ${ANDROID_SENTIMENT}.py
