from lseg_analytics.yield_book_rest import (
    request_py_calculation_sync_by_id,
    request_py_calculation_sync,
    request_py_calculation_async_by_id,    
    request_py_calculation_async,
    get_result,
    Volatility,
    StructureNote,
    CurveTypeAndCurrency,
    LossSettings,
    Vector,
    MonthRatePair,
    RestPrepaySettings,
    MuniSettings,
    PricingScenario,
    CustomScenario,
    CmbsPrepayment,
    Balloon,
    HecmSettings,
    Partials,
    PyCalcGlobalSettings,
    SensitivityShocks,
    LookbackSettings,
    PyCalcInput,
    ExtraSettings,
    CmbsSettings,
    FloaterSettings,
    IndexProjection,
    TermRatePair,
    IndexLinkerSettings,
    MbsSettings,
    CloSettings,
    ConvertiblePricing,
    OptionModel
)

from datetime import date

import json as js

import time

# Select an ISIN or CUSIP ID of the instrument
identifier="31398GY86"

# Set a pricing level for the calculation
price_level = 99

global_settings = PyCalcGlobalSettings(
            pricing_date=date(2025, 1, 1),            
            use_previous_close=True,
            use_live_data=True,
            use_ibor6_m=True,
            retrieve_ppm_projection=True,
            retrieve_oas_path=True,
            use_stochastic_hpa=True,
            use_five_point_convexity=True,
            retrieve_roll_rate_matrix=True,
            use_model_col_haircut=True,
            use1000_path=True,
            use_core_logic_group_model=True,
            sba_ignore_prepay_penalty=True,
            use_ois=False,
            use_non_qm_collateral=False,
            core_logic_collateral="DEFAULT",
            shock_repo_rates_futures=True,
            use_muni_non_call_curve=True,
            use_muni_tax_settings=True,
            muni_de_minimis_annual_discount=0.1,
            muni_capital_gains_rate=0.1,
            muni_ordinary_income_rate=0.2,
            current_coupon_rates="MOATS",
            sensitivity_shocks=SensitivityShocks(
                effective_duration=2.5,
                spread=2.0,
                prepay=1.6,
                current_coupon_spreads=2.2,
                prepay_model_elbow=1.1,
                prepay_model_refi=3.5,
                hpa=1.2,
            ),
            lookback_settings=LookbackSettings(
                basis_lookback_days=10,
                curve_lookback_days=20,
                volatility_lookback_days=10,
                ccoas_lookback_days=10,
                mortgage_date_lookback_days=20,
                curve_date_shift_lookback_days=20,
                curve_date_roll_lookback=20,
            )
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
                    type="LMMDD",
                    structure_note=StructureNote(pricing="ASSETSWAP", callable_zero_pricing="DYNAMIC"),
                ),                
                extra_settings=ExtraSettings(
                    include_partials=False,
                    option_model="OAS",
                    use_oas_to_call=False,
                    partial_vega=False,
                    other_durations=False,
                    volatility_duration=False,
                    prepay_duration=False,
                    refi_elbow_duration=False,
                    current_coupon_spread_sensitivity=False,
                    refi_prepay_duration=False,
                    turnover_prepay_duration=False,
                    primary_secondary_spread_duration=False,
                    index_spread_duration=False,
                    partials=Partials(
                        curve_type="FORWARD",
                        curve_shift=0.1,
                        shock_type="SQUARE",
                        use_cumulative_wave_method=True,
                        partial_duration_years=[1, 2, 3, 5, 10, 20, 30],
                    ),
                ),
                hecm_settings=HecmSettings(
                    draw_type="CONSTANT",
                    draw_rate=1.1,
                    draw_vector=Vector(
                        interpolation_type="INTERPOLATED",
                        index="PRIM",
                        values_property=[MonthRatePair(month=1, rate=1.1)],
                    ),
                ),
                # Loss Settings are not moddeled for all securities, so uncomment this section only for securities with Losses modeled
                #
                # loss_settings=LossSettings(
                #     default_type="SDA",
                #     default_rate=0.01,
                #     default_vector=Vector(
                #         interpolation_type="LEVEL",
                #         index="PRIM",
                #         values_property=[MonthRatePair(month=1, rate=0.01)],
                #     ),
                #     severity_type="MODEL",
                #     severity_rate=0.01,
                #     severity_vector=Vector(
                #         interpolation_type="LEVEL",
                #         index="PRIM",
                #         values_property=[MonthRatePair(month=1, rate=0.01)],
                #     ),
                #     recovery_lag=1,
                #     delinquency_type="PASS",
                #     delinquency_rate=0.01,
                #     delinquency_vector=Vector(
                #         interpolation_type="LEVEL",
                #         index="PRIM",
                #         values_property=[MonthRatePair(month=1, rate=0.01)],
                #     ),
                #     use_model_loan_modifications=True,
                #     ignore_insurance=True,
                # ),
                prepay_settings=RestPrepaySettings(
                    type="CPR",
                    rate=0.01,
                    vector=Vector(
                        interpolation_type="LEVEL",
                        index="PRIM",
                        values_property=[MonthRatePair(month=1, rate=0.01)],
                    ),
                    model_to_balloon=False,
                ),
                 cmbs_settings=CmbsSettings(
                    pricing_scenarios=[
                        PricingScenario(
                            primary=True,
                            type="CPJ",
                            rate=1.1,
                            system_scenario_name="Scen_name",
                            custom_scenario=CustomScenario(
                                assume_call=True,
                                delay=True,
                                delay_balloon_maturity=True,
                                defeasance="AUTO",
                                prepayment=CmbsPrepayment(
                                    rate_during_yield_to_maturity=1.017,
                                    rate_after_yield_to_maturity=0.987,
                                    rate_during_premium=2.331,
                                ),
                                defaults=Balloon(
                                    percent=0.8,
                                    loss_severity=0.8,
                                    recovery_period=1,
                                    loss_type="CDR",
                                    loss_rate=0.8,
                                    month_to_extend=2,
                                    loss_vector=Vector(
                                        interpolation_type="INTERPOLATED",
                                        index="PRIM",
                                        values_property=[MonthRatePair(month=1, rate=1.1)],
                                    ),
                                ),
                                balloon_extend=Balloon(
                                    percent=0.8,
                                    loss_severity=0.8,
                                    recovery_period=1,
                                    loss_type="CDR",
                                    loss_rate=0.8,
                                    month_to_extend=2,
                                    loss_vector=Vector(
                                        interpolation_type="INTERPOLATED",
                                        index="PRIM",
                                        values_property=[MonthRatePair(month=1, rate=1.1)],
                                    ),
                                ),
                                balloon_default=Balloon(
                                    percent=0.8,
                                    loss_severity=0.8,
                                    recovery_period=1,
                                    loss_type="CDR",
                                    loss_rate=0.8,
                                    month_to_extend=2,
                                    loss_vector=Vector(
                                        interpolation_type="INTERPOLATED",
                                        index="PRIM",
                                        values_property=[MonthRatePair(month=1, rate=1.1)],
                                    ),
                                ),
                            ),
                        )
                    ],
                ),
                floater_settings=FloaterSettings(
                    use_forward_index=True,
                    forward_index_rate=1.1,
                    index_projections=[
                        IndexProjection(
                            index="index", term_unit="MONTH", values_property=[TermRatePair(term=1, rate=1.1)]
                        )
                    ],
                ), 
                index_linker_settings=IndexLinkerSettings(real_yield_beta=2.2),
                muni_settings=MuniSettings(
                    paydown_optional=True, 
                    ignore_call_info=True, 
                    use_stub_rate=True
                ),
                settlement_type="MARKET",
                settlement_date=date(2025, 1, 25),
                mbs_settings=MbsSettings(use_roll_info=True, call_underlying_remics=True),
                clo_settings=CloSettings(call_date=date(2025, 1, 17)),                
                #
                # Convertible pricing is not applicable for all security types, so uncomment when needed
                #
                # convertible_pricing=ConvertiblePricing(
                #     method="AT_MARKET",
                #     market_price=99,
                #     credit_spread=2.1,
                #     stock_price=99,
                #     stock_dividend_yield=5.0,
                #     stock_volatility=1.1,
                #     stock_borrow_rate=1.1,
                # ),
                # underlying_price=100,
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
            pricing_date="2025-01-17",
            currency="USD",
            prepay_type="CPR",
            prepay_rate=1.1,
            option_model=OptionModel.OAS,
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
            pricing_date="2025-01-17",
            currency="USD",
            prepay_type="CPR",
            prepay_rate=1.1,
            option_model=OptionModel.OAS
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