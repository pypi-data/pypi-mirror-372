from lseg_analytics.yield_book_rest import (
        post_cash_flow_sync,
        get_cash_flow_sync,
        post_cash_flow_async,
        get_cash_flow_async,
        get_result,
        CashFlowGlobalSettings, 
        CashFlowInput,
        Volatility,
        CurveTypeAndCurrency,
        LossSettings,
        RestPrepaySettings,
        CashflowFloaterSettings,
        CashflowMbsSettings,
        MuniSettings
)
import json as js

import time

# Select an ISIN or CUSIP ID of the instrument
identifier="31398GY86"

# Formulate Request body parameters - Global Settings
global_settings = CashFlowGlobalSettings(
            pricing_date="2025-01-13",
            use_previous_close=True,
            use_live_data=False,
            volatility=Volatility(
                type="Market",
                rate=1.11,
            ),
            retrieve_ppm_projection=False,
            core_logic_collateral="DEFAULT",
        )

# Formulate Request body parameters - Input 
input = CashFlowInput(
            identifier=identifier,
            id_type="CUSIP",
            curve=CurveTypeAndCurrency(
                curve_type="GVT",
                currency="USD",
                retrieve_curve=False,
                snapshot="EOD",
            ),
            settlement_type="MARKET",
            settlement_date="2025-01-15",
            custom_settlement="custom_settlement",
            par_amount="10000",
            # Loss Settings are not moddeled for all securities, so uncomment this section only for securities with Losses modeled
            #
            # loss_settings=LossSettings(
            #     default_type="SDA",
            #     default_rate=0.01,
            #     severity_type="MODEL",
            #     severity_rate=0.01,
            #     recovery_lag=1,
            #     delinquency_type="PASS",
            #     delinquency_rate=0.01,
            #     use_model_loan_modifications=False,
            #     ignore_insurance=False,
            # ),
            prepay=RestPrepaySettings(
                type="Model",
                rate=0.01,
            ),
            floater_settings=CashflowFloaterSettings(
                use_forward_index=True,
                forward_index_rate=0.01,
                calculate_to_maturity=False,
            ),
            muni_settings=MuniSettings(
                paydown_optional=False, 
                ignore_call_info=False, 
                use_stub_rate=False
            ),
            mbs_settings=CashflowMbsSettings(
                use_roll_info=False, 
                assume_call=False, 
                step_down_fail=False, 
                show_collateral_cash_flow=False
            )
)

# Execute Post sync request with prepared inputs
cf_sync_post_response = post_cash_flow_sync(
                            global_settings=global_settings,
                            input=[input]
                        )

# Formulate and execute the get request by using instrument ID and Par_amount
cf_sync_get_response = get_cash_flow_sync(
            id='999818LH',
            id_type="CUSIP",
            pricing_date="2021-01-01",
            par_amount="10000"
        )

# Request bond CF with async post
cf_async_post_response = post_cash_flow_async(
            global_settings=global_settings,
            input=[input]
        )

attempt = 1

while attempt < 10:

    from lseg_analytics.exceptions import ResourceNotFound
    try:
        # Request bond indic with async post
        async_post_results_response = get_result(request_id_parameter=cf_async_post_response.request_id)
        break
    except Exception as err:
        print(f"Attempt " + str(
            attempt) + " resulted in error retrieving results from:" + cf_async_post_response.request_id)
        if (isinstance(err, ResourceNotFound)
                and f"The result is not ready yet for requestID:{cf_async_post_response.request_id}" in str(err)):
            time.sleep(3)
            attempt += 1
        else:
            raise err

# Formulate and execute the get request by using instrument ID, Par_amount and job in which the calculation will be done
cf_async_get_response = get_cash_flow_async(
            id='999818LH',
            id_type="CUSIP",
            pricing_date="2021-01-01",
            par_amount="10000"
        )

# Due to async nature, code Will perform the fetch 10 times, as result is not always ready instantly, with 3 second lapse between attempts
attempt = 1

while attempt < 10:

    from lseg_analytics.exceptions import ResourceNotFound
    try:
        # Request bond indic with async post
        async_get_results_response = get_result(request_id_parameter=cf_async_get_response.request_id)
        break
    except Exception as err:
        print(f"Attempt " + str(
            attempt) + " resulted in error retrieving results from:" + cf_async_get_response.request_id)
        if (isinstance(err, ResourceNotFound)
                and f"The result is not ready yet for requestID:{cf_async_get_response.request_id}" in str(err)):
            time.sleep(3)
            attempt += 1
        else:
            raise err

# Print output to a file, as CF output is too long for terminal printout
print(js.dumps(cf_sync_post_response, indent=4), file=open('CF_output_Sync_Post.json', 'w+'))

# Print output to a file, as CF output is too long for terminal printout
print(js.dumps(cf_sync_get_response, indent=4), file=open('CF_output_Sync_Get.json', 'w+'))

# Print results in json format
print(js.dumps(async_post_results_response, indent=4), file=open('CF_output_Async_Post.json', 'w+'))

# Print results in json format
print(js.dumps(async_get_results_response, indent=4), file=open('CF_output_Async_Get.json', 'w+'))