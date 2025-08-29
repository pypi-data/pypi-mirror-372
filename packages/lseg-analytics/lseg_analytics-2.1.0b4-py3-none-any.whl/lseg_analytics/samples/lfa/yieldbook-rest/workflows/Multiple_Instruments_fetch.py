from lseg_analytics.yield_book_rest import (
    request_bond_indic_sync,
    request_bond_indic_async,
    IdentifierInfo,
    get_result
)
import json as js

import time

# List of instruments defined by either CUSIP or ISIN identifiers 
instrument_input=[IdentifierInfo(identifier="91282CLF6"),
                    IdentifierInfo(identifier="US1352752"),
                    IdentifierInfo(identifier="999818YT")]

# Request single/multiple bond indices with sync post
sync_response = request_bond_indic_sync(input=instrument_input)

# Request multiple bond indices with async post
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

# Print results in json format
print(js.dumps(obj=sync_response.as_dict(), indent=4))

# Print results in json format
print(js.dumps(async_post_results_response, indent=4))