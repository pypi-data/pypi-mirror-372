# coding=utf-8


from copy import deepcopy
from typing import Any, Awaitable

from corehttp.rest import AsyncHttpResponse, HttpRequest
from corehttp.runtime import AsyncPipelineClient, policies
from typing_extensions import Self

from .._serialization import Deserializer, Serializer
from ._configuration import AnalyticsAPIClientConfiguration
from .operations import (
    YieldBookRestOperations,
    bondFutureOperations,
    bondOperations,
    calendarResourceOperations,
    calendarsResourceOperations,
    capFloorOperations,
    cdsOperations,
    commoditiesCurvesOperations,
    creditCurvesOperations,
    eqVolatilityOperations,
    floatingRateIndexResourceOperations,
    floatingRateIndicesResourceOperations,
    forwardRateAgreementOperations,
    fxForwardCurveResourceOperations,
    fxForwardCurvesResourceOperations,
    fxForwardResourceOperations,
    fxForwardsResourceOperations,
    fxSpotResourceOperations,
    fxSpotsResourceOperations,
    fxVolatilityOperations,
    inflationCurvesOperations,
    instrumentTemplateResourceOperations,
    instrumentTemplatesResourceOperations,
    interestRateCurveServiceOperations,
    interestRateCurvesServiceOperations,
    ipaInterestRateCurvesOperations,
    ircapletVolatilityOperations,
    irSwapResourceOperations,
    irSwapsResourceOperations,
    irswaptionVolatilityOperations,
    loanResourceOperations,
    loansResourceOperations,
    optionResourceOperations,
    optionsResourceOperations,
    repoOperations,
    structuredProductsOperations,
    swaptionOperations,
    termDepositOperations,
)


