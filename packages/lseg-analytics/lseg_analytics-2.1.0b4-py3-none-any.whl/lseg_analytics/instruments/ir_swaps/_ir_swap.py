import copy
import datetime
from typing import Any, Dict, List, Literal, Optional, Union

from lseg_analytics._client.client import Client
from lseg_analytics.common._resource_base import ResourceBase
from lseg_analytics.exceptions import (
    LibraryException,
    ResourceNotFound,
    check_exception_and_raise,
    check_id,
)
from lseg_analytics_basic_client.models import (
    CrossCurencySwapOverride,
    CurencyBasisSwapOverride,
    Description,
    IrPricingParameters,
    IrSwapAsCollectionItem,
    IrSwapDefinition,
    IrSwapDefinitionInstrument,
    IrSwapInstrumentSolveResponseFieldsOnResourceResponseData,
    IrSwapInstrumentSolveResponseFieldsResponseData,
    IrSwapInstrumentValuationResponseFieldsOnResourceResponseData,
    IrSwapInstrumentValuationResponseFieldsResponseData,
    Location,
    MarketData,
    ResourceType,
    SortingOrderEnum,
    TenorBasisSwapOverride,
    VanillaIrsOverride,
)

from ._logger import logger


class IrSwap(ResourceBase):
    """
    IrSwap object.

    Contains all the necessary information to identify and define a IrSwap instance.

    Attributes
    ----------
    type : Union[str, ResourceType], optional
        Property defining the type of the resource.
    id : str, optional
        Unique identifier of the IrSwap.
    location : Location
        Object defining the location of the IrSwap in the platform.
    description : Description, optional
        Object defining metadata for the IrSwap.
    definition : IrSwapDefinition
        Object defining the IrSwap.

    See Also
    --------
    IrSwap.solve : Calculate analytics for an interest rate swap stored on the platform, by solving a variable parameter (e.g., fixed rate) provided in the request,
        so that a specified property (e.g., market value, duration) matches a target value.
        Provide an instrument ID in the request to perform the solving.
    IrSwap.value : Calculate analytics for an interest rate swap stored on the platform, including valuation results, risk metrics, and other relevant measures.
        Provide an instrument ID in the request to perform the valuation.

    Examples
    --------


    """

    _definition_class = IrSwapDefinition

    def __init__(self, definition: IrSwapDefinition, description: Optional[Description] = None):
        """
        IrSwap constructor

        Parameters
        ----------
        definition : IrSwapDefinition
            Object defining the IrSwap.
        description : Description, optional
            Object defining metadata for the IrSwap.

        Examples
        --------


        """
        self.definition: IrSwapDefinition = definition
        self.type: Optional[Union[str, ResourceType]] = "IrSwap"
        if description is None:
            self.description: Optional[Description] = Description(tags=[])
        else:
            self.description: Optional[Description] = description
        self._location: Location = Location(name="")
        self._id: Optional[str] = None

    @property
    def id(self):
        """
        Returns the IrSwap id

        Parameters
        ----------


        Returns
        --------
        str
            Unique identifier of the IrSwap.

        Examples
        --------


        """
        return self._id

    @id.setter
    def id(self, value):
        raise AttributeError("id is read only")

    @property
    def location(self):
        """
        Returns the IrSwap location

        Parameters
        ----------


        Returns
        --------
        Location
            Object defining the location of the IrSwap in the platform.

        Examples
        --------


        """
        return self._location

    @location.setter
    def location(self, value):
        raise AttributeError("location is read only")

    def _create(self, location: Location) -> None:
        """
        Save a new IrSwap in the platform

        Parameters
        ----------
        location : Location
            Object defining the location of the IrSwap in the platform.

        Returns
        --------
        None


        Examples
        --------


        """

        try:
            logger.info("Creating IrSwap")

            response = Client().ir_swaps_resource.create(
                location=location,
                description=self.description,
                definition=self.definition,
            )

            self._id = response.data.id

            self._location = response.data.location
            logger.info(f"IrSwap created with id: {self._id}")
        except Exception as err:
            logger.error("Error creating IrSwap:")
            raise err

    def _overwrite(self) -> None:
        """
        Overwrite a IrSwap that exists in the platform. The IrSwap can be identified either by its unique ID (GUID format) or by its location path (space/name).

        Parameters
        ----------


        Returns
        --------
        None


        Examples
        --------


        """
        logger.info(f"Overwriting IrSwap with id: {self._id}")
        Client().ir_swap_resource.overwrite(
            instrument_id=self._id,
            location=self._location,
            description=self.description,
            definition=self.definition,
        )

    def solve(
        self,
        *,
        pricing_preferences: Optional[IrPricingParameters] = None,
        market_data: Optional[MarketData] = None,
        return_market_data: Optional[bool] = None,
        fields: Optional[str] = None,
    ) -> IrSwapInstrumentSolveResponseFieldsOnResourceResponseData:
        """
        Calculate analytics for an interest rate swap stored on the platform, by solving a variable parameter (e.g., fixed rate) provided in the request,
        so that a specified property (e.g., market value, duration) matches a target value.
        Provide an instrument ID in the request to perform the solving.

        Parameters
        ----------
        pricing_preferences : IrPricingParameters, optional
            The parameters that control the computation of the analytics.
        market_data : MarketData, optional
            The market data used to compute the analytics.
        return_market_data : bool, optional
            Boolean property to determine if undelying market data used for calculation should be returned in the response
        fields : str, optional
            A parameter used to select the fields to return in response. If not provided, all fields will be returned.
            Some usage examples:
            1. Simply enumerating the fields, separating them by ',', e.g. 'fields=//please insert the selected fields here, e.g., field1, field2 //'
            2. Using parentheses to indicate nesting, e.g. 'fields= //please insert the selected field and subfields here, e.g., field1(subfield1, subfield2), field2(subfield3)//’
            3. Using forward slash '/' to indicate nesting, e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1/subfield1, field1/subfield2, field2/subfield3//’ (same result as example above)
            4. Operators can even be combined (forward slashes in brackets, not the way around), e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1(subfield1/subsubfield1), field2/subfield2//'

        Returns
        --------
        IrSwapInstrumentSolveResponseFieldsOnResourceResponseData


        Examples
        --------
        >>> # build the swap from 'LSEG/OIS_SOFR' template
        >>> fwd_start_sofr = create_from_vanilla_irs_template(template_reference = "LSEG/OIS_SOFR")
        >>>
        >>> # Swap needs to be saved in order for the solve class method to be executable
        >>> fwd_start_sofr.save(name="sofr_fwd_start_swap_exm")
        >>>
        >>> # set a solving variable between first and second leg and Fixed Rate or Spread
        >>> solving_variable = IrSwapSolvingVariable(leg='FirstLeg', name='FixedRate')
        >>>
        >>> # Apply solving target(s)
        >>> solving_target=IrSwapSolvingTarget(market_value=IrMeasure(value=0.0))
        >>>
        >>> # Setup the solving parameter object
        >>> solving_parameters = IrSwapSolvingParameters(variable=solving_variable, target=solving_target)
        >>>
        >>> # instantiate pricing parameters
        >>> pricing_parameters = IrPricingParameters(solving_parameters=solving_parameters)
        >>>
        >>> # solve the swap par rate
        >>> solving_response_object = fwd_start_sofr.solve(pricing_preferences=pricing_parameters)
        >>>
        >>> delete(name="sofr_fwd_start_swap_exm")
        >>>
        >>> print(js.dumps(solving_response_object.analytics.as_dict(), indent=4))
        {
            "solving": {
                "result": 3.7728670986451025
            },
            "description": {
                "instrumentTag": "",
                "instrumentDescription": "Pay USD Annual 3.77% vs Receive USD Annual +0bp SOFR 2035-08-27",
                "startDate": "2025-08-25",
                "endDate": "2035-08-27",
                "tenor": "10Y"
            },
            "valuation": {
                "accrued": {
                    "value": 0.0,
                    "percent": 0.0,
                    "dealCurrency": {
                        "value": 0.0,
                        "currency": "USD"
                    },
                    "reportCurrency": {
                        "value": 0.0,
                        "currency": "USD"
                    }
                },
                "marketValue": {
                    "value": 4.65661287307739e-10,
                    "dealCurrency": {
                        "value": 4.65661287307739e-10,
                        "currency": "USD"
                    },
                    "reportCurrency": {
                        "value": 4.65661287307739e-10,
                        "currency": "USD"
                    }
                },
                "cleanMarketValue": {
                    "value": 4.65661287307739e-10,
                    "dealCurrency": {
                        "value": 4.65661287307739e-10,
                        "currency": "USD"
                    },
                    "reportCurrency": {
                        "value": 4.65661287307739e-10,
                        "currency": "USD"
                    }
                }
            },
            "risk": {
                "duration": {
                    "value": -8.48922542195612
                },
                "modifiedDuration": {
                    "value": -8.17194017159767
                },
                "benchmarkHedgeNotional": {
                    "value": -9833438.11004938,
                    "currency": "USD"
                },
                "annuity": {
                    "value": -8364.31794109568,
                    "dealCurrency": {
                        "value": -8364.31794109568,
                        "currency": "USD"
                    },
                    "reportCurrency": {
                        "value": -8364.31794109568,
                        "currency": "USD"
                    }
                },
                "dv01": {
                    "value": -8166.69434783421,
                    "bp": -8.16669434783421,
                    "dealCurrency": {
                        "value": -8166.69434783421,
                        "currency": "USD"
                    },
                    "reportCurrency": {
                        "value": -8166.69434783421,
                        "currency": "USD"
                    }
                },
                "pv01": {
                    "value": -8166.69434783328,
                    "bp": -8.16669434783328,
                    "dealCurrency": {
                        "value": -8166.69434783328,
                        "currency": "USD"
                    },
                    "reportCurrency": {
                        "value": -8166.69434783328,
                        "currency": "USD"
                    }
                },
                "br01": {
                    "value": 0.0,
                    "dealCurrency": {
                        "value": 0.0,
                        "currency": "USD"
                    },
                    "reportCurrency": {
                        "value": 0.0,
                        "currency": "USD"
                    }
                }
            },
            "firstLeg": {
                "description": {
                    "legTag": "PaidLeg",
                    "legDescription": "Pay USD Annual 3.77%",
                    "interestType": "Fixed",
                    "currency": "USD",
                    "startDate": "2025-08-25",
                    "endDate": "2035-08-27",
                    "index": ""
                },
                "valuation": {
                    "accrued": {
                        "value": 0.0,
                        "percent": 0.0,
                        "dealCurrency": {
                            "value": 0.0,
                            "currency": "USD"
                        },
                        "reportCurrency": {
                            "value": 0.0,
                            "currency": "USD"
                        }
                    },
                    "marketValue": {
                        "value": 3155745.9962566453,
                        "dealCurrency": {
                            "value": 3155745.9962566453,
                            "currency": "USD"
                        },
                        "reportCurrency": {
                            "value": 3155745.9962566453,
                            "currency": "USD"
                        }
                    },
                    "cleanMarketValue": {
                        "value": 3155745.9962566453,
                        "dealCurrency": {
                            "value": 3155745.9962566453,
                            "currency": "USD"
                        },
                        "reportCurrency": {
                            "value": 3155745.9962566453,
                            "currency": "USD"
                        }
                    }
                },
                "risk": {
                    "duration": {
                        "value": 8.489225421956121
                    },
                    "modifiedDuration": {
                        "value": 8.186786007273955
                    },
                    "benchmarkHedgeNotional": {
                        "value": 0.0,
                        "currency": "USD"
                    },
                    "annuity": {
                        "value": 8364.31794109568,
                        "dealCurrency": {
                            "value": 8364.31794109568,
                            "currency": "USD"
                        },
                        "reportCurrency": {
                            "value": 8364.31794109568,
                            "currency": "USD"
                        }
                    },
                    "dv01": {
                        "value": 8181.530653504655,
                        "bp": 8.181530653504655,
                        "dealCurrency": {
                            "value": 8181.530653504655,
                            "currency": "USD"
                        },
                        "reportCurrency": {
                            "value": 8181.530653504655,
                            "currency": "USD"
                        }
                    },
                    "pv01": {
                        "value": 1585.6289644073695,
                        "bp": 1.5856289644073696,
                        "dealCurrency": {
                            "value": 1585.6289644073695,
                            "currency": "USD"
                        },
                        "reportCurrency": {
                            "value": 1585.6289644073695,
                            "currency": "USD"
                        }
                    },
                    "br01": {
                        "value": 0.0,
                        "dealCurrency": {
                            "value": 0.0,
                            "currency": "USD"
                        },
                        "reportCurrency": {
                            "value": 0.0,
                            "currency": "USD"
                        }
                    }
                }
            },
            "secondLeg": {
                "description": {
                    "legTag": "ReceivedLeg",
                    "legDescription": "Receive USD Annual +0bp SOFR",
                    "interestType": "Float",
                    "currency": "USD",
                    "startDate": "2025-08-25",
                    "endDate": "2035-08-27",
                    "index": "SOFR"
                },
                "valuation": {
                    "accrued": {
                        "value": 0.0,
                        "percent": 0.0,
                        "dealCurrency": {
                            "value": 0.0,
                            "currency": "USD"
                        },
                        "reportCurrency": {
                            "value": 0.0,
                            "currency": "USD"
                        }
                    },
                    "marketValue": {
                        "value": 3155745.996256646,
                        "dealCurrency": {
                            "value": 3155745.996256646,
                            "currency": "USD"
                        },
                        "reportCurrency": {
                            "value": 3155745.996256646,
                            "currency": "USD"
                        }
                    },
                    "cleanMarketValue": {
                        "value": 3155745.996256646,
                        "dealCurrency": {
                            "value": 3155745.996256646,
                            "currency": "USD"
                        },
                        "reportCurrency": {
                            "value": 3155745.996256646,
                            "currency": "USD"
                        }
                    }
                },
                "risk": {
                    "duration": {
                        "value": 0.0
                    },
                    "modifiedDuration": {
                        "value": 0.0148458356762826
                    },
                    "benchmarkHedgeNotional": {
                        "value": 0.0,
                        "currency": "USD"
                    },
                    "annuity": {
                        "value": 0.0,
                        "dealCurrency": {
                            "value": 0.0,
                            "currency": "USD"
                        },
                        "reportCurrency": {
                            "value": 0.0,
                            "currency": "USD"
                        }
                    },
                    "dv01": {
                        "value": 14.836305670440197,
                        "bp": 0.014836305670440197,
                        "dealCurrency": {
                            "value": 14.836305670440197,
                            "currency": "USD"
                        },
                        "reportCurrency": {
                            "value": 14.836305670440197,
                            "currency": "USD"
                        }
                    },
                    "pv01": {
                        "value": -6581.065383425914,
                        "bp": -6.581065383425914,
                        "dealCurrency": {
                            "value": -6581.065383425914,
                            "currency": "USD"
                        },
                        "reportCurrency": {
                            "value": -6581.065383425914,
                            "currency": "USD"
                        }
                    },
                    "br01": {
                        "value": 0.0,
                        "dealCurrency": {
                            "value": 0.0,
                            "currency": "USD"
                        },
                        "reportCurrency": {
                            "value": 0.0,
                            "currency": "USD"
                        }
                    }
                }
            }
        }

        """

        try:
            logger.info("Calling solve for irSwap with id")
            check_id(self._id)

            response = Client().ir_swap_resource.solve(
                instrument_id=self._id,
                fields=fields,
                pricing_preferences=pricing_preferences,
                market_data=market_data,
                return_market_data=return_market_data,
            )

            output = response.data
            logger.info("Called solve for irSwap with id")

            return output
        except Exception as err:
            logger.error("Error solve for irSwap with id.")
            check_exception_and_raise(err, logger)

    def value(
        self,
        *,
        pricing_preferences: Optional[IrPricingParameters] = None,
        market_data: Optional[MarketData] = None,
        return_market_data: Optional[bool] = None,
        fields: Optional[str] = None,
    ) -> IrSwapInstrumentValuationResponseFieldsOnResourceResponseData:
        """
        Calculate analytics for an interest rate swap stored on the platform, including valuation results, risk metrics, and other relevant measures.
        Provide an instrument ID in the request to perform the valuation.

        Parameters
        ----------
        pricing_preferences : IrPricingParameters, optional
            The parameters that control the computation of the analytics.
        market_data : MarketData, optional
            The market data used to compute the analytics.
        return_market_data : bool, optional
            Boolean property to determine if undelying market data used for calculation should be returned in the response
        fields : str, optional
            A parameter used to select the fields to return in response. If not provided, all fields will be returned.
            Some usage examples:
            1. Simply enumerating the fields, separating them by ',', e.g. 'fields=//please insert the selected fields here, e.g., field1, field2 //'
            2. Using parentheses to indicate nesting, e.g. 'fields= //please insert the selected field and subfields here, e.g., field1(subfield1, subfield2), field2(subfield3)//’
            3. Using forward slash '/' to indicate nesting, e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1/subfield1, field1/subfield2, field2/subfield3//’ (same result as example above)
            4. Operators can even be combined (forward slashes in brackets, not the way around), e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1(subfield1/subsubfield1), field2/subfield2//'

        Returns
        --------
        IrSwapInstrumentValuationResponseFieldsOnResourceResponseData


        Examples
        --------
        >>> # build the swap from 'LSEG/OIS_SOFR' template
        >>> fwd_start_sofr = create_from_vanilla_irs_template(template_reference = "LSEG/OIS_SOFR")
        >>>
        >>> # Swap needs to be saved in order for the value class method to be executable
        >>> fwd_start_sofr.save(name="sofr_fwd_start_swap_exm")
        >>>
        >>> # instantiate pricing parameters
        >>> pricing_parameters = IrPricingParameters()
        >>>
        >>> # solve the swap par rate
        >>> valuing_response_object = fwd_start_sofr.value(pricing_preferences=pricing_parameters)
        >>>
        >>> delete(name="sofr_fwd_start_swap_exm")
        >>>
        >>> print(js.dumps(valuation_response.analytics[0].valuation.as_dict(), indent=4))
        {
            "accrued": {
                "value": 0.0,
                "percent": 0.0,
                "dealCurrency": {
                    "value": 0.0,
                    "currency": "USD"
                },
                "reportCurrency": {
                    "value": 0.0,
                    "currency": "USD"
                }
            },
            "marketValue": {
                "value": 3155746.00060931,
                "dealCurrency": {
                    "value": 3155746.00060931,
                    "currency": "USD"
                },
                "reportCurrency": {
                    "value": 3155746.00060931,
                    "currency": "USD"
                }
            },
            "cleanMarketValue": {
                "value": 3155746.00060931,
                "dealCurrency": {
                    "value": 3155746.00060931,
                    "currency": "USD"
                },
                "reportCurrency": {
                    "value": 3155746.00060931,
                    "currency": "USD"
                }
            }
        }

        """

        try:
            logger.info("Calling value for irSwap with id")
            check_id(self._id)

            response = Client().ir_swap_resource.value(
                instrument_id=self._id,
                fields=fields,
                pricing_preferences=pricing_preferences,
                market_data=market_data,
                return_market_data=return_market_data,
            )

            output = response.data
            logger.info("Called value for irSwap with id")

            return output
        except Exception as err:
            logger.error("Error value for irSwap with id.")
            check_exception_and_raise(err, logger)

    def save(self, *, name: Optional[str] = None, space: Optional[str] = None) -> bool:
        """
        Save IrSwap instance in the platform store.

        Parameters
        ----------
        name : str, optional
            The IrSwap name. The name parameter must be specified when the object is first created. Thereafter it is optional. For first creation, name must follow the pattern '^[A-Za-z0-9_]{1,50}$'.
        space : str, optional
            The space where the IrSwap is stored. Space is like a namespace where resources are stored. By default there are two spaces:
            LSEG is reserved for LSEG maintained resources, HOME is reserved for user's default space. If space is not specified, HOME will be used.

        Returns
        --------
        bool, optional
            True, if saved successfully, otherwise None


        Examples
        --------
        >>> # build the swap from 'LSEG/OIS_SOFR' template
        >>> fwd_start_sofr = create_from_vanilla_irs_template(template_reference = "LSEG/OIS_SOFR")
        >>>
        >>> swap_id = "SOFR_OIS_1Y2Y"
        >>>
        >>> swap_space = "HOME"
        >>>
        >>> try:
        >>>     # If the instrument does not exist in HOME space, we can save it
        >>>     fwd_start_sofr.save(name=swap_id, space=swap_space)
        >>>     print(f"Instrument {swap_id} saved in {swap_space} space.")
        >>> except:
        >>>     # Check if the instrument already exists in HOME space
        >>>     fwd_start_sofr = load(name=swap_id, space=swap_space)
        >>>     print(f"Instrument {swap_id} already exists in {swap_space} space.")
        Instrument SOFR_OIS_1Y2Y saved in HOME space.

        """
        try:
            logger.info("Saving IrSwap")
            if self._id:
                if name and name != self._location.name or (space and space != self._location.space):
                    raise LibraryException("When saving an existing resource, you may not change the name or space")
                self._overwrite()
                logger.info("IrSwap saved")
            elif name:
                location = Location(name=name, space=space)
                self._create(location=location)
                logger.info(f"IrSwap saved to space: {self._location.space} name: {self._location.name}")
            else:
                raise LibraryException("When saving for the first time, name must be defined.")
            return True
        except Exception as err:
            logger.info("IrSwap save failed")
            check_exception_and_raise(err, logger)

    def clone(self) -> "IrSwap":
        """
        Return the same object, without id, name and space

        Parameters
        ----------


        Returns
        --------
        IrSwap
            The cloned IrSwap object


        Examples
        --------


        """
        definition = self._definition_class()
        definition._data = copy.deepcopy(self.definition._data)
        description = None
        if self.description:
            description = Description()
            description._data = copy.deepcopy(self.description._data)
        return self.__class__(definition=definition, description=description)
