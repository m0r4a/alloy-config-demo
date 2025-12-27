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


def generate_transaction_log():
    fecha = datetime.now().strftime("%Y-%m-%d")
    hora_inicio = datetime.now()
    latencia_ms = random.randint(10, 5000)
    hora_final = hora_inicio + timedelta(milliseconds=latencia_ms)
    hora_inicio_str = hora_inicio.strftime("%H:%M:%S.%f")[:-3]
    hora_final_str = hora_final.strftime("%H:%M:%S.%f")[:-3]
    metodo = random.choice(METHODS)
    is_success = random.random() < 0.8

    if is_success:
        estado = "SUCCESS"
        codigo = random.choice([0, 200])
        detalle = random.choice(SUCCESS_DETAILS)
    else:
        estado = "FAILED"
        codigo = random.choice([1, 400, 500])
        detalle = random.choice(FAILED_DETAILS)

    return f"{fecha}|{hora_inicio_str}|{hora_final_str}|{latencia_ms}|{metodo}|{detalle}|{estado}|{codigo}\n"


def main():
    print(f"Generating transaction logs: {log_file.absolute()}")
    print("Format: date|start_time|end_time|latency|method|detail|status|code\n")

    try:
        with open(log_file, "a") as f:
            while True:
                log_line = generate_transaction_log()
                f.write(log_line)
                f.flush()
                print(log_line.strip())
                time.sleep(random.uniform(0.3, 2.0))

    except KeyboardInterrupt:
        print("\nLog generation stopped.")


if __name__ == "__main__":
    main()
