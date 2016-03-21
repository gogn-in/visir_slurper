#!/bin/bash

TIMESTAMP=`date +%Y%m%d-%H-%M`
PWD=`pwd`
DEST_DIR="${PWD}"
SRC_DIR="${PWD}/visir_slurper/data"
FNAME="text_and_json"
find visir_slurper/data/ \( -name "*.txt" -o -name "*.json" \)  -print | tar -vczf ${DEST_DIR}/${FNAME}-${TIMESTAMP}.tar.gz -T -
