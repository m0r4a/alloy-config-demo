#!/bin/bash

if [ "$EUID" -ne 0 ]; then
	echo "Error: This script must be run as root"
	echo "Directory ownership must be set to match container UIDs (472, 10001, 65534)"
	exit 1
fi

set -e

mkdir -p extra/{grafana,loki,prometheus}/{config,data}
mkdir -p extra/logs

chown -R 472:472 extra/grafana
chown -R 10001:10001 extra/loki
chown -R 65534:65534 extra/prometheus

chmod -R 755 extra/grafana
chmod -R 755 extra/loki
chmod -R 755 extra/prometheus
chmod -R 755 extra/logs

echo "Setup complete"
