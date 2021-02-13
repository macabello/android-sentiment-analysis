#!/bin/bash
source config.conf

aws s3 cp ./${ANDROID_SENTIMENT}.zip s3://${S3_BUCKET}/${ANDROID_SENTIMENT}.zip
