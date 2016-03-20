#!/bin/bash

TIMESTAMP=`date +%Y%m%d-%H-%M`
PWD=`pwd`
DEST_DIR="${PWD}"
SRC_DIR="${PWD}/visir_slurper/data"
FNAME="data"
tar -vczf ${DEST_DIR}/${FNAME}-${TIMESTAMP}.tar.gz ${SRC_DIR}
