# Grafana Alloy Log Processing Pipeline

A reference implementation for processing and parsing structured logs using Grafana Alloy with modular pipeline configurations. This project demonstrates log ingestion, parsing, labeling, and metric extraction patterns suitable for production logging scenarios.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Configuration Philosophy](#configuration-philosophy)
- [Log Format](#log-format)
- [Pipeline Pattern](#pipeline-pattern)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Querying Logs](#querying-logs)
- [Important Notes](#important-notes)

## Overview

This project provides a working example of Grafana Alloy's log processing capabilities, focusing on:

- Modular pipeline declarations for reusable log processing configurations
- Regex-based log parsing with validation patterns
- Label extraction and enrichment
- Metric generation from log data
- Parse success/failure tracking

**Note**: The Loki and Grafana configurations in this project are minimal implementations designed solely to support Alloy functionality. They are **not production-ready** and lack security hardening, high availability, and other enterprise requirements.

## Architecture

The stack consists of three main components:

- **Grafana Alloy**: Log collection, parsing, and forwarding
- **Loki**: Log aggregation and storage (minimal configuration)
- **Grafana**: Visualization and querying (basic setup)

Most of the project infrastructure is boilerplate necessary to demonstrate Alloy's log processing capabilities. The core focus is the Alloy pipeline configuration pattern.

## Project Structure
```
.
├── alloy/
│   ├── config.alloy           # Main Alloy configuration
│   └── modules/
│       └── template.alloy     # Modular pipeline declaration
├── apps/
│   ├── grafana/
│   │   ├── data/              # Grafana persistent data
│   │   └── provisioning/
│   │       └── datasources/
│   │           └── loki.yml   # Loki datasource configuration
│   └── loki/
│       ├── config/
│       │   └── config.yaml    # Minimal Loki configuration
│       └── data/              # Loki persistent data
├── logs/
│   └── transactions.log       # Generated log file
├── compose.yml                # Docker Compose stack definition
└── log_generator.py           # Transaction log generator script
```

### Why This Structure?

**Modular Pipeline Pattern**: The `modules/` directory contains reusable pipeline declarations. This approach allows you to:

- Define separate parsing configurations for different log formats
- Maintain clean separation between pipeline logic and orchestration
- Easily enable/disable specific log processors
- Share pipeline configurations across multiple Alloy instances

**Single Source Configuration**: The main `config.alloy` file imports and instantiates pipeline modules, keeping orchestration logic minimal and declarative.

## Configuration Philosophy

This project is designed for **messy, real-world log processing scenarios** where:

- Log formats are inconsistent or evolving
- Multiple applications produce different log structures
- Parse failures need to be tracked and debugged
- Each log source requires custom parsing logic

The modular pattern allows you to create a dedicated pipeline module for each log format, imported and instantiated in the main configuration:

```hcl
import.file "transactions" {
  filename = "/etc/alloy/modules/transactions.alloy"
}

import.file "application_logs" {
  filename = "/etc/alloy/modules/app_logs.alloy"
}

transactions.pipeline "prod" {}
application_logs.pipeline "prod" {}
```

## Log Format

The included log generator produces transaction logs in pipe-delimited format:
```
date|start_time|end_time|latency|method|detail|status|code
```

**Example:**
```
2025-12-26|21:45:32.123|21:45:32.423|300|CashIn|Transfer completed successfully|SUCCESS|200
2025-12-26|21:45:33.456|21:45:34.956|1500|STP-OUT|Payment processed|SUCCESS|0
2025-12-26|21:45:35.789|21:45:36.189|400|Transfer|Insufficient funds|FAILED|400
```

**Fields:**

| Field | Description | Example |
|-------|-------------|---------|
| date | Transaction date | 2025-12-26 |
| start_time | Transaction start timestamp | 21:45:32.123 |
| end_time | Transaction end timestamp | 21:45:32.423 |
| latency | Processing time in milliseconds | 300 |
| method | Transaction type | CashIn, STP-OUT, Transfer |
| detail | Human-readable description | Transfer completed successfully |
| status | Transaction outcome | SUCCESS, FAILED |
| code | Status code | 0, 200, 400, 500 |

## Pipeline Pattern

The pipeline uses a **fail-first validation pattern**:

### 1. Initial State: Mark as Failed
```hcl
stage.static_labels {
  values = {
    parse_status = "failed",
  }
}
```

All logs start with `parse_status="failed"`. This ensures unparseable logs are identifiable.

### 2. Attempt Parsing
```hcl
stage.regex {
  expression = `^(?P<date>\S+)\|(?P<time_start>\S+)\|...`
}
```

Extract structured data using named capture groups.

### 3. Conditional Success Marking
```hcl
stage.match {
  selector = `{method=~".+"}`
  stage.static_labels {
    values = {
      parse_status = "success",
    }
  }
}
```

Only logs that successfully extract required fields (e.g., `method`) are marked with `parse_status="success"`.

### Why This Pattern?

**Visibility**: Failed parses are immediately visible via the `parse_status` label
**Debugging**: Query `{parse_status="failed"}` to identify problematic log lines
**Validation**: Ensures downstream systems only process valid, structured data
**Monitoring**: Track parse success rate as a health metric

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.7+

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Create required directories:
```bash
mkdir -p apps/grafana/{data,provisioning/datasources}
mkdir -p apps/loki/{config,data}
mkdir -p logs
```

3. Set proper permissions:
```bash
sudo chown -R 472:472 apps/grafana/data
sudo chown -R 10001:10001 apps/loki/data
```

4. Start the stack:
```bash
docker-compose up -d
```

5. Generate sample logs:
```bash
python3 log_generator.py
```

### Access Points

- **Grafana**: http://localhost:3000 (admin/admin)
- **Loki API**: http://localhost:3100
- **Alloy UI**: http://localhost:12345

## Usage

### Viewing Logs in Grafana

1. Navigate to **Explore** in Grafana
2. Select **Loki** as the datasource
3. Use LogQL queries:
```logql
{job="template-job"}
{job="template-job", status="FAILED"}
{job="template-job", method="CashIn"}
{job="template-job", parse_status="failed"}
```

### Monitoring Parse Success

Track parsing health:
```logql
sum by (parse_status) (count_over_time({job="template-job"}[5m]))
```

Calculate success rate:
```logql
sum(count_over_time({job="template-job", parse_status="success"}[5m])) 
/ 
sum(count_over_time({job="template-job"}[5m]))
```

### Analyzing Metrics

The pipeline generates Prometheus metrics:

- `payment_transaction_latency_ms_bucket`: Latency histogram
- `payment_failed_transactions_total`: Failed transaction counter
- `payment_success_transactions_total`: Successful transaction counter

Access metrics at: http://localhost:12345/metrics

## Querying Logs

### Basic Queries

**All transactions:**
```logql
{job="template-job"}
```

**Filter by status:**
```logql
{job="template-job", status="FAILED"}
```

**Filter by method:**
```logql
{job="template-job", method="STP-OUT"}
```

**Parse failures:**
```logql
{job="template-job", parse_status="failed"}
```

### Advanced Queries

**Transaction rate per second:**
```logql
rate({job="template-job"}[1m])
```

**Failed transaction rate:**
```logql
rate({job="template-job", status="FAILED"}[5m])
```

## Important Notes

### Production Considerations

This project is a **reference implementation** for learning and testing. Before deploying to production:

**Loki Configuration:**
- Implement authentication (`auth_enabled: true`)
- Configure object storage (S3, GCS) instead of local filesystem
- Set up retention policies
- Enable multi-tenancy if needed
- Configure resource limits and rate limiting

**Grafana Configuration:**
- Change default admin credentials
- Configure OAuth/LDAP authentication
- Set up HTTPS with valid certificates
- Configure alerting and notifications
- Implement RBAC policies

**Alloy Configuration:**
- Secure API endpoints
- Implement TLS for log forwarding
- Configure resource limits
- Set up monitoring and alerting
- Implement log sampling for high-volume scenarios

**Security:**
- All services run without authentication in this setup
- No TLS/SSL encryption is configured
- Default credentials are used
- No network segmentation or firewall rules

### Limitations

- Single-node deployment (no high availability)
- Local filesystem storage (not suitable for production scale)
- No backup or disaster recovery mechanisms
- Minimal observability and monitoring
- No rate limiting or resource quotas

**Disclaimer**: This project is intended for educational and development purposes. Do not deploy to production without implementing proper security, scalability, and reliability measures.
