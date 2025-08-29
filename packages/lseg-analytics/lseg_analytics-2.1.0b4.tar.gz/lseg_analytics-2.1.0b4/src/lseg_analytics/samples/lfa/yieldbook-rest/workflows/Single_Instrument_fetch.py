from lseg_analytics.yield_book_rest import (
    request_bond_indic_sync,
    request_bond_indic_sync_get,
    request_bond_indic_async,
    request_bond_indic_async_get,
    IdentifierInfo,
    get_result
)

import json as js

import time

# Select an ISIN or CUSIP ID of the instrument
identifier="NL0000102317"

# Prepare the input data container
instrument_input=[IdentifierInfo(identifier=identifier)]

# Request bond indic with sync post
sync_post_response = request_bond_indic_sync(input=instrument_input)

# Request bond indic with sync get
sync_get_response = request_bond_indic_sync_get(id=identifier)

# Request bond indic with async post
async_post_response = request_bond_indic_async(input=instrument_input)

attempt = 1

while attempt < 10:

    from lseg_analytics.exceptions import ResourceNotFound
    try:
        # Request bond indic with async post
        async_post_results_response = get_result(request_id_parameter=async_post_response.request_id)
        break
    except Exception as err:
        print(f"Attempt " + str(
            attempt) + " resulted in error retrieving results from:" + async_post_response.request_id)
        if (isinstance(err, ResourceNotFound)
                and f"The result is not ready yet for requestID:{async_post_response.request_id}" in str(err)):
            time.sleep(3)
            attempt += 1
        else:
            raise err

# Request bond indic with async get
async_get_response = request_bond_indic_async_get(id=identifier)

# Due to async nature, code Will perform the fetch 10 times, as result is not always ready instantly, with 3 second lapse between attempts
attempt = 1

while attempt < 10:

    from lseg_analytics.exceptions import ResourceNotFound
    try:
        # Request bond indic with async post
        async_get_results_response = get_result(request_id_parameter=async_get_response.request_id)
        break
    except Exception as err:
        print(f"Attempt " + str(
            attempt) + " resulted in error retrieving results from:" + async_get_response.request_id)
        if (isinstance(err, ResourceNotFound)
                and f"The result is not ready yet for requestID:{async_get_response.request_id}" in str(err)):
            time.sleep(3)
            attempt += 1
        else:
            raise err

# Print results in json format
print(js.dumps(sync_post_response.as_dict(), indent=4))

# Print results in json format
print(js.dumps(sync_get_response, indent=4))

# Print results in json format
print(js.dumps(async_post_results_response, indent=4))

# Print results in json format
print(js.dumps(async_get_results_response, indent=4))