from lseg_analytics.yield_book_rest import (
    request_py_calculation_sync_by_id,
    request_py_calculation_sync,
    request_py_calculation_async_by_id,    
    request_py_calculation_async,
    get_result,
    PyCalcGlobalSettings,
    PyCalcInput,
    CurveTypeAndCurrency,
    Volatility
)

from datetime import date

import json as js

import time

# Select an ISIN or CUSIP ID of the instrument
identifier="31398GY86"

# Set a pricing level for the calculation
price_level = 99

global_settings = PyCalcGlobalSettings(
            pricing_date=date(2025, 1, 1)
        )

input = [
            PyCalcInput(
                identifier=identifier,
                level=price_level,   
                curve=CurveTypeAndCurrency(
                    curve_type="GVT",
                    currency="USD",
                    retrieve_curve=False,
                    snapshot="EOD",
                ),                  
                volatility=Volatility(
                    type="LMMDD"
                ),               
            )
        ]

# Request bond PY with sync POST
py_sync_post_response = request_py_calculation_sync(
            global_settings=global_settings,
            input=input,
            keywords=["yield"]
        )

# Request bond PY with sync GET
py_sync_get_response = request_py_calculation_sync_by_id(
            id=identifier,
            level=price_level,
            curve_type="GVT",
            pricing_date="2025-01-01",
            currency="USD"
        )

# Request bond PY with async post
py_async_post_response = request_py_calculation_async(
            global_settings=global_settings,
            input=input,
            keywords=["yield"]
        )

attempt = 1

while attempt < 10:

    from lseg_analytics.exceptions import ResourceNotFound
    try:
        # Request bond indic with async post
        async_post_results_response = get_result(request_id_parameter=py_async_post_response.request_id)
        break
    except Exception as err:
        print(f"Attempt " + str(
            attempt) + " resulted in error retrieving results from:" + py_async_post_response.request_id)
        if (isinstance(err, ResourceNotFound)
                and f"The result is not ready yet for requestID:{py_async_post_response.request_id}" in str(err)):
            time.sleep(3)
            attempt += 1
        else:
            raise err

# Request bond PY with async get
py_async_get_response = request_py_calculation_async_by_id(
            id=identifier,
            level=price_level,
            curve_type="GVT",
            pricing_date="2025-01-01",
            currency="USD"
        )

# Due to async nature, code Will perform the fetch 10 times, as result is not always ready instantly, with 3 second lapse between attempts
attempt = 1

while attempt < 10:

    from lseg_analytics.exceptions import ResourceNotFound
    try:
        # Request bond indic with async post
        async_get_results_response = get_result(request_id_parameter=py_async_get_response.request_id)
        break
    except Exception as err:
        print(f"Attempt " + str(
            attempt) + " resulted in error retrieving results from:" + py_async_get_response.request_id)
        if (isinstance(err, ResourceNotFound)
                and f"The result is not ready yet for requestID:{py_async_get_response.request_id}" in str(err)):
            time.sleep(3)
            attempt += 1
        else:
            raise err

# Print results in json format
print(js.dumps(py_sync_post_response, indent=4))

# Print results in json format
print(js.dumps(py_sync_get_response, indent=4))

# Print results in json format
print(js.dumps(async_post_results_response, indent=4))

# Print results in json format
print(js.dumps(async_get_results_response, indent=4))