import asyncio
import time
import pandas as pd
import numpy as np
from pathlib import Path

from coap_client_calls import client_auth_put_call

current_dir = Path(__file__).parent.absolute()


def benchmark_protocol(iterations):

    benchmark_file_name = 'protocol_benchmark'
    headers = ['Authenticate']
    measured_time = np.zeros([iterations, 2])

    benchmark_rad_authentication(1, iterations, measured_time)

    total_data_df = pd.DataFrame(data=measured_time, columns=headers)
    total_data_df.to_csv(benchmark_file_name+".csv")


def benchmark_rad_authentication(column, iterations, measured_time):
    for i in range(iterations):
        start = time.time()

        asyncio.get_event_loop().run_until_complete(client_auth_put_call())

        duration = time.time() - start

        measured_time[i, column] = duration


if __name__ == "__main__":

    #asyncio.get_event_loop().run_until_complete(get_call())
    #asyncio.get_event_loop().run_until_complete(register_device_put_call())
    #asyncio.get_event_loop().run_until_complete(client_auth_put_call())

    benchmark_protocol(10)
