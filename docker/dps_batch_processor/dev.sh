#!/bin/sh

dps_batch_processor --dps-manager-url=http://dps-manager:8000/ --database-manager-url=http://dps-database-manager:3002/ --api-key=$BATCH_PROCESSOR_API_KEY --verbose 1

exec "$@"
