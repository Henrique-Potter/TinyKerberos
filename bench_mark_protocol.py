import asyncio
import time
import pandas as pd
import numpy as np
from pathlib import Path

from coap_client_calls import sec_client_auth_put_call, sec_register_device_put_call, register_device_put_call

current_dir = Path(__file__).parent.absolute()


def benchmark_protocol(iterations, stop_between):
    benchmark_file_name = 'protocol_benchmark'
    headers = ['SecAuthenticate', 'SecRegisterDevice', 'PlainRegisterDevice']
    measured_time = np.zeros([iterations, 3])

    if stop_between:
        input("About to start sec authentication")
    benchmark_sec_rad_authentication(0, iterations, measured_time)

    if stop_between:
        input("About to start sec register device")
    benchmark_sec_register_device(1, iterations, measured_time)

    if stop_between:
        input("About to start plain register device")
    benchmark_register_device(2, iterations, measured_time)

    total_data_df = pd.DataFrame(data=measured_time, columns=headers)
    total_data_df.to_csv(benchmark_file_name + ".csv")


def benchmark_sec_rad_authentication(column, iterations, measured_time):
    for i in range(iterations):
        start = time.time()

        asyncio.get_event_loop().run_until_complete(sec_client_auth_put_call())

        duration = time.time() - start

        measured_time[i, column] = duration


def benchmark_sec_register_device(column, iterations, measured_time):
    for i in range(iterations):
        start = time.time()

        asyncio.get_event_loop().run_until_complete(sec_register_device_put_call())

        duration = time.time() - start

        measured_time[i, column] = duration


def benchmark_register_device(column, iterations, measured_time):
    for i in range(iterations):
        start = time.time()

        asyncio.get_event_loop().run_until_complete(register_device_put_call())

        duration = time.time() - start

        measured_time[i, column] = duration


if __name__ == "__main__":
    benchmark_protocol(10)
