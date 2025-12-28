#!/usr/bin/env python3
import random
import time
from datetime import datetime, timedelta
from pathlib import Path

log_dir = Path("./extra/logs")
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "trans.log"

METHODS = [
    "CashIn",
    "CashOut",
    "STP-IN",
    "STP-OUT",
    "Transfer",
    "Payment",
    "Withdrawal",
    "Deposit"
]

SUCCESS_DETAILS = [
    "Transfer completed successfully",
    "Credit created",
    "Payment processed",
    "Withdrawal completed",
    "Deposit credited",
    "Transaction validated",
    "Operation finalized"
]

FAILED_DETAILS = [
    "Insufficient funds",
    "Invalid destination account",
    "Connection timeout",
    "Validation error",
    "Daily limit exceeded",
    "Service temporarily unavailable",
    "Transaction processing error"
]


def generate_transaction_data():
    date = datetime.now().strftime("%Y-%m-%d")
    start_time = datetime.now()
    latency_ms = random.randint(10, 1000)
    end_time = start_time + timedelta(milliseconds=latency_ms)

    start_time_str = start_time.strftime("%H:%M:%S.%f")[:-3]
    end_time_str = end_time.strftime("%H:%M:%S.%f")[:-3]

    method = random.choice(METHODS)
    is_success = random.random() < 0.8

    if is_success:
        status = "SUCCESS"
        code = random.choice([0, 200])
        detail = random.choice(SUCCESS_DETAILS)
    else:
        status = "FAILED"
        code = random.choice([1, 400, 500])
        detail = random.choice(FAILED_DETAILS)

    return {
        "date": date,
        "start_time": start_time_str,
        "end_time": end_time_str,
        "latency_ms": latency_ms,
        "method": method,
        "detail": detail,
        "status": status,
        "code": code
    }


def format_style_1(data):
    return f"{data['date']}|{data['start_time']}|{data['end_time']}|{data['latency_ms']}|{data['method']}|{data['detail']}|{data['status']}|{data['code']}\n"


def format_style_2(data):
    return f"|{data['date']}|{data['start_time']}|{data['end_time']}|{data['latency_ms']}|{data['method']}|{data['detail']}|{data['status']}|{data['code']}|\n"


def main():
    print(f"Generating transaction logs: {log_file.absolute()}")
    print("Format 1: date|start_time|end_time|latency_ms|method|detail|status|code")
    print("Format 2: |date|start_time|end_time|latency_ms|method|detail|status|code|")
    print()

    try:
        with open(log_file, "a") as f:
            use_format_1 = True

            while True:
                transaction_data = generate_transaction_data()

                if use_format_1:
                    log_line = format_style_1(transaction_data)
                else:
                    log_line = format_style_2(transaction_data)

                f.write(log_line)
                f.flush()

                print(log_line.strip())

                use_format_1 = not use_format_1

                time.sleep(random.uniform(0.1, 0.3))

    except KeyboardInterrupt:
        print("\nLog generation stopped.")


if __name__ == "__main__":
    main()
