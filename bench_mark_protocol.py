import asyncio
import time
import pandas as pd
import numpy as np
from pathlib import Path

from coap_client_calls import sec_client_auth_put_call, sec_register_device_put_call, register_device_put_call, \
    sec_client_discover_device_put_call, client_discover_device_put_call

current_dir = Path(__file__).parent.absolute()


def benchmark_protocol(iterations, stop_between):
    benchmark_file_name = 'protocol_benchmark'
    headers = ['SecAuthenticate', 'SecDiscover', 'Discover', 'SecRegisterDevice', 'PlainRegisterDevice']
    measured_time = np.zeros([iterations, 5])

    if stop_between:
        input("About to start sec authentication")
    session_key, access_ticket = benchmark_sec_rad_authentication(0, iterations, measured_time)

    if stop_between:
        input("About to start sec client device discover")
    url, device_session_key, rad_ticket, owner_ticket = benchmark_sec_client_discover_device_put_call(1, iterations, measured_time, session_key, access_ticket)

    if stop_between:
        input("About to start non-sec client device discover")
    url = benchmark_client_discover_device_put_call(2, iterations, measured_time)

    if stop_between:
        input("About to start sec register device")
    benchmark_sec_register_device(3, iterations, measured_time)

    if stop_between:
        input("About to start non-sec register device")
    benchmark_register_device(4, iterations, measured_time)

    total_data_df = pd.DataFrame(data=measured_time, columns=headers)
    total_data_df.to_csv(benchmark_file_name + ".csv")


def benchmark_sec_rad_authentication(column, iterations, measured_time):

    session_key = None
    access_ticket = None

    for i in range(iterations):
        start = time.time()

        session_key, access_ticket = asyncio.get_event_loop().run_until_complete(sec_client_auth_put_call())

        duration = time.time() - start

        measured_time[i, column] = duration

    return session_key, access_ticket


def benchmark_sec_client_discover_device_put_call(column, iterations, measured_time, session_key, access_ticket):

    url = None
    device_session_key = None
    rad_ticket = None
    owner_ticket = None

    for i in range(iterations):
        start = time.time()

        url, device_session_key, rad_ticket, owner_ticket = asyncio.get_event_loop().run_until_complete(sec_client_discover_device_put_call(session_key, access_ticket))

        duration = time.time() - start

        measured_time[i, column] = duration

    return url, device_session_key, rad_ticket, owner_ticket


def benchmark_client_discover_device_put_call(column, iterations, measured_time):

    url = None

    for i in range(iterations):
        start = time.time()

        url = asyncio.get_event_loop().run_until_complete(client_discover_device_put_call())

        duration = time.time() - start

        measured_time[i, column] = duration

    return url


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
    benchmark_protocol(10, False)
