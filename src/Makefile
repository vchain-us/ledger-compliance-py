SHELL := /bin/bash

PROTOC ?= $(shell which protoc)
PYTEST ?= python3 -m pytest
PIP ?= pip3
COVERAGE ?= coverage

PROTO_DIR := proto
PROTO_FILE := ${PROTO_DIR}/lc.proto ${PROTO_DIR}/schema.proto
PROTO_URL := https://raw.githubusercontent.com/codenotary/immudb/master/pkg/api/schema/schema.proto

SCHEMA_OUT_DIR := LedgerCompliance/schema
GRPC_OUT_DIR := LedgerCompliance/schema

.PHONY: schema
schema:
	python3 -m grpc_tools.protoc -I ${PROTO_DIR} \
		--python_out=${SCHEMA_OUT_DIR} --grpc_python_out=${GRPC_OUT_DIR} \
		${PROTO_FILE}
	./fixup.sh
	
init:
	$(PIP) install -r requirements.txt
	
dev:
	$(PIP) install -r requirements-dev.txt

test:
	$(PYTEST) -vv --color=yes tests/

coverage:
	$(COVERAGE) run -m pytest tests

install:
	python3 setup.py install

.PHONY: dist
dist:
	mkdir -p ./dist
	rm -f ./dist/*
	python setup.py sdist bdist_wheel
