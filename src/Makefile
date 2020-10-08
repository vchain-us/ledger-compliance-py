SHELL := /bin/bash

PROTOC ?= $(shell which protoc)
PYTEST ?= python -m pytest
PIP ?= pip

PROTO_DIR := proto
PROTO_FILE := ${PROTO_DIR}/lc.proto ${PROTO_DIR}/schema.proto
PROTO_URL := https://raw.githubusercontent.com/codenotary/immudb/master/pkg/api/schema/schema.proto

SCHEMA_OUT_DIR := LedgerCompliance/schema
GRPC_OUT_DIR := LedgerCompliance/schema

.PHONY: schema
schema:
	python -m grpc_tools.protoc -I ${PROTO_DIR} \
		--python_out=${SCHEMA_OUT_DIR} --grpc_python_out=${GRPC_OUT_DIR} \
		${PROTO_FILE}
	./fixup.sh
	