class AnalyticsAPIClient:  # pylint: disable=client-accepts-api-version-keyword,too-many-instance-attributes
    """Analytic API to support channels workflows.

    :ivar calendars_resource: calendarsResourceOperations operations
    :vartype calendars_resource: analyticsapi.aio.operations.calendarsResourceOperations
    :ivar calendar_resource: calendarResourceOperations operations
    :vartype calendar_resource: analyticsapi.aio.operations.calendarResourceOperations
    :ivar fx_forward_curves_resource: fxForwardCurvesResourceOperations operations
    :vartype fx_forward_curves_resource:
     analyticsapi.aio.operations.fxForwardCurvesResourceOperations
    :ivar fx_forward_curve_resource: fxForwardCurveResourceOperations operations
    :vartype fx_forward_curve_resource:
     analyticsapi.aio.operations.fxForwardCurveResourceOperations
    :ivar fx_forwards_resource: fxForwardsResourceOperations operations
    :vartype fx_forwards_resource: analyticsapi.aio.operations.fxForwardsResourceOperations
    :ivar fx_forward_resource: fxForwardResourceOperations operations
    :vartype fx_forward_resource: analyticsapi.aio.operations.fxForwardResourceOperations
    :ivar fx_spots_resource: fxSpotsResourceOperations operations
    :vartype fx_spots_resource: analyticsapi.aio.operations.fxSpotsResourceOperations
    :ivar fx_spot_resource: fxSpotResourceOperations operations
    :vartype fx_spot_resource: analyticsapi.aio.operations.fxSpotResourceOperations
    :ivar yield_book_rest: YieldBookRestOperations operations
    :vartype yield_book_rest: analyticsapi.aio.operations.YieldBookRestOperations
    :ivar instrument_templates_resource: instrumentTemplatesResourceOperations operations
    :vartype instrument_templates_resource:
     analyticsapi.aio.operations.instrumentTemplatesResourceOperations
    :ivar instrument_template_resource: instrumentTemplateResourceOperations operations
    :vartype instrument_template_resource:
     analyticsapi.aio.operations.instrumentTemplateResourceOperations
    :ivar ir_swaps_resource: irSwapsResourceOperations operations
    :vartype ir_swaps_resource: analyticsapi.aio.operations.irSwapsResourceOperations
    :ivar ir_swap_resource: irSwapResourceOperations operations
    :vartype ir_swap_resource: analyticsapi.aio.operations.irSwapResourceOperations
    :ivar floating_rate_indices_resource: floatingRateIndicesResourceOperations operations
    :vartype floating_rate_indices_resource:
     analyticsapi.aio.operations.floatingRateIndicesResourceOperations
    :ivar floating_rate_index_resource: floatingRateIndexResourceOperations operations
    :vartype floating_rate_index_resource:
     analyticsapi.aio.operations.floatingRateIndexResourceOperations
    :ivar commodities_curves: commoditiesCurvesOperations operations
    :vartype commodities_curves: analyticsapi.aio.operations.commoditiesCurvesOperations
    :ivar credit_curves: creditCurvesOperations operations
    :vartype credit_curves: analyticsapi.aio.operations.creditCurvesOperations
    :ivar inflation_curves: inflationCurvesOperations operations
    :vartype inflation_curves: analyticsapi.aio.operations.inflationCurvesOperations
    :ivar ipa_interest_rate_curves: ipaInterestRateCurvesOperations operations
    :vartype ipa_interest_rate_curves: analyticsapi.aio.operations.ipaInterestRateCurvesOperations
    :ivar bond: bondOperations operations
    :vartype bond: analyticsapi.aio.operations.bondOperations
    :ivar bond_future: bondFutureOperations operations
    :vartype bond_future: analyticsapi.aio.operations.bondFutureOperations
    :ivar cap_floor: capFloorOperations operations
    :vartype cap_floor: analyticsapi.aio.operations.capFloorOperations
    :ivar cds: cdsOperations operations
    :vartype cds: analyticsapi.aio.operations.cdsOperations
    :ivar forward_rate_agreement: forwardRateAgreementOperations operations
    :vartype forward_rate_agreement: analyticsapi.aio.operations.forwardRateAgreementOperations
    :ivar repo: repoOperations operations
    :vartype repo: analyticsapi.aio.operations.repoOperations
    :ivar structured_products: structuredProductsOperations operations
    :vartype structured_products: analyticsapi.aio.operations.structuredProductsOperations
    :ivar swaption: swaptionOperations operations
    :vartype swaption: analyticsapi.aio.operations.swaptionOperations
    :ivar term_deposit: termDepositOperations operations
    :vartype term_deposit: analyticsapi.aio.operations.termDepositOperations
    :ivar eq_volatility: eqVolatilityOperations operations
    :vartype eq_volatility: analyticsapi.aio.operations.eqVolatilityOperations
    :ivar fx_volatility: fxVolatilityOperations operations
    :vartype fx_volatility: analyticsapi.aio.operations.fxVolatilityOperations
    :ivar ircaplet_volatility: ircapletVolatilityOperations operations
    :vartype ircaplet_volatility: analyticsapi.aio.operations.ircapletVolatilityOperations
    :ivar irswaption_volatility: irswaptionVolatilityOperations operations
    :vartype irswaption_volatility: analyticsapi.aio.operations.irswaptionVolatilityOperations
    :ivar options_resource: optionsResourceOperations operations
    :vartype options_resource: analyticsapi.aio.operations.optionsResourceOperations
    :ivar option_resource: optionResourceOperations operations
    :vartype option_resource: analyticsapi.aio.operations.optionResourceOperations
    :ivar interest_rate_curves_service: interestRateCurvesServiceOperations operations
    :vartype interest_rate_curves_service:
     analyticsapi.aio.operations.interestRateCurvesServiceOperations
    :ivar interest_rate_curve_service: interestRateCurveServiceOperations operations
    :vartype interest_rate_curve_service:
     analyticsapi.aio.operations.interestRateCurveServiceOperations
    :ivar loans_resource: loansResourceOperations operations
    :vartype loans_resource: analyticsapi.aio.operations.loansResourceOperations
    :ivar loan_resource: loanResourceOperations operations
    :vartype loan_resource: analyticsapi.aio.operations.loanResourceOperations
    :keyword endpoint: Service host. Default value is "https://api.analytics.lseg.com".
    :paramtype endpoint: str
    """

    def __init__(  # pylint: disable=missing-client-constructor-parameter-credential
        self, *, endpoint: str = "https://api.analytics.lseg.com", **kwargs: Any
    ) -> None:
        _endpoint = "{endpoint}"
        self._config = AnalyticsAPIClientConfiguration(endpoint=endpoint, **kwargs)
        _policies = kwargs.pop("policies", None)
        if _policies is None:
            _policies = [
                self._config.headers_policy,
                self._config.user_agent_policy,
                self._config.proxy_policy,
                policies.ContentDecodePolicy(**kwargs),
                self._config.retry_policy,
                self._config.authentication_policy,
                self._config.logging_policy,
            ]
        self._client: AsyncPipelineClient = AsyncPipelineClient(endpoint=_endpoint, policies=_policies, **kwargs)

        self._serialize = Serializer()
        self._deserialize = Deserializer()
        self._serialize.client_side_validation = False
        self.calendars_resource = calendarsResourceOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.calendar_resource = calendarResourceOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.fx_forward_curves_resource = fxForwardCurvesResourceOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.fx_forward_curve_resource = fxForwardCurveResourceOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.fx_forwards_resource = fxForwardsResourceOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.fx_forward_resource = fxForwardResourceOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.fx_spots_resource = fxSpotsResourceOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.fx_spot_resource = fxSpotResourceOperations(self._client, self._config, self._serialize, self._deserialize)
        self.yield_book_rest = YieldBookRestOperations(self._client, self._config, self._serialize, self._deserialize)
        self.instrument_templates_resource = instrumentTemplatesResourceOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.instrument_template_resource = instrumentTemplateResourceOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.ir_swaps_resource = irSwapsResourceOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.ir_swap_resource = irSwapResourceOperations(self._client, self._config, self._serialize, self._deserialize)
        self.floating_rate_indices_resource = floatingRateIndicesResourceOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.floating_rate_index_resource = floatingRateIndexResourceOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.commodities_curves = commoditiesCurvesOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.credit_curves = creditCurvesOperations(self._client, self._config, self._serialize, self._deserialize)
        self.inflation_curves = inflationCurvesOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.ipa_interest_rate_curves = ipaInterestRateCurvesOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.bond = bondOperations(self._client, self._config, self._serialize, self._deserialize)
        self.bond_future = bondFutureOperations(self._client, self._config, self._serialize, self._deserialize)
        self.cap_floor = capFloorOperations(self._client, self._config, self._serialize, self._deserialize)
        self.cds = cdsOperations(self._client, self._config, self._serialize, self._deserialize)
        self.forward_rate_agreement = forwardRateAgreementOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.repo = repoOperations(self._client, self._config, self._serialize, self._deserialize)
        self.structured_products = structuredProductsOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.swaption = swaptionOperations(self._client, self._config, self._serialize, self._deserialize)
        self.term_deposit = termDepositOperations(self._client, self._config, self._serialize, self._deserialize)
        self.eq_volatility = eqVolatilityOperations(self._client, self._config, self._serialize, self._deserialize)
        self.fx_volatility = fxVolatilityOperations(self._client, self._config, self._serialize, self._deserialize)
        self.ircaplet_volatility = ircapletVolatilityOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.irswaption_volatility = irswaptionVolatilityOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.options_resource = optionsResourceOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.option_resource = optionResourceOperations(self._client, self._config, self._serialize, self._deserialize)
        self.interest_rate_curves_service = interestRateCurvesServiceOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.interest_rate_curve_service = interestRateCurveServiceOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.loans_resource = loansResourceOperations(self._client, self._config, self._serialize, self._deserialize)
        self.loan_resource = loanResourceOperations(self._client, self._config, self._serialize, self._deserialize)

    def send_request(
        self, request: HttpRequest, *, stream: bool = False, **kwargs: Any
    ) -> Awaitable[AsyncHttpResponse]:
        """Runs the network request through the client's chained policies.

        >>> from corehttp.rest import HttpRequest
        >>> request = HttpRequest("GET", "https://www.example.org/")
        <HttpRequest [GET], url: 'https://www.example.org/'>
        >>> response = await client.send_request(request)
        <AsyncHttpResponse: 200 OK>

        For more information on this code flow, see https://aka.ms/azsdk/dpcodegen/python/send_request

        :param request: The network request you want to make. Required.
        :type request: ~corehttp.rest.HttpRequest
        :keyword bool stream: Whether the response payload will be streamed. Defaults to False.
        :return: The response of your network call. Does not do error handling on your response.
        :rtype: ~corehttp.rest.AsyncHttpResponse
        """

        request_copy = deepcopy(request)
        path_format_arguments = {
            "endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
        }

        request_copy.url = self._client.format_url(request_copy.url, **path_format_arguments)
        return self._client.send_request(request_copy, stream=stream, **kwargs)  # type: ignore

    async def close(self) -> None:
        await self._client.close()

    async def __aenter__(self) -> Self:
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *exc_details: Any) -> None:
        await self._client.__aexit__(*exc_details)
