from lseg_analytics.yield_book_rest import (
        request_scenario_calculation_sync,
        request_get_scen_calc_sys_scen_sync,
        request_scenario_calculation_async,
        request_get_scen_calc_sys_scen_async,
        get_result,
        Volatility,
        StructureNote,
        CurveTypeAndCurrency,
        LossSettings,
        Vector,
        MonthRatePair,
        RestPrepaySettings,
        ScenarioCalcGlobalSettings,
        Scenario,
        ScenarioDefinition,
        SystemScenario,
        UserScenario,
        ApimCurveShift,
        CurveMultiShift,
        ScenAbsoluteCurvePoint,
        ScenarioVolatility,
        SwaptionVolatility,
        SwaptionVolItem,
        CapVolatility,
        CapVolItem,
        ScenarioCalcInput,
        SettlementInfo,
        PricingScenario,
        CustomScenario,
        CmbsPrepayment,
        Balloon,
        HorizonInfo,
        ScenarioCalcFloaterSettings,
        HecmSettings,
        ScenCalcExtraSettings,
        Partials,
)
import json as js
import time

# request_scenario_calculation_async
global_settings = ScenarioCalcGlobalSettings(
            pricing_date="2025-01-01",
        )

scenario = Scenario(
            scenario_id="ScenID1",
            definition=ScenarioDefinition(
                system_scenario=SystemScenario(name="BEARFLAT100")
            ),
        )

input = ScenarioCalcInput(
            identifier="US742718AV11",
            id_type="ISIN",
            curve=CurveTypeAndCurrency(
                curve_type="GVT",
                currency="USD",
            ),
            settlement_info=SettlementInfo(
                level="100",
            ),
            horizon_info=[
                HorizonInfo(
                    scenario_id="ScenID1",
                    level="100",
                )
            ],
            horizon_py_method="OAS",
        )

# Execute Post sync request with prepared inputs
sa_sync_post_response = request_scenario_calculation_sync(
                            global_settings=global_settings,
                            scenarios=[scenario],
                            input=[input],
                        )

# Formulate and execute the get request
sa_sync_get_response = request_get_scen_calc_sys_scen_sync(
            id='US742718AV11',
            h_py_method="OAS",
            curve_type="GVT",
            pricing_date="2025-01-01",
            level="100",
            scenario="/sys/scenario/Par/50"
        )

# Request bond CF with async post
sa_async_post_response = request_scenario_calculation_async(
                            global_settings=global_settings,
                            scenarios=[scenario],
                            input=[input],
                        )

attempt = 1

while attempt < 10:

    from lseg_analytics.exceptions import ResourceNotFound
    try:
        # Request bond indic with async post
        async_post_results_response = get_result(request_id_parameter=sa_async_post_response.request_id)
        break
    except Exception as err:
        print(f"Attempt " + str(
            attempt) + " resulted in error retrieving results from:" + sa_async_post_response.request_id)
        if (isinstance(err, ResourceNotFound)
                and f"The result is not ready yet for requestID:{sa_async_post_response.request_id}" in str(err)):
            time.sleep(3)
            attempt += 1
        else:
            raise err

# Formulate and execute the get request by using instrument ID, Par_amount and job in which the calculation will be done
sa_async_get_response = request_get_scen_calc_sys_scen_async(
            id='US742718AV11',
            scenario="/sys/scenario/Par/50",
            pricing_date="2025-01-01",
            curve_type="GVT",
            h_py_method="OAS",
            h_level="100",
            level="100"
        )

# Due to async nature, code Will perform the fetch 10 times, as result is not always ready instantly, with 3 second lapse between attempts
attempt = 1

while attempt < 10:

    from lseg_analytics.exceptions import ResourceNotFound
    try:
        # Request bond indic with async post
        async_get_results_response = get_result(request_id_parameter=sa_async_get_response.request_id)
        break
    except Exception as err:
        print(f"Attempt " + str(
            attempt) + " resulted in error retrieving results from:" + sa_async_get_response.request_id)
        if (isinstance(err, ResourceNotFound)
                and f"The result is not ready yet for requestID:{sa_async_get_response.request_id}" in str(err)):
            time.sleep(3)
            attempt += 1
        else:
            raise err

# Print output in JSON format
print(js.dumps(obj=sa_sync_post_response, indent=4))

# Print output in JSON format
print(js.dumps(obj=sa_sync_get_response, indent=4))

# Print output in JSON format
print(js.dumps(obj=async_post_results_response, indent=4))

# Print output in JSON format
print(js.dumps(obj=async_get_results_response, indent=4))