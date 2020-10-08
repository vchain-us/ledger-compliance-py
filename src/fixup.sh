#!/bin/sh
find ./LedgerCompliance/schema -name '*.py'|xargs grep -l "^import .*_pb2 as"|xargs sed -i '/^import .*_pb2 as/s/^/from . /'
