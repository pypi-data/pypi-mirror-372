# pylint: disable=too-many-lines
# coding=utf-8


from enum import Enum

from corehttp.utils import CaseInsensitiveEnumMeta


class AccruedCalculationMethodEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of AccruedCalculationMethodEnum."""

    DCB_30_360 = "Dcb_30_360"
    DCB_30_360_US = "Dcb_30_360_US"
    DCB_30_360_GERMAN = "Dcb_30_360_German"
    DCB_30_360_ISDA = "Dcb_30_360_ISDA"
    DCB_30_365_ISDA = "Dcb_30_365_ISDA"
    DCB_30_365_GERMAN = "Dcb_30_365_German"
    DCB_30_365_BRAZIL = "Dcb_30_365_Brazil"
    DCB_30_ACTUAL_GERMAN = "Dcb_30_Actual_German"
    DCB_30_ACTUAL = "Dcb_30_Actual"
    DCB_30_ACTUAL_ISDA = "Dcb_30_Actual_ISDA"
    DCB_30_E_360_ISMA = "Dcb_30E_360_ISMA"
    DCB_ACTUAL_360 = "Dcb_Actual_360"
    DCB_ACTUAL_364 = "Dcb_Actual_364"
    DCB_ACTUAL_365 = "Dcb_Actual_365"
    DCB_ACTUAL_ACTUAL = "Dcb_Actual_Actual"
    DCB_ACTUAL_ACTUAL_ISDA = "Dcb_Actual_Actual_ISDA"
    DCB_ACTUAL_ACTUAL_AFB = "Dcb_Actual_Actual_AFB"
    DCB_WORKING_DAYS_252 = "Dcb_WorkingDays_252"
    DCB_ACTUAL_365_L = "Dcb_Actual_365L"
    DCB_ACTUAL_365_P = "Dcb_Actual_365P"
    DCB_ACTUAL_LEAP_DAY_365 = "Dcb_ActualLeapDay_365"
    DCB_ACTUAL_LEAP_DAY_360 = "Dcb_ActualLeapDay_360"
    DCB_ACTUAL_36525 = "Dcb_Actual_36525"
    DCB_ACTUAL_365_CANADIAN_CONVENTION = "Dcb_Actual_365_CanadianConvention"
    DCB_CONSTANT = "Dcb_Constant"


class AccruedRoundingEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of AccruedRoundingEnum."""

    ZERO = "Zero"
    ONE = "One"
    TWO = "Two"
    THREE = "Three"
    FOUR = "Four"
    FIVE = "Five"
    SIX = "Six"
    SEVEN = "Seven"
    EIGHT = "Eight"
    DEFAULT = "Default"
    UNROUNDED = "Unrounded"


class AccruedRoundingTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of AccruedRoundingTypeEnum."""

    NEAR = "Near"
    UP = "Up"
    DOWN = "Down"
    FLOOR = "Floor"
    CEIL = "Ceil"
    FACE_NEAR = "FaceNear"
    FACE_DOWN = "FaceDown"
    FACE_UP = "FaceUp"
    DEFAULT = "Default"


class AdjustInterestToPaymentDateEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of AdjustInterestToPaymentDateEnum."""

    UNADJUSTED = "Unadjusted"
    ADJUSTED = "Adjusted"


class AmortizationFrequencyEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of AmortizationFrequencyEnum."""

    ONCE = "Once"
    EVERY_COUPON = "EveryCoupon"
    EVERY2ND_COUPON = "Every2ndCoupon"
    EVERY3RD_COUPON = "Every3rdCoupon"
    EVERY4TH_COUPON = "Every4thCoupon"
    EVERY12TH_COUPON = "Every12thCoupon"
    ANNUAL = "Annual"
    SEMI_ANNUAL = "SemiAnnual"
    QUARTERLY = "Quarterly"
    MONTHLY = "Monthly"
    BI_MONTHLY = "BiMonthly"
    EVERYDAY = "Everyday"
    EVERY_WORKING_DAY = "EveryWorkingDay"
    EVERY7_DAYS = "Every7Days"
    EVERY14_DAYS = "Every14Days"
    EVERY28_DAYS = "Every28Days"
    EVERY30_DAYS = "Every30Days"
    EVERY91_DAYS = "Every91Days"
    EVERY182_DAYS = "Every182Days"
    EVERY364_DAYS = "Every364Days"
    EVERY365_DAYS = "Every365Days"
    EVERY90_DAYS = "Every90Days"
    EVERY92_DAYS = "Every92Days"
    EVERY93_DAYS = "Every93Days"
    EVERY180_DAYS = "Every180Days"
    EVERY183_DAYS = "Every183Days"
    EVERY184_DAYS = "Every184Days"
    EVERY4_MONTHS = "Every4Months"
    R2 = "R2"
    R4 = "R4"
    ZERO = "Zero"
    SCHEDULED = "Scheduled"


class AmortizationTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The type of amortization."""

    LINEAR = "Linear"
    """The amount repaid is the same each period, so the remaining amount decreases linearly."""
    ANNUITY = "Annuity"
    """The amount repaid is low at the beginning of the term and increases towards the end."""


class AsianTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The type of an Asian option based on whether the strike is fixed or not."""

    PRICE = "Price"
    """An Asian option in which the strike is predetermined and the average price of the underlying
    asset is used for payoff calculation.
    """
    STRIKE = "Strike"
    """An Asian option in which the average price of the underlying asset over the fixing period
    becomes the option's strike
    and is used with the final price of the underlying asset on the expiration date to calculate
    the payoff.
    """


class AverageTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The mathematical type used to calculate the average price of the underlying asset."""

    ARITHMETIC = "Arithmetic"
    """Calculates average by adding all values and dividing by the number of values."""
    GEOMETRIC = "Geometric"
    """Calculates average by multiplying all values and taking the nth root, where n is the number of
    values.
    """


class BarrierDirectionEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of BarrierDirectionEnum."""

    UP = "Up"
    DOWN = "Down"


class BarrierModeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The barrier mode that defines the timing and conditions under which the barrier level is
    monitored and can trigger activation.
    """

    AMERICAN = "American"
    """The conditions of a barrier option are monitored continuously throughout the entire lifetime of
    the option.
    """
    EUROPEAN = "European"
    """The conditions of a barrier option are only checked on the option's expiration date."""
    BERMUDAN = "Bermudan"
    """The conditions of a barrier option are monitored only on specific predefined dates during the
    option's lifetime.
    """


class BarrierTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of BarrierTypeEnum."""

    KNOCK_IN = "KnockIn"
    KNOCK_OUT = "KnockOut"
    KNOCK_IN_KNOCK_OUT = "KnockInKnockOut"
    KNOCK_OUT_KNOCK_IN = "KnockOutKnockIn"


class BasisSplineSmoothModelEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of BasisSplineSmoothModelEnum."""

    ANDERSON_SMOOTHING_SPLINE_MODEL = "AndersonSmoothingSplineModel"
    MC_CULLOCH_LINEAR_REGRESSION = "McCullochLinearRegression"
    WAGGONER_SMOOTHING_SPLINE_MODEL = "WaggonerSmoothingSplineModel"


class BenchmarkYieldSelectionModeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of BenchmarkYieldSelectionModeEnum."""

    INTERPOLATE = "Interpolate"
    NEAREST = "Nearest"


class BinaryTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The type of a binary option based on the trigger that activates it."""

    ONE_TOUCH = "OneTouch"
    """The option is activated (pays immediately) if the agreed price level of the underlying asset is
    reached at any time before the option expires.
    """
    NO_TOUCH = "NoTouch"
    """The option is activated if the agreed price level of the underlying asset is not reached before
    the option expires.
    """
    DIGITAL = "Digital"
    """The option is activated if the agreed price level of the underlying asset is reached on the
    option's expiration date.
    """


class BusinessSectorEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of BusinessSectorEnum."""

    ACADEMIC_AND_EDUCATIONAL_SERVICES = "AcademicAndEducationalServices"
    APPLIED_RESOURCES = "AppliedResources"
    AUTOMOBILES_AND_AUTO_PARTS = "AutomobilesAndAutoParts"
    BANKING_AND_INVESTMENT_SERVICES = "BankingAndInvestmentServices"
    CHEMICALS = "Chemicals"
    COLLECTIVE_INVESTMENTS = "CollectiveInvestments"
    CONSUMER_GOODS_CONGLOMERATES = "ConsumerGoodsConglomerates"
    CYCLICAL_CONSUMER_PRODUCTS = "CyclicalConsumerProducts"
    CYCLICAL_CONSUMER_SERVICES = "CyclicalConsumerServices"
    ENERGY_FOSSIL_FUELS = "EnergyFossilFuels"
    FINANCIAL_TECHNOLOGY_AND_INFRASTRUCTURE = "FinancialTechnologyAndInfrastructure"
    FOOD_AND_BEVERAGES = "FoodAndBeverages"
    FOOD_AND_DRUG_RETAILING = "FoodAndDrugRetailing"
    GOVERNMENT_ACTIVITY = "GovernmentActivity"
    HEALTHCARE_SERVICES_AND_EQUIPMENT = "HealthcareServicesAndEquipment"
    INDUSTRIAL_AND_COMMERCIAL_SERVICES = "IndustrialAndCommercialServices"
    INDUSTRIAL_GOODS = "IndustrialGoods"
    INSTITUTIONS_ASSOCIATIONS_AND_ORGANIZATIONS = "InstitutionsAssociationsAndOrganizations"
    INSURANCE = "Insurance"
    INVESTMENT_HOLDING_COMPANIES = "InvestmentHoldingCompanies"
    MINERAL_RESOURCES = "MineralResources"
    PERSONAL_AND_HOUSEHOLD_PRODUCTS_AND_SERVICES = "PersonalAndHouseholdProductsAndServices"
    PHARMACEUTICALS_AND_MEDICAL_RESEARCH = "PharmaceuticalsAndMedicalResearch"
    REAL_ESTATE = "RealEstate"
    RENEWABLE_ENERGY = "RenewableEnergy"
    RETAILERS = "Retailers"
    SOFTWARE_AND_IT_SERVICES = "SoftwareAndITServices"
    TECHNOLOGY_EQUIPMENT = "TechnologyEquipment"
    TELECOMMUNICATIONS_SERVICES = "TelecommunicationsServices"
    TRANSPORTATION = "Transportation"
    URANIUM = "Uranium"
    UTILITIES = "Utilities"


class CalendarAdjustmentEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of CalendarAdjustmentEnum."""

    CALENDAR = "Calendar"
    NO = "No"
    WEEKEND = "Weekend"


class CalibrationMethodEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of CalibrationMethodEnum."""

    BOOTSTRAP_APPROXIMATION = "BootstrapApproximation"
    GLOBAL_MINIMIZATION = "GlobalMinimization"
    GLOBAL_MINIMIZATION_LAST_INDEX = "GlobalMinimizationLastIndex"
    GLOBAL_MINIMIZATION_MATURITIES_WEIGHTED = "GlobalMinimizationMaturitiesWeighted"


class CalibrationModelEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of CalibrationModelEnum."""

    BASIS_SPLINE = "BasisSpline"
    BOOTSTRAP = "Bootstrap"
    NELSON_SIEGEL_SVENSSON = "NelsonSiegelSvensson"


class CalibrationTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of CalibrationTypeEnum."""

    BOOTSTRAP = "Bootstrap"
    OPTIMIZE = "Optimize"
    GLOBAL = "Global"


class CallPutEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """An indicator of whether an option is a call or a put."""

    CALL = "Call"
    """A call option gives the option holder the right to buy the underlying asset."""
    PUT = "Put"
    """A put option gives the option holder the right to sell the underlying asset."""


class CapFloorTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The type of an interest rate cap or an interest rate floor."""

    STANDARD = "Standard"
    """The cap or floor value applies to each interest period of the instrument."""
    PERIODIC = "Periodic"
    """The cap or floor value is incremented for each new interest period of the instrument."""
    LIFE_TIME = "LifeTime"
    """The cap or floor applies to the cumulative value of the interest paid over the life of the
    instrument.
    """
    FIRST_PERIOD = "FirstPeriod"
    """The cap or floor applies only to the first interest period of the instrument."""


class CategoryEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of CategoryEnum."""

    CONSTITUENTS = "Constituents"
    CURVE = "Curve"
    CURVE_PARAMETER = "CurveParameter"
    SHIFTING = "Shifting"
    TURN = "Turn"


class CdsConventionEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of CdsConventionEnum."""

    ISDA = "ISDA"
    USER_DEFINED = "UserDefined"


class CityNameEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of CityNameEnum."""

    AABENRAA = "Aabenraa"
    AALBORG = "Aalborg"
    ABIDJAN = "Abidjan"
    ABU_DHABI = "AbuDhabi"
    ACCRA = "Accra"
    AHMEDABAD = "Ahmedabad"
    AICHI = "Aichi"
    ALBERTA = "Alberta"
    ALGIERS = "Algiers"
    ALMATY = "Almaty"
    AMMAN = "Amman"
    AMSTERDAM = "Amsterdam"
    ANKARA = "Ankara"
    ANTANANARIVO = "Antananarivo"
    ANTWERPEN = "Antwerpen"
    ASTANA = "Astana"
    ASTI = "Asti"
    ASUNCION = "Asuncion"
    ATHENS = "Athens"
    ATLANTA = "Atlanta"
    AUCKLAND = "Auckland"
    AYLESBURY = "Aylesbury"
    BAGHDAD = "Baghdad"
    BAKU = "Baku"
    BANGALORE = "Bangalore"
    BANGKOK = "Bangkok"
    BANJA_LUKA = "BanjaLuka"
    BARCELONA = "Barcelona"
    BASSETERRE = "Basseterre"
    BEDMINSTER = "Bedminster"
    BEIJING = "Beijing"
    BEIRUT = "Beirut"
    BELGRADE = "Belgrade"
    BERGAMO = "Bergamo"
    BERGEN = "Bergen"
    BERLIN = "Berlin"
    BERMUDA = "Bermuda"
    BERNE = "Berne"
    BIELLA = "Biella"
    BILBAO = "Bilbao"
    BISHKEK = "Bishkek"
    BLANTYRE = "Blantyre"
    BOCA_RATON = "BocaRaton"
    BOGOTA = "Bogota"
    BOLOGNA = "Bologna"
    BOSTON = "Boston"
    BRADFORD = "Bradford"
    BRATISLAVA = "Bratislava"
    BREMEN = "Bremen"
    BRIDGETOWN = "Bridgetown"
    BRUSSELS = "Brussels"
    BRYANSTON_SANDTON = "BryanstonSandton"
    BUCHAREST = "Bucharest"
    BUDAORS = "Budaors"
    BUDAPEST = "Budapest"
    BUENOS_AIRES = "BuenosAires"
    CAIRO = "Cairo"
    CALCUTTA = "Calcutta"
    CALGARY = "Calgary"
    CARACAS = "Caracas"
    CASABLANCA = "Casablanca"
    CHARLOTTE = "Charlotte"
    CHATHAM = "Chatham"
    CHICAGO = "Chicago"
    CHISINAU = "Chisinau"
    CHITTAGONG = "Chittagong"
    CHIYODA_KU = "ChiyodaKu"
    CLUJ_NAPOCA = "ClujNapoca"
    COLOMBO = "Colombo"
    COPENHAGEN = "Copenhagen"
    CORDOBA = "Cordoba"
    CORRIENTES = "Corrientes"
    CURITIBA = "Curitiba"
    CYBERCITY_EBENE = "CybercityEbene"
    DALIAN = "Dalian"
    DALLAS = "Dallas"
    DAMASCUS = "Damascus"
    DAR_ES_SALAAM = "DarEsSalaam"
    DELHI = "Delhi"
    DHAKA = "Dhaka"
    DNIPROPETROVSK = "Dnipropetrovsk"
    DOHA = "Doha"
    DOUALA = "Douala"
    DUBAI = "Dubai"
    DUBLIN = "Dublin"
    DUESSELDORF = "Duesseldorf"
    EBENE = "Ebene"
    EBENE_CITY = "EbeneCity"
    EDEN_ISLAND = "EdenIsland"
    EDINBURGH = "Edinburgh"
    EKATERINBURG = "Ekaterinburg"
    EL_SALVADOR = "ElSalvador"
    ESCHBORN = "Eschborn"
    ESCH_SUR_ALZETTE = "EschSurAlzette"
    ESPIRITO_SANTO = "EspiritoSanto"
    ESPOO = "Espoo"
    FIAC = "Fiac"
    FIRENZE = "Firenze"
    FLORENCE = "Florence"
    FRANKFURT = "Frankfurt"
    FRANKFURT_AM_MAIN = "FrankfurtAmMain"
    FUKUOKA = "Fukuoka"
    GABORONE = "Gaborone"
    GANDHINAGAR = "Gandhinagar"
    GENEVA = "Geneva"
    GENOVA = "Genova"
    GEORGETOWN = "Georgetown"
    GIBRALTAR = "Gibraltar"
    GIFT_CITY_GANDHINAGAR = "GiftCityGandhinagar"
    GLENVIEW = "Glenview"
    GREAT_NECK = "GreatNeck"
    GREENWICH = "Greenwich"
    GRINDSTED = "Grindsted"
    GUATEMALA = "Guatemala"
    GUAYAQUIL = "Guayaquil"
    GUAYNABO = "Guaynabo"
    GUILDFORD = "Guildford"
    HAMBURG = "Hamburg"
    HAMILTON = "Hamilton"
    HANNOVER = "Hannover"
    HANOI = "Hanoi"
    HARARE = "Harare"
    HELSINKI = "Helsinki"
    HIROSHIMA = "Hiroshima"
    HO_CHI_MINH_CITY = "HoChiMinhCity"
    HONG_KONG = "HongKong"
    HORSENS = "Horsens"
    HOVE = "Hove"
    HRADEC_KRALOVE = "HradecKralove"
    ILLINOIS = "Illinois"
    INDORE_MADHYA_PRADESH = "IndoreMadhyaPradesh"
    ISLAMABAD = "Islamabad"
    ISTANBUL = "Istanbul"
    IZMIR = "Izmir"
    JAEN = "Jaen"
    JAKARTA = "Jakarta"
    JERSEY_CITY = "JerseyCity"
    JOHANNESBURG = "Johannesburg"
    KAMPALA = "Kampala"
    KANSAS_CITY = "KansasCity"
    KARACHI = "Karachi"
    KATHMANDU = "Kathmandu"
    KHARKOV = "Kharkov"
    KHARTOUM = "Khartoum"
    KIEL = "Kiel"
    KIEV = "Kiev"
    KIGALI = "Kigali"
    KINGSTON = "Kingston"
    KINGSTOWN = "Kingstown"
    KLAGENFURT_AM_WOERTHERSEE = "KlagenfurtAmWoerthersee"
    KOBE = "Kobe"
    KONGSVINGER = "Kongsvinger"
    KRAKOW = "Krakow"
    KUALA_LUMPUR = "KualaLumpur"
    KUWAIT = "Kuwait"
    KYOTO = "Kyoto"
    LA_PAZ = "LaPaz"
    LABUAN = "Labuan"
    LAGOS = "Lagos"
    LAHORE = "Lahore"
    LANE_COVE = "LaneCove"
    LAO = "Lao"
    LARNACA = "Larnaca"
    LEIPZIG = "Leipzig"
    LENEXA = "Lenexa"
    LEUVEN = "Leuven"
    LIMA = "Lima"
    LIMASSOL = "Limassol"
    LINZ = "Linz"
    LISBON = "Lisbon"
    LJUBLJANA = "Ljubljana"
    LONDON = "London"
    LOS_ANGELES = "LosAngeles"
    LUANDA = "Luanda"
    LUSAKA = "Lusaka"
    LUXEMBOURG = "Luxembourg"
    LUZERN = "Luzern"
    MADRAS = "Madras"
    MADRID = "Madrid"
    MAKATI_CITY = "MakatiCity"
    MALE = "Male"
    MANAGUA = "Managua"
    MANAMA = "Manama"
    MANILA = "Manila"
    MAPUTO = "Maputo"
    MARINGA = "Maringa"
    MBABANE = "Mbabane"
    MELBOURNE = "Melbourne"
    MENDOZA = "Mendoza"
    MEXICO = "Mexico"
    MIAMI = "Miami"
    MILAN = "Milan"
    MILTON_KEYNES = "MiltonKeynes"
    MINNEAPOLIS = "Minneapolis"
    MINSK = "Minsk"
    MONTEVIDEO = "Montevideo"
    MONTREAL = "Montreal"
    MOORPARK = "Moorpark"
    MOSCOW = "Moscow"
    MOUNT_PLEASANT = "MountPleasant"
    MUENCHEN = "Muenchen"
    MUMBAI = "Mumbai"
    MUNICH = "Munich"
    MUSCAT = "Muscat"
    NABLUS = "Nablus"
    NACKA = "Nacka"
    NAGOYA = "Nagoya"
    NAIROBI = "Nairobi"
    NARBERTH = "Narberth"
    NASAU = "Nasau"
    NEW_YORK_CITY = "NewYorkCity"
    NEWCASTLE = "Newcastle"
    NICOSIA = "Nicosia"
    NIGITA = "Nigita"
    NIZHNIY_NOVGOROD = "NizhniyNovgorod"
    NORTH_BERGEN = "NorthBergen"
    NOVOSIBIRSK = "Novosibirsk"
    NYON = "Nyon"
    ODESSA = "Odessa"
    OLDENBURG = "Oldenburg"
    OSAKA = "Osaka"
    OSLO = "Oslo"
    OSTSTEINBEK = "Oststeinbek"
    PADOVA = "Padova"
    PALMA_DE_MALLORCA = "PalmaDeMallorca"
    PANAMA = "Panama"
    PARIS = "Paris"
    PASIG_CITY = "PasigCity"
    PHILADELPHIA = "Philadelphia"
    PHNOM_PENH = "PhnomPenh"
    PHOENIX = "Phoenix"
    PODGORICA = "Podgorica"
    POLOKWANE = "Polokwane"
    PORT_LOUIS = "PortLouis"
    PORT_MORESBY = "PortMoresby"
    PORT_OF_SPAIN = "PortOfSpain"
    PORT_VILA = "PortVila"
    PORTO = "Porto"
    PRAGUE = "Prague"
    PRAIA = "Praia"
    PRINCETON = "Princeton"
    PURCHASE = "Purchase"
    QUITO = "Quito"
    RANDERS = "Randers"
    RED_BANK = "RedBank"
    REGENSBURG = "Regensburg"
    REYKJAVIK = "Reykjavik"
    RIGA = "Riga"
    RIO_DE_JANEIRO = "RioDeJaneiro"
    RIYADH = "Riyadh"
    ROAD_TOWN = "RoadTown"
    RODGAU = "Rodgau"
    ROME = "Rome"
    ROSARIO = "Rosario"
    ROSTOV = "Rostov"
    SABADELL = "Sabadell"
    SAINT_PETERSBURG = "SaintPetersburg"
    SALZBURG = "Salzburg"
    SAMARA = "Samara"
    SAN_CARLOS = "SanCarlos"
    SAN_FRANCISCO = "SanFrancisco"
    SAN_JOSE = "SanJose"
    SAN_PEDRO_SULA = "SanPedroSula"
    SANTA_FE = "SantaFe"
    SANTANDER = "Santander"
    SANTIAGO = "Santiago"
    SANTO_DOMINGO = "SantoDomingo"
    SAO_PAULO = "SaoPaulo"
    SAPPORO = "Sapporo"
    SARAJEVO = "Sarajevo"
    SCHWERIN = "Schwerin"
    SEA_GIRT = "SeaGirt"
    SEOUL = "Seoul"
    SHANGHAI = "Shanghai"
    SHENZHEN = "Shenzhen"
    SHERTOGENBOSCH = "Shertogenbosch"
    SHIMONOSEKI = "Shimonoseki"
    SIBIU = "Sibiu"
    SILKEBORG = "Silkeborg"
    SINGAPORE = "Singapore"
    SKOPJE = "Skopje"
    SLIEMA = "Sliema"
    SOFIA = "Sofia"
    SPLIT = "Split"
    ST_ALBANS = "StAlbans"
    ST_JOHN = "StJohn"
    ST_PETER_PORT = "StPeterPort"
    STAMFORD = "Stamford"
    STOCKHOLM = "Stockholm"
    STUTTGART = "Stuttgart"
    SURABAYA = "Surabaya"
    SUVA = "Suva"
    SYDNEY = "Sydney"
    TAIPEI = "Taipei"
    TAIWAN = "Taiwan"
    TALLINN = "Tallinn"
    TASHKENT = "Tashkent"
    TBILISI = "Tbilisi"
    TEGUCIGALPA = "Tegucigalpa"
    TEHRAN = "Tehran"
    TEL_AVIV = "TelAviv"
    THE_HAGUE = "TheHague"
    THE_WOODLANDS = "TheWoodlands"
    TIRANA = "Tirana"
    TOKYO = "Tokyo"
    TORINO = "Torino"
    TORONTO = "Toronto"
    TORSHAVN = "Torshavn"
    TORTOLA = "Tortola"
    TRIPOLI = "Tripoli"
    TROMSO = "Tromso"
    TRONDHEIM = "Trondheim"
    TUCUMAN = "Tucuman"
    TUNIS = "Tunis"
    ULAAN_BAATAR = "UlaanBaatar"
    UNTERSCHLEISSHEM = "Unterschleisshem"
    UTRECHT = "Utrecht"
    VADUZ = "Vaduz"
    VALENCIA = "Valencia"
    VALLETTA = "Valletta"
    VALPARAISO = "Valparaiso"
    VANCOUVER = "Vancouver"
    VARAZDIN = "Varazdin"
    VICTORIA = "Victoria"
    VICTORIA_FALLS = "VictoriaFalls"
    VIENNA = "Vienna"
    VILA = "Vila"
    VILNIUS = "Vilnius"
    VLADIVOSTOK = "Vladivostok"
    WARSAW = "Warsaw"
    WASHINGTON = "Washington"
    WILLEMSTAD = "Willemstad"
    WILMINGTON = "Wilmington"
    WINDHOEK = "Windhoek"
    WINNIPEG = "Winnipeg"
    WINTER_PARK = "WinterPark"
    WROCLAW = "Wroclaw"
    WUXI = "Wuxi"
    YEREVAN = "Yerevan"
    ZAGREB = "Zagreb"
    ZARAGOZA = "Zaragoza"
    ZHENGZHOU = "Zhengzhou"
    ZILINA = "Zilina"
    ZUG = "Zug"
    ZURICH = "Zurich"


class CodeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of CodeEnum."""

    AAUCPI = "AAUCPI"
    ABECPI = "ABECPI"
    ABRIGPM = "ABRIGPM"
    ABRIPC10 = "ABRIPC10"
    ADECPI = "ADECPI"
    AESCPI = "AESCPI"
    AFRCPIXT = "AFRCPIXT"
    AGBRPI = "AGBRPI"
    AILCPI = "AILCPI"
    AITCPI = "AITCPI"
    AITCPIXT = "AITCPIXT"
    AJPCPICOR = "AJPCPICOR"
    AUSCPI = "AUSCPI"
    AXZHICPXT = "AXZHICPXT"
    AZACPI = "AZACPI"
    ERROR_ANALYSE_INVALID_CURRENCIES = "ErrorAnalyse_InvalidCurrencies"
    ERROR_ANALYSE_INVALID_DATE = "ErrorAnalyse_InvalidDate"
    ERROR_ANALYSE_INVALID_LEG_TYPE_FROM_CROSS_TYPE = "ErrorAnalyse_InvalidLegTypeFromCrossType"
    ERROR_ANALYSE_INVALID_PRICING_ITEM = "ErrorAnalyse_InvalidPricingItem"
    ERROR_ANALYSE_NO_ANALYZER = "ErrorAnalyse_NoAnalyzer"
    ERROR_ANALYSE_NO_CENTRAL_BANK_DATE = "ErrorAnalyse_NoCentralBankDate"
    ERROR_ANALYSE_NO_SUITABLE_FX_CANDIDATE = "ErrorAnalyse_NoSuitableFxCandidate"
    ERROR_ANALYSE_NO_SUITABLE_VOLATILITY_SOURCE = "ErrorAnalyse_NoSuitableVolatilitySource"
    ERROR_ANALYSE_NO_SWAP_TYPE = "ErrorAnalyse_NoSwapType"
    ERROR_ANALYSE_SUB_ITEM_ANALYSIS_ERROR = "ErrorAnalyse_SubItemAnalysisError"
    ERROR_ANALYSE_UNSPECIFIED = "ErrorAnalyse_Unspecified"
    ERROR_ANALYSE_UNSUPPORTED_CCY_PRICING_FOR_PREFERRED_SECURITIES = (
        "ErrorAnalyse_UnsupportedCcyPricingForPreferredSecurities"
    )
    ERROR_ANALYSE_UNSUPPORTED_INSTRUMENT = "ErrorAnalyse_UnsupportedInstrument"
    ERROR_BUSINESS_CALENDAR_CALENDAR_DAY_OF_MONTH_INVALID_RANGE = "ErrorBusinessCalendar_CalendarDayOfMonthInvalidRange"
    ERROR_BUSINESS_CALENDAR_CALENDAR_NOT_FOUND = "ErrorBusinessCalendar_CalendarNotFound"
    ERROR_BUSINESS_CALENDAR_DAY_OF_MONTH_EMPTY = "ErrorBusinessCalendar_DayOfMonthEmpty"
    ERROR_BUSINESS_CALENDAR_DAY_OF_WEEK_OR_INDEX_OR_MONTH_EMPTY = "ErrorBusinessCalendar_DayOfWeekOrIndexOrMonthEmpty"
    ERROR_BUSINESS_CALENDAR_DEFINE_BOTH_START_DATE_AND_END_DATE_IN_THE_PAST = (
        "ErrorBusinessCalendar_DefineBothStartDateAndEndDateInThePast"
    )
    ERROR_BUSINESS_CALENDAR_END_DATE_EARLIER_START_DATE = "ErrorBusinessCalendar_EndDateEarlierStartDate"
    ERROR_BUSINESS_CALENDAR_END_DATE_MUST_BE_GREATER_THAN_START_DATE = (
        "ErrorBusinessCalendar_EndDateMustBeGreaterThanStartDate"
    )
    ERROR_BUSINESS_CALENDAR_HOLIDAY_RULE_EMPTY = "ErrorBusinessCalendar_HolidayRuleEmpty"
    ERROR_BUSINESS_CALENDAR_HOLIDAY_RULE_FORMAT_NOT_SUPPORTED = "ErrorBusinessCalendar_HolidayRuleFormatNotSupported"
    ERROR_BUSINESS_CALENDAR_HOLIDAY_RULE_POSITION_EMPTY = "ErrorBusinessCalendar_HolidayRulePositionEmpty"
    ERROR_BUSINESS_CALENDAR_INVALID_CALCULATION_DATE = "ErrorBusinessCalendar_InvalidCalculationDate"
    ERROR_BUSINESS_CALENDAR_INVALID_CALENDAR_OUTPUT = "ErrorBusinessCalendar_InvalidCalendarOutput"
    ERROR_BUSINESS_CALENDAR_INVALID_DATE_STRING = "ErrorBusinessCalendar_InvalidDateString"
    ERROR_BUSINESS_CALENDAR_INVALID_END_DATE = "ErrorBusinessCalendar_InvalidEndDate"
    ERROR_BUSINESS_CALENDAR_INVALID_FREQUENCY = "ErrorBusinessCalendar_InvalidFrequency"
    ERROR_BUSINESS_CALENDAR_INVALID_HOLIDAY_OUTPUT = "ErrorBusinessCalendar_InvalidHolidayOutput"
    ERROR_BUSINESS_CALENDAR_INVALID_PERIOD = "ErrorBusinessCalendar_InvalidPeriod"
    ERROR_BUSINESS_CALENDAR_INVALID_REF_MONTH = "ErrorBusinessCalendar_InvalidRefMonth"
    ERROR_BUSINESS_CALENDAR_INVALID_START_DATE = "ErrorBusinessCalendar_InvalidStartDate"
    ERROR_BUSINESS_CALENDAR_NAME_EMPTY = "ErrorBusinessCalendar_NameEmpty"
    ERROR_BUSINESS_CALENDAR_NEGATIVE_COUNT = "ErrorBusinessCalendar_NegativeCount"
    ERROR_BUSINESS_CALENDAR_NO_END_DATE_OR_COUNT = "ErrorBusinessCalendar_NoEndDateOrCount"
    ERROR_BUSINESS_CALENDAR_NO_RESULT_RETURNED_BY_ADFIN = "ErrorBusinessCalendar_NoResultReturnedByAdfin"
    ERROR_BUSINESS_CALENDAR_SET_ONLY_DAY_OF_WEEK_OR_CALENDAR_DAY_OF_MONTH = (
        "ErrorBusinessCalendar_SetOnlyDayOfWeekOrCalendarDayOfMonth"
    )
    ERROR_BUSINESS_CALENDAR_SET_ONLY_END_DATE_OR_COUNT = "ErrorBusinessCalendar_SetOnlyEndDateOrCount"
    ERROR_BUSINESS_CALENDAR_SPECIFY_CALENDAR_DAY_OF_MONTH = "ErrorBusinessCalendar_SpecifyCalendarDayOfMonth"
    ERROR_BUSINESS_CALENDAR_SPECIFY_DAY_OF_WEEK = "ErrorBusinessCalendar_SpecifyDayOfWeek"
    ERROR_BUSINESS_CALENDAR_SPECIFY_MONTHLY_FREQUENCY = "ErrorBusinessCalendar_SpecifyMonthlyFrequency"
    ERROR_BUSINESS_CALENDAR_SPECIFY_WEEKLY_FREQUENCY = "ErrorBusinessCalendar_SpecifyWeeklyFrequency"
    ERROR_BUSINESS_CALENDAR_START_DATE_AFTER_END_DATE = "ErrorBusinessCalendar_StartDateAfterEndDate"
    ERROR_BUSINESS_CALENDAR_TOO_MANY_CALENDARS = "ErrorBusinessCalendar_TooManyCalendars"
    ERROR_BUSINESS_CALENDAR_TOO_MANY_CURRENCIES = "ErrorBusinessCalendar_TooManyCurrencies"
    ERROR_CVA_INPUT = "ErrorCvaInput"
    ERROR_CVA_INPUT_INVALID_CSA_DEFINITION = "ErrorCvaInput_InvalidCSADefinition"
    ERROR_CVA_INPUT_INVALID_CREDIT_CURVE = "ErrorCvaInput_InvalidCreditCurve"
    ERROR_CVA_INPUT_INVALID_INSTRUMENT_TYPE = "ErrorCvaInput_InvalidInstrumentType"
    ERROR_CVA_INPUT_INVALID_VOLATILITY_MODEL = "ErrorCvaInput_InvalidVolatilityModel"
    ERROR_CVA_INPUT_MISSING_CSA_DEFINITION = "ErrorCvaInput_MissingCSADefinition"
    ERROR_CVA_INPUT_NO_CSA_DEFINED = "ErrorCvaInput_NoCSADefined"
    ERROR_CVA_INPUT_NO_ITEM_DEFINED = "ErrorCvaInput_NoItemDefined"
    ERROR_CVA_PRICING_MISSING_RECOVERY_RATE = "ErrorCvaPricing_MissingRecoveryRate"
    ERROR_CVA_PRICING_PRICE_IT_ERROR = "ErrorCvaPricing_PriceItError"
    ERROR_CVA_PRICING_PRICE_IT_FIXINGS = "ErrorCvaPricing_PriceItFixings"
    ERROR_CVA_PRICING_PRICE_IT_INPUT_ERROR = "ErrorCvaPricing_PriceItInputError"
    ERROR_FX_VOL_SURF_INPUT_DEFINE_DATA_POINTS_FOR_LIST = "ErrorFxVolSurfInput_DefineDataPointsForList"
    ERROR_FX_VOL_SURF_INPUT_DEFINE_SURFACE_LAYOUT_FILTER_IS_ATM_FOR_LIST = (
        "ErrorFxVolSurfInput_DefineSurfaceLayoutFilterIsAtmForList"
    )
    ERROR_FX_VOL_SURF_INPUT_EMPTY_CUTOFF_TIME = "ErrorFxVolSurfInput_EmptyCutoffTime"
    ERROR_FX_VOL_SURF_INPUT_EMPTY_CUTOFF_TIME_ZONE = "ErrorFxVolSurfInput_EmptyCutoffTimeZone"
    ERROR_FX_VOL_SURF_INPUT_INVALID_CUTOFF_TIME = "ErrorFxVolSurfInput_InvalidCutoffTime"
    ERROR_FX_VOL_SURF_INPUT_INVALID_CUTOFF_TIME_ZONE = "ErrorFxVolSurfInput_InvalidCutoffTimeZone"
    ERROR_FX_VOL_SURF_INPUT_MATRIX_MODE = "ErrorFxVolSurfInput_MatrixMode"
    ERROR_FX_VOL_SURF_INPUT_OUTPUT_FIELD = "ErrorFxVolSurfInput_OutputField"
    ERROR_MARKET_DATA_ACCESS_DENIED = "ErrorMarketData_Access_Denied"
    ERROR_MARKET_DATA_ASSIGNMENT = "ErrorMarketData_Assignment"
    ERROR_MARKET_DATA_EMPTY_CALIBRATION_PARAMETERS = "ErrorMarketData_EmptyCalibrationParameters"
    ERROR_MARKET_DATA_EMPTY_DISCOUNT_CURVE = "ErrorMarketData_EmptyDiscountCurve"
    ERROR_MARKET_DATA_EMPTY_DIVIDEND_CURVE = "ErrorMarketData_EmptyDividendCurve"
    ERROR_MARKET_DATA_EMPTY_FORWARD_CURVE = "ErrorMarketData_EmptyForwardCurve"
    ERROR_MARKET_DATA_EMPTY_FX_SPOT_POINT = "ErrorMarketData_EmptyFxSpotPoint"
    ERROR_MARKET_DATA_EMPTY_FX_VOL_SURFACE = "ErrorMarketData_EmptyFxVolSurface"
    ERROR_MARKET_DATA_EMPTY_RATE_CURVE = "ErrorMarketData_EmptyRateCurve"
    ERROR_MARKET_DATA_FIXING_INFO = "ErrorMarketData_FixingInfo"
    ERROR_MARKET_DATA_INVALID_FX_CURVE = "ErrorMarketData_InvalidFxCurve"
    ERROR_MARKET_DATA_INVALID_SWAP_CURVE = "ErrorMarketData_InvalidSwapCurve"
    ERROR_MARKET_DATA_NO_CURVE_SERVICE_DATA = "ErrorMarketData_NoCurveService_Data"
    ERROR_MARKET_DATA_NO_DATA_CLOUD_DATA = "ErrorMarketData_NoDataCloud_Data"
    ERROR_MARKET_DATA_NO_HISTORICAL_FX_RATE = "ErrorMarketData_NoHistoricalFxRate"
    ERROR_MARKET_DATA_NO_IDN_CURVE_FOR_THIS_CURRENCY = "ErrorMarketData_NoIdnCurve_ForThisCurrency"
    ERROR_MARKET_DATA_NO_QUOTES_FROM_MARKET = "ErrorMarketData_NoQuotesFromMarket"
    ERROR_MARKET_DATA_NO_REAL_TIME_DATA = "ErrorMarketData_NoRealTime_Data"
    ERROR_MARKET_DATA_NO_SEARCH_DATA = "ErrorMarketData_NoSearch_Data"
    ERROR_MARKET_DATA_NO_TIME_SERIES_DATA = "ErrorMarketData_NoTimeSeries_Data"
    ERROR_MARKET_DATA_NOT_FOUND = "ErrorMarketData_NotFound"
    ERROR_MARKET_DATA_TOO_MANY_MARKET_DATA_REQUESTS = "ErrorMarketData_TooManyMarketDataRequests"
    ERROR_MARKET_DATA_UNSPECIFIED = "ErrorMarketData_Unspecified"
    ERROR_MARKET_DATA_WRONG_ANALYZED_ITEM = "ErrorMarketData_WrongAnalyzedItem"
    ERROR_MARKET_DATA_WRONG_CSV_FILE_FORMAT = "ErrorMarketData_WrongCsvFileFormat"
    ERROR_MARKET_DATA_WRONG_OVERRIDE = "ErrorMarketData_WrongOverride"
    ERROR_MISSING_INPUT_GREEKS_FAILED = "ErrorMissingInput_GreeksFailed"
    ERROR_MISSING_INPUT_IMPLIED_VOL_FAILED = "ErrorMissingInput_ImpliedVolFailed"
    ERROR_MISSING_INPUT_NO_TENOR = "ErrorMissingInput_NoTenor"
    ERROR_MISSING_INPUT_PREMIUM_FAILED = "ErrorMissingInput_PremiumFailed"
    ERROR_PRICING_ACCRUED_COMPUTATION = "ErrorPricing_AccruedComputation"
    ERROR_PRICING_ADFIN = "ErrorPricing_Adfin"
    ERROR_PRICING_ASSET_SWAP_SPREAD_COMPUTATION = "ErrorPricing_AssetSwapSpreadComputation"
    ERROR_PRICING_BOND_FUTURE_END_DATE = "ErrorPricing_BondFutureEndDate"
    ERROR_PRICING_BOND_PROCEEDS = "ErrorPricing_BondProceeds"
    ERROR_PRICING_BRENT_SOLVER = "ErrorPricing_BrentSolver"
    ERROR_PRICING_CALCULATION_OUTPUT_EMPTY = "ErrorPricing_CalculationOutputEmpty"
    ERROR_PRICING_CASH_FLOWS_COMPUTATION = "ErrorPricing_CashFlowsComputation"
    ERROR_PRICING_CFC_CALCULATION_ERROR = "ErrorPricing_CfcCalculationError"
    ERROR_PRICING_CONV_SPREAD_COMPUTATION = "ErrorPricing_ConvSpreadComputation"
    ERROR_PRICING_DATES_COMPUTATION = "ErrorPricing_DatesComputation"
    ERROR_PRICING_DCB_CONSTANT = "ErrorPricing_Dcb_Constant"
    ERROR_PRICING_DIVIDE_BY_ZERO = "ErrorPricing_Divide_By_Zero"
    ERROR_PRICING_GREEKS_COMPUTATION = "ErrorPricing_GreeksComputation"
    ERROR_PRICING_IBOR_RATE_COMPUTATION = "ErrorPricing_IborRateComputation"
    ERROR_PRICING_IMPLIED_PREP_SPEED = "ErrorPricing_ImpliedPrepSpeed"
    ERROR_PRICING_IMPLIED_VOL_COMPUTATION = "ErrorPricing_ImpliedVolComputation"
    ERROR_PRICING_INSTRUMENT_NOT_MANAGED = "ErrorPricing_InstrumentNotManaged"
    ERROR_PRICING_INVALID_INPUT_INSTRUMENT_NOT_LISTED_YET = "ErrorPricing_InvalidInput_InstrumentNotListedYet"
    ERROR_PRICING_INVALID_INPUT_INVALID_RATE = "ErrorPricing_InvalidInput_InvalidRate"
    ERROR_PRICING_INVALID_INSTRUMENT = "ErrorPricing_InvalidInstrument"
    ERROR_PRICING_NO_HISTORICAL_FX_RATE = "ErrorPricing_NoHistoricalFxRate"
    ERROR_PRICING_NO_LEGS = "ErrorPricing_NoLegs"
    ERROR_PRICING_NO_RESULT_RETURNED = "ErrorPricing_NoResultReturned"
    ERROR_PRICING_NO_SOURCE_CURRENCY = "ErrorPricing_NoSourceCurrency"
    ERROR_PRICING_NO_TARGET_CURRENCY = "ErrorPricing_NoTargetCurrency"
    ERROR_PRICING_NOTIONAL_COMPUTATION = "ErrorPricing_NotionalComputation"
    ERROR_PRICING_NPV_COMPUTATION = "ErrorPricing_NpvComputation"
    ERROR_PRICING_OAS_COMPUTATION = "ErrorPricing_OASComputation"
    ERROR_PRICING_OPR_INVALID_ASSET_TYPE = "ErrorPricing_OprInvalidAssetType"
    ERROR_PRICING_OUT_PUT_IS_EMPTY = "ErrorPricing_OutPutIsEmpty"
    ERROR_PRICING_PAR_CAP_STRIKE_COMPUTATION = "ErrorPricing_ParCapStrikeComputation"
    ERROR_PRICING_PAR_FLOOR_STRIKE_COMPUTATION = "ErrorPricing_ParFloorStrikeComputation"
    ERROR_PRICING_PAR_RATE_COMPUTATION = "ErrorPricing_ParRateComputation"
    ERROR_PRICING_PAR_SPREAD_COMPUTATION = "ErrorPricing_ParSpreadComputation"
    ERROR_PRICING_PREMIUM_COMPUTATION = "ErrorPricing_PremiumComputation"
    ERROR_PRICING_PRICE_IT = "ErrorPricing_PriceIt"
    ERROR_PRICING_PRICE_SIDE_NOT_AVAILABLE = "ErrorPricing_PriceSideNotAvailable"
    ERROR_PRICING_PRICING_ANALYSIS = "ErrorPricing_PricingAnalysis"
    ERROR_PRICING_REPO_END_DATES = "ErrorPricing_RepoEndDates"
    ERROR_PRICING_REPO_PRICING_END_DATE = "ErrorPricing_RepoPricingEndDate"
    ERROR_PRICING_REPO_PRICING_ERROR = "ErrorPricing_RepoPricingError"
    ERROR_PRICING_RISK_MEASURES = "ErrorPricing_RiskMeasures"
    ERROR_PRICING_SENSITIVITY_COMPUTATION = "ErrorPricing_SensitivityComputation"
    ERROR_PRICING_SETTLEMENT_CONVENTION = "ErrorPricing_SettlementConvention"
    ERROR_PRICING_SOLVER_ERROR = "ErrorPricing_SolverError"
    ERROR_PRICING_STRUCTURED_PRODUCTS_PRICING = "ErrorPricing_StructuredProducts_Pricing"
    ERROR_PRICING_SUB_ITEM_DATA_NOT_FOUND = "ErrorPricing_SubItem_DataNotFound"
    ERROR_PRICING_TOO_MANY_REQUESTS = "ErrorPricing_TooManyRequests"
    ERROR_PRICING_TRADE_DATE_INVALID_FOR_TRADE_DATE_ACCRUED = "ErrorPricing_TradeDateInvalidForTradeDateAccrued"
    ERROR_PRICING_UNABLE_TO_INTERPOLATE = "ErrorPricing_UnableToInterpolate"
    ERROR_PRICING_UNHANDLED_CURRENCY = "ErrorPricing_UnhandledCurrency"
    ERROR_PRICING_UNSPECIFIED = "ErrorPricing_Unspecified"
    ERROR_PRICING_UPFRONT_COMPUTATION = "ErrorPricing_UpfrontComputation"
    ERROR_PRICING_VALUATION = "ErrorPricing_Valuation"
    ERROR_PRICING_VOL_SURF = "ErrorPricing_VolSurf"
    ERROR_PRICING_Z_SPREAD_COMPUTATION = "ErrorPricing_ZSpreadComputation"
    ERROR_PRICING_INPUT_ERROR = "ErrorPricing_inputError"
    ERROR_RATE_SURF_INPUT_CURRENCY = "ErrorRateSurfInput_Currency"
    ERROR_RATE_SURF_INPUT_DEFINITION_DATE = "ErrorRateSurfInput_DefinitionDate"
    ERROR_STRIPLET_DATES_INVALID_INPUT_END_DATE = "ErrorStripletDates_InvalidInputEndDate"
    ERROR_STRIPLET_DATES_INVALID_MONTHLY_INPUT_DAY_OF_MONTH = "ErrorStripletDates_InvalidMonthlyInputDayOfMonth"
    ERROR_STRIPLET_DATES_INVALID_PERIOD_DEFINTION = "ErrorStripletDates_InvalidPeriodDefintion"
    ERROR_STRIPLET_DATES_INVALID_ROLL_CONVENTION_TYPE = "ErrorStripletDates_InvalidRollConventionType"
    ERROR_VOL_SURF_FILTERING_DYNAMIC_FILTERING = "ErrorVolSurfFiltering_DynamicFiltering"
    ERROR_VOL_SURF_FILTERING_NO_DATA = "ErrorVolSurfFiltering_NoData"
    ERROR_VOL_SURF_FILTERING_NOT_EFFICIENT_FILTERS = "ErrorVolSurfFiltering_NotEfficientFilters"
    ERROR_VOL_SURF_FILTERING_STATIC_FILTERING = "ErrorVolSurfFiltering_StaticFiltering"
    ERROR_VOL_SURF_INPUT_INCORENT_INPUT_CONSTITUENTS = "ErrorVolSurfInput_IncorentInputConstituents"
    ERROR_VOL_SURF_INPUT_INCORRECT_INPUT_INTRUMENT_CODE_FORMAT = "ErrorVolSurfInput_IncorrectInputIntrumentCodeFormat"
    ERROR_WRONG_INPUT_FREQUENCY_NOT_SUPPORTED = "ErrorWrongInput_FrequencyNotSupported"
    ERROR_GEN_SEC_ANALYSIS_ERROR = "Error_GenSec_Analysis_Error"
    ERROR_HRA_INSUFFICIENT_DATA = "Error_HraInsufficientData"
    ERROR_IMPLIED_DISTRIBUTION_NO_SURFACE_RETURNED = "Error_ImpliedDistribution_No_Surface_Returned"
    ERROR_INVALID_INPUT_ANALYSIS_DIRECTION = "Error_InvalidInput_AnalysisDirection"
    ERROR_INVALID_INPUT_CROSS_CURRENCY_EMPTY = "Error_InvalidInput_CrossCurrencyEmpty"
    ERROR_INVALID_INPUT_CROSS_CURRENCY_INVALID = "Error_InvalidInput_CrossCurrencyInvalid"
    ERROR_INVALID_INPUT_CURVE_PRICING_PARAMETERS = "Error_InvalidInput_CurvePricingParameters"
    ERROR_INVALID_INPUT_DATE_AND_TENOR_AND_TENORS_NULL = "Error_InvalidInput_DateAndTenorAndTenorsNull"
    ERROR_INVALID_INPUT_DATE_AND_TENOR_CONFLICT = "Error_InvalidInput_DateAndTenorConflict"
    ERROR_INVALID_INPUT_DELTA_NO_SIGMA = "Error_InvalidInput_DeltaNoSigma"
    ERROR_INVALID_INPUT_EMPTY_CALENDAR_COUNT_PERIOD = "Error_InvalidInput_EmptyCalendarCountPeriod"
    ERROR_INVALID_INPUT_EMPTY_EXPIRY_AXIS = "Error_InvalidInput_EmptyExpiryAxis"
    ERROR_INVALID_INPUT_EMPTY_PRICING_ITEM = "Error_InvalidInput_EmptyPricingItem"
    ERROR_INVALID_INPUT_EMPTY_SURFACE_DEFINITION = "Error_InvalidInput_EmptySurfaceDefinition"
    ERROR_INVALID_INPUT_EMPTY_SURFACE_LAYOUT = "Error_InvalidInput_EmptySurfaceLayout"
    ERROR_INVALID_INPUT_EMPTY_SURFACE_PARAMETERS = "Error_InvalidInput_EmptySurfaceParameters"
    ERROR_INVALID_INPUT_EMPTY_UNIVERSE = "Error_InvalidInput_EmptyUniverse"
    ERROR_INVALID_INPUT_END_DATE = "Error_InvalidInput_EndDate"
    ERROR_INVALID_INPUT_END_DATE_BEFORE_VALUATION_DATE = "Error_InvalidInput_EndDateBeforeValuationDate"
    ERROR_INVALID_INPUT_IMPLIED_VOL_OVERRIDE_INCOMPATIBLE_WITH_CAPS_ON_CMS = (
        "Error_InvalidInput_ImpliedVolOverrideIncompatibleWithCapsOnCms"
    )
    ERROR_INVALID_INPUT_IMPLIED_VOL_OVERRIDE_INCOMPATIBLE_WITH_COLLARS = (
        "Error_InvalidInput_ImpliedVolOverrideIncompatibleWithCollars"
    )
    ERROR_INVALID_INPUT_INCONSISTENT_PARAMETERS = "Error_InvalidInput_InconsistentParameters"
    ERROR_INVALID_INPUT_INSTRUMENT_DEFINTION_CANT_BE_OVERRIDEN = "Error_InvalidInput_InstrumentDefintionCantBeOverriden"
    ERROR_INVALID_INPUT_INVALID_AMORTIZATION_SCHEDULE = "Error_InvalidInput_InvalidAmortizationSchedule"
    ERROR_INVALID_INPUT_INVALID_AMOUNT = "Error_InvalidInput_InvalidAmount"
    ERROR_INVALID_INPUT_INVALID_AXIS = "Error_InvalidInput_InvalidAxis"
    ERROR_INVALID_INPUT_INVALID_CALCULATION_INPUT = "Error_InvalidInput_InvalidCalculationInput"
    ERROR_INVALID_INPUT_INVALID_CALENDAR_CODE = "Error_InvalidInput_InvalidCalendarCode"
    ERROR_INVALID_INPUT_INVALID_CALENDAR_DAY_OF_MONTH = "Error_InvalidInput_InvalidCalendarDayOfMonth"
    ERROR_INVALID_INPUT_INVALID_CALENDAR_OR_CURRENCY = "Error_InvalidInput_InvalidCalendarOrCurrency"
    ERROR_INVALID_INPUT_INVALID_COMMODITY_FORWARD_CURVE_DEFINITION = (
        "Error_InvalidInput_InvalidCommodityForwardCurveDefinition"
    )
    ERROR_INVALID_INPUT_INVALID_CONVEXITY_ADJUSTMENT_INTEGRATION_METHOD = (
        "Error_InvalidInput_InvalidConvexityAdjustmentIntegrationMethod"
    )
    ERROR_INVALID_INPUT_INVALID_COUNT = "Error_InvalidInput_InvalidCount"
    ERROR_INVALID_INPUT_INVALID_CROSS_CURRENCY_SWAPS_CONSTITUENT = (
        "Error_InvalidInput_InvalidCrossCurrencySwapsConstituent"
    )
    ERROR_INVALID_INPUT_INVALID_CURRENCY_CODE = "Error_InvalidInput_InvalidCurrencyCode"
    ERROR_INVALID_INPUT_INVALID_DATE = "Error_InvalidInput_InvalidDate"
    ERROR_INVALID_INPUT_INVALID_DAY_OF_WEEK = "Error_InvalidInput_InvalidDayOfWeek"
    ERROR_INVALID_INPUT_INVALID_FIELD_VALUE = "Error_InvalidInput_InvalidFieldValue"
    ERROR_INVALID_INPUT_INVALID_FX_CROSS_CODE_CROSS_CURRENCY_SWAPS_CONSTITUENT = (
        "Error_InvalidInput_InvalidFxCrossCodeCrossCurrencySwapsConstituent"
    )
    ERROR_INVALID_INPUT_INVALID_FX_FORWARD_CURVE_DEFINITION = "Error_InvalidInput_InvalidFxForwardCurveDefinition"
    ERROR_INVALID_INPUT_INVALID_INSTRUMENT_DEFINITION = "Error_InvalidInput_InvalidInstrumentDefinition"
    ERROR_INVALID_INPUT_INVALID_INTEREST_RATE_CURVE_DEFINITION = "Error_InvalidInput_InvalidInterestRateCurveDefinition"
    ERROR_INVALID_INPUT_INVALID_INTERVAL = "Error_InvalidInput_InvalidInterval"
    ERROR_INVALID_INPUT_INVALID_JSON_PAYLOAD = "Error_InvalidInput_InvalidJsonPayload"
    ERROR_INVALID_INPUT_INVALID_LAG_AND_LOCK_OUT_VALUES = "Error_InvalidInput_InvalidLagAndLockOutValues"
    ERROR_INVALID_INPUT_INVALID_LEG_DEFINITION = "Error_InvalidInput_InvalidLegDefinition"
    ERROR_INVALID_INPUT_INVALID_MARKET_DATA_DATE = "Error_InvalidInput_InvalidMarketDataDate"
    ERROR_INVALID_INPUT_INVALID_MARKET_DATA_PARAMETERS = "Error_InvalidInput_InvalidMarketDataParameters"
    ERROR_INVALID_INPUT_INVALID_MATURITY_DATE = "Error_InvalidInput_InvalidMaturityDate"
    ERROR_INVALID_INPUT_INVALID_PARAMETERS_FOR_IMMPLIED_VOL = "Error_InvalidInput_InvalidParametersForImmpliedVol"
    ERROR_INVALID_INPUT_INVALID_PRICING_MODEL_TYPE = "Error_InvalidInput_InvalidPricingModelType"
    ERROR_INVALID_INPUT_INVALID_PRICING_PARAMETER = "Error_InvalidInput_InvalidPricingParameter"
    ERROR_INVALID_INPUT_INVALID_PRICING_TYPE = "Error_InvalidInput_InvalidPricingType"
    ERROR_INVALID_INPUT_INVALID_REPORT_CURRENCY_CODE = "Error_InvalidInput_InvalidReportCurrencyCode"
    ERROR_INVALID_INPUT_INVALID_SHIFT_MODEL = "Error_InvalidInput_InvalidShiftModel"
    ERROR_INVALID_INPUT_INVALID_SURFACE_TYPE = "Error_InvalidInput_InvalidSurfaceType"
    ERROR_INVALID_INPUT_INVALID_TENOR = "Error_InvalidInput_InvalidTenor"
    ERROR_INVALID_INPUT_INVALID_TENOR_PRIORITY = "Error_InvalidInput_InvalidTenorPriority"
    ERROR_INVALID_INPUT_INVALID_UNDERLYING_INSTRUMENT_TYPE = "Error_InvalidInput_InvalidUnderlyingInstrumentType"
    ERROR_INVALID_INPUT_INVALID_VALUATION_DATE = "Error_InvalidInput_InvalidValuationDate"
    ERROR_INVALID_INPUT_MANDATORY_FIELD_VALUE = "Error_InvalidInput_MandatoryFieldValue"
    ERROR_INVALID_INPUT_MATURITY_DATE_EXPIRED = "Error_InvalidInput_MaturityDateExpired"
    ERROR_INVALID_INPUT_MAX_MATURITY_FILTER = "Error_InvalidInput_MaxMaturityFilter"
    ERROR_INVALID_INPUT_MAX_STALENESS_DAYS_FILTER = "Error_InvalidInput_MaxStalenessDaysFilter"
    ERROR_INVALID_INPUT_MIN_MATURITY_FILTER = "Error_InvalidInput_MinMaturityFilter"
    ERROR_INVALID_INPUT_MISSING_PARAMETER = "Error_InvalidInput_MissingParameter"
    ERROR_INVALID_INPUT_MISSING_UNDERLYING_INSTRUMENT = "Error_InvalidInput_MissingUnderlyingInstrument"
    ERROR_INVALID_INPUT_MISSING_UNDERLYING_INSTRUMENT_TYPE = "Error_InvalidInput_MissingUnderlyingInstrumentType"
    ERROR_INVALID_INPUT_NO_CALCULATION_INPUT = "Error_InvalidInput_NoCalculationInput"
    ERROR_INVALID_INPUT_NO_DEFAULT_FIELDS = "Error_InvalidInput_NoDefaultFields"
    ERROR_INVALID_INPUT_NO_FIELDS = "Error_InvalidInput_NoFields"
    ERROR_INVALID_INPUT_NO_INSTRUMENT_TYPE = "Error_InvalidInput_NoInstrumentType"
    ERROR_INVALID_INPUT_NO_REQUEST = "Error_InvalidInput_NoRequest"
    ERROR_INVALID_INPUT_NO_UNDERLYING_TYPE = "Error_InvalidInput_NoUnderlyingType"
    ERROR_INVALID_INPUT_NO_UNIVERSE = "Error_InvalidInput_NoUniverse"
    ERROR_INVALID_INPUT_NO_USER_ID = "Error_InvalidInput_NoUserId"
    ERROR_INVALID_INPUT_REQUEST_ID_MISMATCH = "Error_InvalidInput_RequestIdMismatch"
    ERROR_INVALID_INPUT_RIC_NOT_SUPPORTED = "Error_InvalidInput_Ric_Not_Supported"
    ERROR_INVALID_INPUT_SAME_EXPIRY_AXIS = "Error_InvalidInput_SameExpiryAxis"
    ERROR_INVALID_INPUT_START_DATE = "Error_InvalidInput_StartDate"
    ERROR_INVALID_INPUT_START_DATE_AFTER_END_DATE = "Error_InvalidInput_StartDateAfterEndDate"
    ERROR_INVALID_INPUT_START_DATE_MATCH_END_DATE = "Error_InvalidInput_StartDateMatchEndDate"
    ERROR_INVALID_INPUT_STATIC_FILTER_PAST_CAL_DATE = "Error_InvalidInput_StaticFilter_PastCalDate"
    ERROR_INVALID_INPUT_TEMPLATE_NOT_SUPPORTED = "Error_InvalidInput_Template_Not_Supported"
    ERROR_INVALID_INPUT_TOO_MANY_INSTRUMENTS = "Error_InvalidInput_TooManyInstruments"
    ERROR_INVALID_INPUT_UNBINDABLE_JSON_PAYLOAD = "Error_InvalidInput_UnbindableJsonPayload"
    ERROR_INVALID_INPUT_UNKNOWN_FIELD = "Error_InvalidInput_UnknownField"
    ERROR_INVALID_INPUT_UNRECOGNIZED_UNDERLYING_TYPE = "Error_InvalidInput_UnrecognizedUnderlyingType"
    ERROR_INVALID_INPUT_UNSPECIFIED = "Error_InvalidInput_Unspecified"
    ERROR_INVALID_INPUT_UNSUPPORTED_INSTRUMENT_TYPE = "Error_InvalidInput_UnsupportedInstrumentType"
    ERROR_INVALID_MARKET_DATA_INPUT_CROSS_CURRENCY_CURVE_DUPLICATED_OUTRIGHTS = (
        "Error_InvalidMarketDataInput_CrossCurrencyCurve_Duplicated_Outrights"
    )
    ERROR_INVALID_MARKET_DATA_INPUT_CROSS_CURRENCY_CURVE_DUPLICATED_SWAP_POINTS = (
        "Error_InvalidMarketDataInput_CrossCurrencyCurve_Duplicated_SwapPoints"
    )
    ERROR_INVALID_MARKET_DATA_INPUT_CROSS_CURRENCY_CURVE_MANY_CURVES_DEFINED = (
        "Error_InvalidMarketDataInput_CrossCurrencyCurve_ManyCurvesDefined"
    )
    ERROR_INVALID_MARKET_DATA_INPUT_CROSS_CURRENCY_CURVE_INVALID_FX_CROSS_CODE = (
        "Error_InvalidMarketDataInput_CrossCurrencyCurve__InvalidFxCrossCode"
    )
    ERROR_INVALID_MARKET_DATA_INPUT_DEPOSIT_CURVE_EMPTY_CURRENCY = (
        "Error_InvalidMarketDataInput_DepositCurve_EmptyCurrency"
    )
    ERROR_INVALID_MARKET_DATA_INPUT_DEPOSIT_CURVE_INVALID_CURRENCY = (
        "Error_InvalidMarketDataInput_DepositCurve_InvalidCurrency"
    )
    ERROR_INVALID_MARKET_DATA_INPUT_EXCLUDED_TENORS_DEFINITION = "Error_InvalidMarketDataInput_ExcludedTenorsDefinition"
    ERROR_INVALID_MARKET_DATA_INPUT_FX_CURVE_EMPTY_FX_CROSS_CODE = (
        "Error_InvalidMarketDataInput_FxCurve_EmptyFxCrossCode"
    )
    ERROR_INVALID_MARKET_DATA_INPUT_FX_CURVE_INVALID_FX_CROSS_CODE = (
        "Error_InvalidMarketDataInput_FxCurve_InvalidFxCrossCode"
    )
    ERROR_INVALID_MARKET_DATA_INPUT_FX_CURVE_INVALID_REFERENCE_CURRENCY = (
        "Error_InvalidMarketDataInput_FxCurve_InvalidReferenceCurrency"
    )
    ERROR_INVALID_MARKET_DATA_INPUT_INTEREST_RATE_CURVE_EMPTY_CURRENCY = (
        "Error_InvalidMarketDataInput_InterestRateCurve_EmptyCurrency"
    )
    ERROR_INVALID_MARKET_DATA_INPUT_INTEREST_RATE_CURVE_INSUFFICIENT_DATA = (
        "Error_InvalidMarketDataInput_InterestRateCurve_InsufficientData"
    )
    ERROR_INVALID_MARKET_DATA_INPUT_INTEREST_RATE_CURVE_INVALID_CURRENCY = (
        "Error_InvalidMarketDataInput_InterestRateCurve_InvalidCurrency"
    )
    ERROR_INVALID_MARKET_DATA_INPUT_IR_VOLATILITY_INSUFFICIENT_DATA = (
        "Error_InvalidMarketDataInput_IrVolatility_InsufficientData"
    )
    ERROR_INVALID_MARKET_DATA_INPUT_TENORS_DEFINITION = "Error_InvalidMarketDataInput_TenorsDefinition"
    ERROR_INVALID_VOLATILITY_TYPE = "Error_Invalid_VolatilityType"
    ERROR_LIFE_CYCLE_EVENT_NO_EVENT_FOUND = "Error_LifeCycleEvent_No_Event_Found"
    ERROR_NO_UNDERLYING_PRICE = "Error_No_Underlying_Price"
    ERROR_NOT_FOUND = "Error_NotFound"
    NONE = "None"
    TECHNICAL_ERROR = "TechnicalError"
    TEST_DATA_NOT_RECORDED_ERROR = "TestDataNotRecordedError"
    TEST_DATA_SAVING_FAILED = "TestDataSavingFailed"
    WARNING_INVALID_INPUT_CUBIC_SPLINE_IS_NOT_RECOMMENDED = "Warning_InvalidInput_CubicSplineIsNotRecommended"
    WARNING_INVALID_INPUT_CURVE_POINT_WITH_NEGATIVE_OUTRIGHT = "Warning_InvalidInput_CurvePointWithNegativeOutright"
    WARNING_INVALID_INPUT_DUPLICATED_TENORS = "Warning_InvalidInput_DuplicatedTenors"
    WARNING_INVALID_INPUT_END_DATE_NOT_BUSINESS_DAY = "Warning_InvalidInput_EndDateNotBusinessDay"
    WARNING_INVALID_INPUT_FX_SPOT_NOT_EXIST = "Warning_InvalidInput_FxSpotNotExist"
    WARNING_INVALID_INPUT_FX_SPOT_ONLY_USED = "Warning_InvalidInput_FxSpotOnlyUsed"
    WARNING_INVALID_INPUT_IGNORED_CROSS_CURRENCY_SWAPS = "Warning_InvalidInput_IgnoredCrossCurrencySwaps"
    WARNING_INVALID_INPUT_IGNORED_UNCOLLATERALIZED_INSTRUMENTS = (
        "Warning_InvalidInput_IgnoredUncollateralizedInstruments"
    )
    WARNING_INVALID_INPUT_INVALID_CONSTITUENT = "Warning_InvalidInput_InvalidConstituent"
    WARNING_INVALID_INPUT_INVALID_FX_FORWARD_CONSTITUENT = "Warning_InvalidInput_InvalidFxForwardConstituent"
    WARNING_INVALID_INPUT_INVALID_STEP_DATES = "Warning_InvalidInput_InvalidStepDates"
    WARNING_INVALID_INPUT_NO_BEFORE_AFTER_TURN = "Warning_InvalidInput_NoBeforeAfterTurn"
    WARNING_INVALID_INPUT_NO_ENCAPSULATED_TURN = "Warning_InvalidInput_NoEncapsulatedTurn"
    WARNING_INVALID_INPUT_NO_OVERLAP_TURN = "Warning_InvalidInput_NoOverlapTurn"
    WARNING_INVALID_INPUT_NO_PRE_SPOT_TURN = "Warning_InvalidInput_NoPreSpotTurn"
    WARNING_INVALID_INPUT_NO_PRE_VALUATION_STEP_DATE = "Warning_InvalidInput_NoPreValuationStepDate"
    WARNING_INVALID_INPUT_PARTIAL_SWAP_POINTS = "Warning_InvalidInput_PartialSwapPoints"
    WARNING_INVALID_INPUT_START_DATE_ALREADY_EXISTS = "Warning_InvalidInput_StartDateAlreadyExists"
    WARNING_INVALID_INPUT_START_DATE_BEFORE_SPOT_DATE = "Warning_InvalidInput_StartDateBeforeSpotDate"
    WARNING_INVALID_INPUT_START_DATE_CANNOT_BE_EXTRAPOLATED = "Warning_InvalidInput_StartDateCannotBeExtrapolated"
    WARNING_INVALID_INPUT_START_DATE_EMPTY = "Warning_InvalidInput_StartDateEmpty"
    WARNING_INVALID_INPUT_START_DATE_INCLUDED_IN_STANDARD_TURN_PERIODS = (
        "Warning_InvalidInput_StartDateIncludedInStandardTurnPeriods"
    )
    WARNING_INVALID_INPUT_START_DATE_IS_THE_SAME_WITH_STANDARD_TURN_DATES = (
        "Warning_InvalidInput_StartDateIsTheSameWithStandardTurnDates"
    )
    WARNING_INVALID_INPUT_START_DATE_NOT_BUSINESS_DAY = "Warning_InvalidInput_StartDateNotBusinessDay"
    WARNING_INVALID_INPUT_STEP_DATE_BEFORE_VALUATION_DATE = "Warning_InvalidInput_StepDateBeforeValuationDate"
    WARNING_INVALID_INPUT_TURN_ADJUSTMENTS_NOT_APPLIED_TO_BOTH_LEGS = (
        "Warning_InvalidInput_TurnAdjustmentsNotAppliedToBothLegs"
    )
    WARNING_INVALID_INPUT_TURN_ADJUSTMENTS_NOT_MATCHED_CONSTITUENTS = (
        "Warning_InvalidInput_TurnAdjustmentsNotMatchedConstituents"
    )
    WARNING_INVALID_INPUT_TURN_PERIOD_EXCEEDED = "Warning_InvalidInput_TurnPeriodExceeded"
    WARNING_INVALID_INPUT_UNPROCESSED_TURN = "Warning_InvalidInput_UnprocessedTurn"


class CompoundingModeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The mode used to define how the interest rate is calculated from the reset floating rates when
    the reset frequency is higher than the interest payment frequency (e.g., daily index reset with
    quarterly interest payments).
    """

    COMPOUNDING = "Compounding"
    """The mode uses the compounded average rate from multiple fixings."""
    AVERAGE = "Average"
    """The mode uses the arithmetic average rate from multiple fixings."""
    CONSTANT = "Constant"
    """The mode uses the last published rate among multiple fixings."""
    ADJUSTED_COMPOUNDED = "AdjustedCompounded"
    """The mode uses Chinese 7-day repo fixing."""
    MEXICAN_COMPOUNDED = "MexicanCompounded"
    """The mode uses Mexican Bremse fixing."""


class CompoundingType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of CompoundingType."""

    CONTINUOUS = "Continuous"
    MONEY_MARKET = "MoneyMarket"
    COMPOUNDED = "Compounded"
    DISCOUNTED = "Discounted"


class CompoundingTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of CompoundingTypeEnum."""

    COMPOUNDED = "Compounded"
    CONTINUOUS = "Continuous"
    DISCOUNTED = "Discounted"
    MONEY_MARKET = "MoneyMarket"


class ConstituentOverrideModeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of ConstituentOverrideModeEnum."""

    MERGE_WITH_DEFINITION = "MergeWithDefinition"
    REPLACE_DEFINITION = "ReplaceDefinition"


class CouponReferenceDateEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The reference date for the interest payment date calculation."""

    PERIOD_START_DATE = "PeriodStartDate"
    """The reference date is the start date of the interest period."""
    PERIOD_END_DATE = "PeriodEndDate"
    """The reference date is the end date of the interest period."""


class CreditCurveTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of CreditCurveTypeEnum."""

    BOND_ISSUER_CURVE = "BondIssuerCurve"
    BOND_PEERS_CURVE = "BondPeersCurve"
    BOND_RATING_CURVE = "BondRatingCurve"
    BOND_SECTOR_RATING_CURVE = "BondSectorRatingCurve"
    CDSISSUER_CURVE = "CDSIssuerCurve"
    CDSPEERS_CURVE = "CDSPeersCurve"
    CDSRATING_CURVE = "CDSRatingCurve"
    CDSSECTOR_RATING_CURVE = "CDSSectorRatingCurve"


class CreditSpreadTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of CreditSpreadTypeEnum."""

    FLAT_SPREAD = "FlatSpread"
    TERM_STRUCTURE = "TermStructure"


class CurvesAndSurfacesCalibrationTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of CurvesAndSurfacesCalibrationTypeEnum."""

    ALTERNATE_CONJUGATE_GRADIENT = "AlternateConjugateGradient"
    CONJUGATE_GRADIENT = "ConjugateGradient"
    POWELL = "Powell"
    SIMPLEX_NELDER_MEAD = "SimplexNelderMead"


class CurvesAndSurfacesFxSwapCalculationMethodEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of CurvesAndSurfacesFxSwapCalculationMethodEnum."""

    DEPOSIT_CCY1_IMPLIED_FROM_FX_SWAP = "DepositCcy1ImpliedFromFxSwap"
    DEPOSIT_CCY2_IMPLIED_FROM_FX_SWAP = "DepositCcy2ImpliedFromFxSwap"
    FX_SWAP = "FxSwap"
    FX_SWAP_IMPLIED_FROM_DEPOSIT = "FxSwapImpliedFromDeposit"


class CurvesAndSurfacesInterestCalculationMethodEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of CurvesAndSurfacesInterestCalculationMethodEnum."""

    DCB_30_E_360_ISMA = "Dcb_30E_360_ISMA"
    DCB_30_360 = "Dcb_30_360"
    DCB_30_360_GERMAN = "Dcb_30_360_German"
    DCB_30_360_ISDA = "Dcb_30_360_ISDA"
    DCB_30_360_US = "Dcb_30_360_US"
    DCB_30_365_BRAZIL = "Dcb_30_365_Brazil"
    DCB_30_365_GERMAN = "Dcb_30_365_German"
    DCB_30_365_ISDA = "Dcb_30_365_ISDA"
    DCB_30_ACTUAL = "Dcb_30_Actual"
    DCB_30_ACTUAL_GERMAN = "Dcb_30_Actual_German"
    DCB_30_ACTUAL_ISDA = "Dcb_30_Actual_ISDA"
    DCB_ACTUAL_LEAP_DAY_360 = "Dcb_ActualLeapDay_360"
    DCB_ACTUAL_LEAP_DAY_365 = "Dcb_ActualLeapDay_365"
    DCB_ACTUAL_360 = "Dcb_Actual_360"
    DCB_ACTUAL_364 = "Dcb_Actual_364"
    DCB_ACTUAL_365 = "Dcb_Actual_365"
    DCB_ACTUAL_36525 = "Dcb_Actual_36525"
    DCB_ACTUAL_365_L = "Dcb_Actual_365L"
    DCB_ACTUAL_365_P = "Dcb_Actual_365P"
    DCB_ACTUAL_365_CANADIAN_CONVENTION = "Dcb_Actual_365_CanadianConvention"
    DCB_ACTUAL_ACTUAL = "Dcb_Actual_Actual"
    DCB_ACTUAL_ACTUAL_AFB = "Dcb_Actual_Actual_AFB"
    DCB_ACTUAL_ACTUAL_ISDA = "Dcb_Actual_Actual_ISDA"
    DCB_CONSTANT = "Dcb_Constant"
    DCB_WORKING_DAYS_252 = "Dcb_WorkingDays_252"


class CurvesAndSurfacesPriceSideEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of CurvesAndSurfacesPriceSideEnum."""

    ASK = "Ask"
    BID = "Bid"
    LAST = "Last"
    MID = "Mid"


class CurvesAndSurfacesQuotationModeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of CurvesAndSurfacesQuotationModeEnum."""

    CASH_CLEAN_PRICE = "CashCleanPrice"
    CASH_GROSS_PRICE = "CashGrossPrice"
    DISCOUNT = "Discount"
    DISCOUNT_MARGIN = "DiscountMargin"
    MONEY_MARKET_YIELD = "MoneyMarketYield"
    OUTRIGHT = "Outright"
    PAR_YIELD = "ParYield"
    PERCENT_CLEAN_PRICE = "PercentCleanPrice"
    PERCENT_GROSS_PRICE = "PercentGrossPrice"
    PRICE = "Price"
    SIMPLE_MARGIN = "SimpleMargin"
    SPREAD = "Spread"
    SWAP_POINT = "SwapPoint"
    SWAP_POINT_IN_ABSOLUTE_UNIT = "SwapPointInAbsoluteUnit"
    UPFRONT = "Upfront"
    YIELD = "Yield"
    ZERO_COUPON = "ZeroCoupon"


class CurvesAndSurfacesSeniorityEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of CurvesAndSurfacesSeniorityEnum."""

    JUNIOR_SECURED_OR_JUNIOR_SUBORDINATED_SECURED = "JuniorSecuredOrJuniorSubordinatedSecured"
    JUNIOR_UNSECURED_OR_JUNIOR_SUBORDINATED_UNSECURED = "JuniorUnsecuredOrJuniorSubordinatedUnsecured"
    SECURED = "Secured"
    SENIOR_NON_PREFERRED = "SeniorNonPreferred"
    SENIOR_PREFERRED = "SeniorPreferred"
    SENIOR_SECURED = "SeniorSecured"
    SENIOR_SECURED_FIRST_AND_REFUNDING_MORTGAGE = "SeniorSecuredFirstAndRefundingMortgage"
    SENIOR_SECURED_FIRST_LIEN = "SeniorSecuredFirstLien"
    SENIOR_SECURED_FIRST_MORTGAGE = "SeniorSecuredFirstMortgage"
    SENIOR_SECURED_GENERAL_AND_REFUNDING_MORTGAGE = "SeniorSecuredGeneralAndRefundingMortgage"
    SENIOR_SECURED_MORTGAGE = "SeniorSecuredMortgage"
    SENIOR_SECURED_SECOND_LIEN = "SeniorSecuredSecondLien"
    SENIOR_SECURED_SECOND_MORTGAGE = "SeniorSecuredSecondMortgage"
    SENIOR_SECURED_THIRD_MORTGAGE = "SeniorSecuredThirdMortgage"
    SENIOR_SUBORDINATED_SECURED = "SeniorSubordinatedSecured"
    SENIOR_SUBORDINATED_UNSECURED = "SeniorSubordinatedUnsecured"
    SENIOR_UNSECURED = "SeniorUnsecured"
    SUBORDINATED_SECURED = "SubordinatedSecured"
    SUBORDINATED_UNSECURED = "SubordinatedUnsecured"
    UNSECURED = "Unsecured"


class CurvesAndSurfacesStrikeTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of CurvesAndSurfacesStrikeTypeEnum."""

    ABSOLUTE_PERCENT = "AbsolutePercent"
    RELATIVE_PERCENT = "RelativePercent"


class CurvesAndSurfacesTimeStampEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of CurvesAndSurfacesTimeStampEnum."""

    CLOSE = "Close"
    DEFAULT = "Default"
    OPEN = "Open"
    SETTLE = "Settle"


class CurvesAndSurfacesUnderlyingTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of CurvesAndSurfacesUnderlyingTypeEnum."""

    CAP = "Cap"
    ETI = "Eti"
    FX = "Fx"
    SWAPTION = "Swaption"


class CurvesAndSurfacesUnitEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of CurvesAndSurfacesUnitEnum."""

    BUSINESS_CALENDAR_DAY = "BusinessCalendarDay"
    CALENDAR_DAY = "CalendarDay"
    HOUR = "Hour"


class CurvesAndSurfacesVolatilityModelEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of CurvesAndSurfacesVolatilityModelEnum."""

    CUBIC_SPLINE = "CubicSpline"
    SABR = "SABR"
    SSVI = "SSVI"
    SVI = "SVI"
    TWIN_LOGNORMAL = "TwinLognormal"


class CurveSubTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of CurveSubTypeEnum."""

    BOND_CARRY = "BondCarry"
    BREAKEVEN_INFLATION_CURVE = "BreakevenInflationCurve"
    CDSCREDIT_INDEX = "CDSCreditIndex"
    CAP_FLOOR_VOLATILITY = "CapFloorVolatility"
    CENTRAL_BANK_INTEREST_RATE_PROBABILITY = "CentralBankInterestRateProbability"
    COMMERCIAL_PAPER_BENCHMARK = "CommercialPaperBenchmark"
    CORPORATE_BOND_BENCHMARK = "CorporateBondBenchmark"
    CORPORATE_BOND_PAR = "CorporateBondPar"
    CORPORATE_BOND_SPREAD = "CorporateBondSpread"
    CORPORATE_BOND_ZERO = "CorporateBondZero"
    CORPORATE_CDS_CREDIT = "CorporateCDSCredit"
    CORPORATE_CASH_CREDIT = "CorporateCashCredit"
    CORPORATE_ISSUER = "CorporateIssuer"
    COVERED = "Covered"
    DEPOSIT = "Deposit"
    FORWARD_GOVERNMENT_BOND_ZERO = "ForwardGovernmentBondZero"
    FORWARD_GOVERNMENT_PAR = "ForwardGovernmentPar"
    FORWARD_INFLATION = "ForwardInflation"
    FORWARD_RATE_AGREEMENT_ZERO = "ForwardRateAgreementZero"
    FORWARD_STARTING_SWAP = "ForwardStartingSwap"
    GOVERNMENT_BENCHMARK = "GovernmentBenchmark"
    GOVERNMENT_BOND_BENCHMARK = "GovernmentBondBenchmark"
    GOVERNMENT_BOND_VOLATILITY = "GovernmentBondVolatility"
    GOVERNMENT_CDS_CREDIT = "GovernmentCDSCredit"
    GOVERNMENT_CASH_CREDIT = "GovernmentCashCredit"
    GOVERNMENT_STRIP_BENCHMARK = "GovernmentStripBenchmark"
    INFLATION_LINKED_BENCHMARK = "InflationLinkedBenchmark"
    INFLATION_LINKED_ZERO = "InflationLinkedZero"
    INTERBANK_OFFER_RATE = "InterbankOfferRate"
    INTEREST_RATE_SWAP = "InterestRateSwap"
    INTEREST_RATE_VOLATILITY = "InterestRateVolatility"
    MUNICIPAL_BENCHMARK = "MunicipalBenchmark"
    OVERNIGHT_INDEX_SWAP = "OvernightIndexSwap"
    OVERNIGHT_INDEX_SWAP_ZERO = "OvernightIndexSwapZero"
    SEMI_SOVEREIGN_CASH_CREDIT = "SemiSovereignCashCredit"
    SHORT_TERM_INTEREST_RATE_FUTURES_ZERO = "ShortTermInterestRateFuturesZero"
    SOLVENCY_II_CORPORATE_CREDIT_SPRD_RATING = "SolvencyIICorporateCreditSprdRating"
    SOLVENCY_II_COVERED_PFANDBRIEF_ISSUER = "SolvencyIICoveredPfandbriefIssuer"
    SOLVENCY_II_FINANCIAL_CREDIT_SPRD_RATING = "SolvencyIIFinancialCreditSprdRating"
    SOLVENCY_II_INTEREST_RATE_SWAP_YIELD = "SolvencyIIInterestRateSwapYield"
    SOLVENCY_II_LIQUIDITY_SPREAD = "SolvencyIILiquiditySpread"
    SOLVENCY_II_PFANDBRIEF_YIELD_BY_CURRENCY = "SolvencyIIPfandbriefYieldByCurrency"
    SOLVENCY_II_STRUCTURED_ABS_RATING = "SolvencyIIStructuredABSRating"
    SOLVENCY_II_STRUCTURED_MBS_RATING = "SolvencyIIStructuredMBSRating"
    SOLVENCY_II_SWAP_DERIVED_ZERO = "SolvencyIISwapDerivedZero"
    SOLVENCY_II_TREASURY_VERSUS_IRS_SPREAD = "SolvencyIITreasuryVersusIRSSpread"
    SOVEREIGN_AGENCY_BENCHMARK = "SovereignAgencyBenchmark"
    SWAP_CARRY = "SwapCarry"
    SWAP_PAR = "SwapPar"
    SWAP_ZERO = "SwapZero"
    SWAPTION_VOLATILITY = "SwaptionVolatility"
    TREASURY_SPREAD = "TreasurySpread"


class CurveTenorsFrequencyEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of CurveTenorsFrequencyEnum."""

    MONTHLY = "Monthly"
    QUARTERLY = "Quarterly"
    YEARLY = "Yearly"


class CurveTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The enum that lists the type of curves supported."""

    IR_ZC_CURVE = "IrZcCurve"
    FX_OUTRIGHT_CURVE = "FxOutrightCurve"
    DIVIDEND_CURVE = "DividendCurve"


class DateMovingConvention(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The method to adjust dates to working days."""

    MODIFIED_FOLLOWING = "ModifiedFollowing"
    """Dates are moved to the next working day unless it falls in the next month, in which case the
    PreviousBusinessDay convention is used.
    """
    NEXT_BUSINESS_DAY = "NextBusinessDay"
    """Dates are moved to the next working day."""
    PREVIOUS_BUSINESS_DAY = "PreviousBusinessDay"
    """Dates are moved to the previous working day."""
    NO_MOVING = "NoMoving"
    """Dates are not adjusted."""
    EVERY_THIRD_WEDNESDAY = "EveryThirdWednesday"
    """Dates are moved to the third Wednesday of the month, or to the next working day if the third
    Wednesday is not a working day.
    """
    BBSW_MODIFIED_FOLLOWING = "BbswModifiedFollowing"
    """Dates are moved to the next working day unless it falls in the next month, or crosses mid-month
    (15th). In such case, the PreviousBusinessDay convention is used.
    """


class DateType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Specifies how a date is defined."""

    ADJUSTABLE_DATE = "AdjustableDate"
    """The date is defined as adjustable according the BusinessDayAdjustmentDefinition."""
    RELATIVE_ADJUSTABLE_DATE = "RelativeAdjustableDate"
    """The date is defined as adjusteable according the BusinessDayAdjustmentDefinition and relative
    to a reference date and a tenor.
    """
    FUTURE_DATE = "FutureDate"
    """The date is defined as adjusteable according the BusinessDayAdjustmentDefinition and the
    FutureDateCalculationMethod
    """


class DayCountBasis(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The day count basis convention used to calculate the period between two dates."""

    DCB_30_360 = "Dcb_30_360"
    """For two dates (Y1,M1,D1) and (Y2,M2,D2) the number of days in the period is defined as:
    (D2−D1)+(M2−M1)×30+(Y2−Y1)×360. The year basis is 360 days.

    Date adjustment rules (to be applied in order):

    #. If D1 is the last day of the month, change D1 to 30.
    #. If D1=30, then D2=min(D2,30).
    """
    DCB_30_360_US = "Dcb_30_360_US"
    """For two dates (Y1,M1,D1) and (Y2,M2,D2) the number of days in the period is defined as:
    (D2−D1)+(M2−M1)×30+(Y2−Y1)×360. The year basis is 360 days.

    Date adjustment rules (to be applied in order):

    #. If D1 is the last day of the month, change D1 to 30.
    #. If D1=30 then, D2=min(D2,30).
    #. If D1 and D2 are the last day of February, then D2=30.
    """
    DCB_30_360_GERMAN = "Dcb_30_360_German"
    """For two dates (Y1,M1,D1) and (Y2,M2,D2) the number of days in the period is defined as:
    (D2−D1)+(M2−M1)×30+(Y2−Y1)×360. The year basis is 360 days.

    Date adjustment rules (to be applied in order):

    #. If D1 or D2 is 31, change it to 30.
    #. If D1 or D2 is February 29th, change it to 30.
    """
    DCB_30_360_ISDA = "Dcb_30_360_ISDA"
    """For two dates (Y1,M1,D1) and (Y2,M2,D2) the number of days in the period is defined as:
    (D2−D1)+(M2−M1)×30+(Y2−Y1)×360. The year basis is 360 days.

    Date adjustment rules (to be applied in order):

    #. D1=min(D1,30).
    #. If D1=30, then D2=min(D2,30).
    """
    DCB_30_365_ISDA = "Dcb_30_365_ISDA"
    """Similar to Dcb_30_360_ISDA convention, except that the year basis is 365 days."""
    DCB_30_365_GERMAN = "Dcb_30_365_German"
    """Similar to Dcb_30_360_German convention, except that the year basis is 365 days."""
    DCB_30_365_BRAZIL = "Dcb_30_365_Brazil"
    """Similar to Dcb_30_360_US convention, except that the year basis is 365 days."""
    DCB_30_ACTUAL_GERMAN = "Dcb_30_Actual_German"
    """Similar to Dcb_30_360_German convention, except that the year basis is the actual number of
    days in the year.
    """
    DCB_30_ACTUAL = "Dcb_30_Actual"
    """Similar to Dcb_30_360_US convention, except that the year basis is the actual number of days in
    the year.
    """
    DCB_30_ACTUAL_ISDA = "Dcb_30_Actual_ISDA"
    """Similar to Dcb_30_360_ISDA convention, except that the year basis is the actual number of days
    in the year.
    """
    DCB_30_E_360_ISMA = "Dcb_30E_360_ISMA"
    """The actual number of days in the coupon period is used.
    But it is calculated on the year basis of 360 days with twelve 30-day months (regardless of the
    date of the first day or last day of the period).
    """
    DCB_ACTUAL_360 = "Dcb_Actual_360"
    """The actual number of days in the period is used. The year basis is 360 days."""
    DCB_ACTUAL_364 = "Dcb_Actual_364"
    """The actual number of days in the period is used. The year basis is 364 days."""
    DCB_ACTUAL_365 = "Dcb_Actual_365"
    """The actual number of days in the period is used. The year basis is 365 days."""
    DCB_ACTUAL_ACTUAL = "Dcb_Actual_Actual"
    """The actual number of days in the period is used. The year basis is the actual number of days in
    the year.
    """
    DCB_ACTUAL_ACTUAL_ISDA = "Dcb_Actual_Actual_ISDA"
    """Similar to Dcb_Actual_365 convention, except that on a leap year the year basis is 366 days.
    The period is calculated as: the number of days in a leap year/366 + the number of days in a
    non-leap year/365.
    """
    DCB_ACTUAL_ACTUAL_AFB = "Dcb_Actual_Actual_AFB"
    """The actual number of days in the period is used. The year basis is 366 days if the calculation
    period contains February 29th, otherwise it is 365 days.
    """
    DCB_WORKING_DAYS_252 = "Dcb_WorkingDays_252"
    """The actual number of business days in the period according to a given calendar is used. The
    year basis is 252 days.
    """
    DCB_ACTUAL_365_L = "Dcb_Actual_365L"
    """The actual number of days in the period is used. The year basis is calculated as follows:
    If the coupon frequency is annual and February 29th is included in the period, the year basis
    is 366 days, otherwise it is 365 days.
    If the coupon frequency is not annual, the year basis is 366 days for each coupon period whose
    end date falls in a leap year, otherwise it is 365.
    """
    DCB_ACTUAL_365_P = "Dcb_Actual_365P"
    DCB_ACTUAL_LEAP_DAY_365 = "Dcb_ActualLeapDay_365"
    """The actual number of days in the period is used, but February 29th is ignored for a leap year
    when counting days. The year basis is 365 days."""
    DCB_ACTUAL_LEAP_DAY_360 = "Dcb_ActualLeapDay_360"
    """The actual number of days in the period is used, but February 29th is ignored for a leap year
    when counting days. The year basis is 360 days.
    """
    DCB_ACTUAL_36525 = "Dcb_Actual_36525"
    """The actual number of days in the period is used. The year basis is 365.25 days."""
    DCB_ACTUAL_365_CANADIAN_CONVENTION = "Dcb_Actual_365_CanadianConvention"
    """The actual number of days in the period is used. If it is less than one regular coupon period,
    the year basis is 365 days.
    Otherwise, the day count is defined as: 1 – days remaining in the period x Frequency / 365.
    In most cases, Canadian domestic bonds have semiannual coupons.
    """


class DayCountBasisEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of DayCountBasisEnum."""

    DCB_30_360 = "Dcb_30_360"
    DCB_30_360_US = "Dcb_30_360_US"
    DCB_30_360_GERMAN = "Dcb_30_360_German"
    DCB_30_360_ISDA = "Dcb_30_360_ISDA"
    DCB_30_365_ISDA = "Dcb_30_365_ISDA"
    DCB_30_365_GERMAN = "Dcb_30_365_German"
    DCB_30_365_BRAZIL = "Dcb_30_365_Brazil"
    DCB_30_ACTUAL_GERMAN = "Dcb_30_Actual_German"
    DCB_30_ACTUAL = "Dcb_30_Actual"
    DCB_30_ACTUAL_ISDA = "Dcb_30_Actual_ISDA"
    DCB_30_E_360_ISMA = "Dcb_30E_360_ISMA"
    DCB_ACTUAL_360 = "Dcb_Actual_360"
    DCB_ACTUAL_364 = "Dcb_Actual_364"
    DCB_ACTUAL_365 = "Dcb_Actual_365"
    DCB_ACTUAL_ACTUAL = "Dcb_Actual_Actual"
    DCB_ACTUAL_ACTUAL_ISDA = "Dcb_Actual_Actual_ISDA"
    DCB_ACTUAL_ACTUAL_AFB = "Dcb_Actual_Actual_AFB"
    DCB_WORKING_DAYS_252 = "Dcb_WorkingDays_252"
    DCB_ACTUAL_365_L = "Dcb_Actual_365L"
    DCB_ACTUAL_365_P = "Dcb_Actual_365P"
    DCB_ACTUAL_LEAP_DAY_365 = "Dcb_ActualLeapDay_365"
    DCB_ACTUAL_LEAP_DAY_360 = "Dcb_ActualLeapDay_360"
    DCB_ACTUAL_36525 = "Dcb_Actual_36525"
    DCB_ACTUAL_365_CANADIAN_CONVENTION = "Dcb_Actual_365_CanadianConvention"
    DCB_CONSTANT = "Dcb_Constant"


class Direction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """An indicator of whether the observation period falls before or after the reference point."""

    BEFORE = "Before"
    AFTER = "After"


class DirectionEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The direction of date calculation."""

    BACKWARD = "Backward"
    """The date is calculated backward."""
    FORWARD = "Forward"
    """The date is calculated forward."""


class DiscountingTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of DiscountingTypeEnum."""

    LIBOR_DISCOUNTING = "LiborDiscounting"
    OIS_DISCOUNTING = "OisDiscounting"


class DividendTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The type of the dividend."""

    DEFAULT = "Default"
    """The default value is the projected yield (an estimation of the future dividend yield) for all
    assets with dividends (stocks, indices) and the value 'None' for underlying assets without
    dividends.
    """
    NONE = "None"
    """No dividend payment."""
    DISCRETE = "Discrete"
    """A payment that is made at regular intervals, such as monthly, weekly, or annually."""
    YIELD = "Yield"
    """The ratio of annualized dividends to the price of the underlying asset."""


class DocClauseEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of DocClauseEnum."""

    CUM_RESTRUCT14 = "CumRestruct14"
    MODIFIED_RESTRUCT14 = "ModifiedRestruct14"
    MOD_MOD_RESTRUCT14 = "ModModRestruct14"
    EX_RESTRUCT14 = "ExRestruct14"
    CUM_RESTRUCT03 = "CumRestruct03"
    MODIFIED_RESTRUCT03 = "ModifiedRestruct03"
    MOD_MOD_RESTRUCT03 = "ModModRestruct03"
    EX_RESTRUCT03 = "ExRestruct03"
    NONE = "None"


class DurationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The type of holiday duration. Possible values are FullDayDuration (full days) or
    HalfDayDuration (half days).
    """

    FULL_DAY_DURATION = "FullDayDuration"
    """Full day holidays."""
    HALF_DAY_DURATION = "HalfDayDuration"
    """Half day holidays. Designed to account for the days the markets are open, but not for a full
    trading session.
    """


class EconomicSectorEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of EconomicSectorEnum."""

    ACADEMIC_AND_EDUCATIONAL_SERVICES = "AcademicAndEducationalServices"
    BASIC_MATERIALS = "BasicMaterials"
    CONSUMER_CYCLICALS = "ConsumerCyclicals"
    CONSUMER_NON_CYCLICALS = "ConsumerNonCyclicals"
    ENERGY = "Energy"
    FINANCIALS = "Financials"
    GOVERNMENT_ACTIVITY = "GovernmentActivity"
    HEALTHCARE = "Healthcare"
    INDUSTRIALS = "Industrials"
    INSTITUTIONS_ASSOCIATIONS_AND_ORGANIZATIONS = "InstitutionsAssociationsAndOrganizations"
    REAL_ESTATE = "RealEstate"
    TECHNOLOGY = "Technology"
    UTILITIES = "Utilities"


class EndDateMovingConventionEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of EndDateMovingConventionEnum."""

    MODIFIED_FOLLOWING = "ModifiedFollowing"
    NEXT_BUSINESS_DAY = "NextBusinessDay"
    PREVIOUS_BUSINESS_DAY = "PreviousBusinessDay"
    NO_MOVING = "NoMoving"
    EVERY_THIRD_WEDNESDAY = "EveryThirdWednesday"
    BBSW_MODIFIED_FOLLOWING = "BbswModifiedFollowing"


class EndOfMonthConvention(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Specifies how ends of months are managed when generating date schedules."""

    LAST = "Last"
    """Dates are set to the last working day."""
    SAME = "Same"
    """Dates are set to the same day, if possible, otherwise, they are moved to the last day. The
    adjusted date is also moved if it is a non-working day, according to the convention set by
    DateMovingConvention.
    """
    LAST28 = "Last28"
    """Dates are set to the last day of the month as with Last, but never February 29. For example, a
    semi-annual bond with this convention maturing on August 31 pays coupons on August 31 and
    February 28, even in a leap year.
    """
    SAME28 = "Same28"
    """Dates are set to the same day of the month as with Same, but never February 29."""
    SAME1 = "Same1"
    """Dates are set to the same day of the month as with Same, but payments scheduled for February 29
    are moved to March 1 in a non-leap year.
    For example, a semi-annual bond with this convention maturing on August 29 pays coupons:

    * on February 29 and August 29 in a leap year,
    * on March 1 and August 29 in a non-leap year.
    """


class ExerciseScheduleTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of ExerciseScheduleTypeEnum."""

    FIXED_LEG = "FixedLeg"
    FLOAT_LEG = "FloatLeg"
    USER_DEFINED = "UserDefined"


class ExerciseStyleEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The style of an option based on its exercise restrictions. Note that all exercise styles may
    not apply to certain types of option instruments.
    """

    EUROPEAN = "European"
    """The exercise style when the option holder has the right to exercise the option only on its
    expiration date.
    """
    AMERICAN = "American"
    """The exercise style when the option holder has the right to exercise the option on any date
    before its expiration.
    """
    BERMUDAN = "Bermudan"
    """The exercise style when the option holder has the right to exercise the option on any of
    several specified dates before its expiration.
    """


class ExtrapolationMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The extrapolation method used in the curve bootstrapping."""

    CONSTANT = "Constant"
    """The method of constant extrapolation."""
    LINEAR = "Linear"
    """The method of linear extrapolation."""


class ExtrapolationModeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of ExtrapolationModeEnum."""

    CONSTANT = "Constant"
    CONSTANT_FORWARD_RATE = "ConstantForwardRate"
    CONSTANT_RATE = "ConstantRate"
    LINEAR = "Linear"
    NONE = "None"
    ULTIMATE_FORWARD_RATE = "UltimateForwardRate"


class ExtrapolationTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of ExtrapolationTypeEnum."""

    EXTRAPOLATION_BOTH_DERIVATIVE = "ExtrapolationBothDerivative"
    EXTRAPOLATION_BOTH_FLAT = "ExtrapolationBothFlat"
    EXTRAPOLATION_LEFT_DERIVATIVE = "ExtrapolationLeftDerivative"
    EXTRAPOLATION_LEFT_FLAT = "ExtrapolationLeftFlat"
    EXTRAPOLATION_RIGHT_DERIVATIVE = "ExtrapolationRightDerivative"
    EXTRAPOLATION_RIGHT_FLAT = "ExtrapolationRightFlat"


class FinancialContractAssetClassEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of FinancialContractAssetClassEnum."""

    FOREIGN_EXCHANGE = "ForeignExchange"
    INTEREST_RATE = "InterestRate"
    EQUITY = "Equity"


class FinancialContractStubRuleEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of FinancialContractStubRuleEnum."""

    ISSUE = "Issue"
    MATURITY = "Maturity"
    SHORT_FIRST_PRO_RATA = "ShortFirstProRata"
    SHORT_FIRST_FULL = "ShortFirstFull"
    LONG_FIRST_FULL = "LongFirstFull"
    SHORT_LAST_PRO_RATA = "ShortLastProRata"


class FinancialContractYearBasisEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of FinancialContractYearBasisEnum."""

    DCB_30_360 = "Dcb_30_360"
    DCB_30_360_US = "Dcb_30_360_US"
    DCB_30_360_GERMAN = "Dcb_30_360_German"
    DCB_30_360_ISDA = "Dcb_30_360_ISDA"
    DCB_30_365_ISDA = "Dcb_30_365_ISDA"
    DCB_30_365_GERMAN = "Dcb_30_365_German"
    DCB_30_365_BRAZIL = "Dcb_30_365_Brazil"
    DCB_30_ACTUAL_GERMAN = "Dcb_30_Actual_German"
    DCB_30_ACTUAL = "Dcb_30_Actual"
    DCB_30_ACTUAL_ISDA = "Dcb_30_Actual_ISDA"
    DCB_30_E_360_ISMA = "Dcb_30E_360_ISMA"
    DCB_ACTUAL_360 = "Dcb_Actual_360"
    DCB_ACTUAL_364 = "Dcb_Actual_364"
    DCB_ACTUAL_365 = "Dcb_Actual_365"
    DCB_ACTUAL_ACTUAL = "Dcb_Actual_Actual"
    DCB_ACTUAL_ACTUAL_ISDA = "Dcb_Actual_Actual_ISDA"
    DCB_ACTUAL_ACTUAL_AFB = "Dcb_Actual_Actual_AFB"
    DCB_WORKING_DAYS_252 = "Dcb_WorkingDays_252"
    DCB_ACTUAL_365_L = "Dcb_Actual_365L"
    DCB_ACTUAL_365_P = "Dcb_Actual_365P"
    DCB_ACTUAL_LEAP_DAY_365 = "Dcb_ActualLeapDay_365"
    DCB_ACTUAL_LEAP_DAY_360 = "Dcb_ActualLeapDay_360"
    DCB_ACTUAL_36525 = "Dcb_Actual_36525"
    DCB_ACTUAL_365_CANADIAN_CONVENTION = "Dcb_Actual_365_CanadianConvention"
    DCB_CONSTANT = "Dcb_Constant"


class FormatEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of FormatEnum."""

    LIST = "List"
    MATRIX = "Matrix"
    NDIMENSIONAL_ARRAY = "NDimensionalArray"


class Frequency(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Specifies the the frequency of an event."""

    DAILY = "Daily"
    """The event happens every day."""
    WEEKLY = "Weekly"
    """The event happens every week."""
    BI_WEEKLY = "BiWeekly"
    """The event happens every other week."""
    MONTHLY = "Monthly"
    """The event happens every month."""
    QUARTERLY = "Quarterly"
    """The event happens every quarter."""
    ANUALLY = "Anually"
    """The event happens every year."""


class FrequencyEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Specifies the frequency used in period based calcualtions."""

    ANNUAL = "Annual"
    """Once per year."""
    SEMI_ANNUAL = "SemiAnnual"
    """Twice per year."""
    QUARTERLY = "Quarterly"
    """Four times per year."""
    MONTHLY = "Monthly"
    """Every month."""
    BI_MONTHLY = "BiMonthly"
    """Twice per month."""
    EVERYDAY = "Everyday"
    """Every day."""
    EVERY_WORKING_DAY = "EveryWorkingDay"
    """Every working day."""
    EVERY7_DAYS = "Every7Days"
    """Every seven days."""
    EVERY14_DAYS = "Every14Days"
    """Every 14 days."""
    EVERY28_DAYS = "Every28Days"
    """Every 28 days."""
    EVERY30_DAYS = "Every30Days"
    """Every 30 days."""
    EVERY90_DAYS = "Every90Days"
    """Every 90 days."""
    EVERY91_DAYS = "Every91Days"
    """Every 91 days."""
    EVERY92_DAYS = "Every92Days"
    """Every 92 days."""
    EVERY93_DAYS = "Every93Days"
    """Every 93 days."""
    EVERY4_MONTHS = "Every4Months"
    """Every four months."""
    EVERY180_DAYS = "Every180Days"
    """Every 180 days."""
    EVERY182_DAYS = "Every182Days"
    """Every 182 days."""
    EVERY183_DAYS = "Every183Days"
    """Every 183 days."""
    EVERY184_DAYS = "Every184Days"
    """Every 184 days."""
    EVERY364_DAYS = "Every364Days"
    """Every 364 days."""
    EVERY365_DAYS = "Every365Days"
    """Every 365 days."""
    R2 = "R2"
    """Semiannual: H1 - 182 days, H2 - 183 days."""
    R4 = "R4"
    """Quarterly: Q1 - 91 days, Q2 - 91 days, Q3 - 91 days, Q4 - 92 days."""
    ZERO = "Zero"
    """No frequency set."""
    SCHEDULED = "Scheduled"
    """No fixed interval; frequency is defined by a Schedule field."""


class FutureDateCalculationMethodEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of FutureDateCalculationMethodEnum."""

    SECOND_FRIDAY = "SecondFriday"
    """Second Friday of the delivery month"""
    THIRD_WEDNESDAY = "ThirdWednesday"
    """Third Wednesday day of the delivery month"""
    FIRST_WORKING_DAY = "FirstWorkingDay"
    """First working day of the delivery month"""
    LAST_WORKING_DAY = "LastWorkingDay"
    """Last working day of the delivery month"""
    FIRST_CALENDAR_DAY = "FirstCalendarDay"
    """First calendar day of the delivery month"""
    FIFTEENTH_CALENDAR_DAY = "FifteenthCalendarDay"
    """Fifteenth calendar day of the delivery month"""
    NZL = "NZL"
    """Specific rule for New Zealand"""


class FutureShiftMethodEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of FutureShiftMethodEnum."""

    SHIFT_PRICE = "ShiftPrice"
    SHIFT_RATE = "ShiftRate"


class FuturesQuotationMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Specifies how an interest rate future is quoted."""

    ZERO_COUPON = "ZeroCoupon"
    """As a zero coupon rate."""
    PAR_YIELD = "ParYield"
    """As  par yield."""


class FxConstituentEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The type of the instrument used as a constituent."""

    FX_SPOT = "FxSpot"
    FX_FORWARD = "FxForward"
    CURRENCY_BASIS_SWAP = "CurrencyBasisSwap"
    DEPOSIT = "Deposit"


class FxForwardCurveInterpolationMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The interpolation method used in the curve bootstrapping."""

    CUBIC_SPLINE = "CubicSpline"
    """The local cubic interpolation of discount factors."""
    CONSTANT = "Constant"
    """The method of constant interpolation."""
    LINEAR = "Linear"
    """The method of linear interpolation."""


class FxPriceSideEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of FxPriceSideEnum."""

    MID = "Mid"
    BID = "Bid"
    ASK = "Ask"
    LAST = "Last"


class FxRateTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """An enum that describes the type of the values provided in the fx curve."""

    OUTRIGHT = "Outright"
    """The fx curve values are provided as outright rates."""
    SWAPOINT = "Swapoint"
    """The fx curve values are provided as swap points."""


class IdTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of IdTypeEnum."""

    SECURITY_ID_ENTRY = "SecurityIDEntry"
    SECURITY_ID = "SecurityID"
    CUSIP = "CUSIP"
    ISIN = "ISIN"
    REGSISIN = "REGSISIN"
    SEDOL = "SEDOL"
    IDENTIFIER = "Identifier"
    CHINA_INTERBANK_CODE = "ChinaInterbankCode"
    SHANGHAI_EXCHANGE_CODE = "ShanghaiExchangeCode"
    SHENZHEN_EXCHANGE_CODE = "ShenzhenExchangeCode"
    MXTICKER_ID = "MXTickerID"


class IndexAverageMethodEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of IndexAverageMethodEnum."""

    COMPOUNDED_ACTUAL = "CompoundedActual"
    DAILY_COMPOUNDED_AVERAGE = "DailyCompoundedAverage"
    COMPOUNDED_AVERAGE_RATE = "CompoundedAverageRate"
    ARITHMETIC_AVERAGE = "ArithmeticAverage"


class IndexCompoundingMethodEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of IndexCompoundingMethodEnum."""

    COMPOUNDED = "Compounded"
    ADJUSTED_COMPOUNDED = "AdjustedCompounded"
    MEXICAN_COMPOUNDED = "MexicanCompounded"
    AVERAGE = "Average"
    CONSTANT = "Constant"


class IndexConvexityAdjustmentIntegrationMethodEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of IndexConvexityAdjustmentIntegrationMethodEnum."""

    RIEMANN_SUM = "RiemannSum"
    RUNGE_KUTTA = "RungeKutta"


class IndexConvexityAdjustmentMethodEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of IndexConvexityAdjustmentMethodEnum."""

    NONE = "None"
    BLACK_SCHOLES = "BlackScholes"
    REPLICATION = "Replication"
    LINEAR_SWAP_MODEL = "LinearSwapModel"


class IndexObservationMethodEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """(RFR) Method for determining the accrual observation period. The number of business days
    between the fixing date and the start or end date of the coupon period is determined by the
    index fixing lag.
    """

    LOOKBACK = "Lookback"
    """The method uses the interest period for both rate accrual and interest payment."""
    PERIOD_SHIFT = "PeriodShift"
    """The method uses the observation period for both rate accrual and interest payment."""
    MIXED = "Mixed"
    """The method uses the observation period for rate accrual and the interest period for interest
    payment.
    """


class IndexOrder(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The ordinal number of the day of the week in the month. For example, to specify the second
    Tuesday of the month, you would use "Second" here, and specify Tuesday elsewhere.
    """

    FIRST = "First"
    SECOND = "Second"
    THIRD = "Third"
    FOURTH = "Fourth"
    LAST = "Last"


class IndexPriceSideEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of IndexPriceSideEnum."""

    MID = "Mid"
    BID = "Bid"
    ASK = "Ask"
    LAST = "Last"


class IndexResetFrequencyEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of IndexResetFrequencyEnum."""

    ANNUAL = "Annual"
    SEMI_ANNUAL = "SemiAnnual"
    QUARTERLY = "Quarterly"
    MONTHLY = "Monthly"
    BI_MONTHLY = "BiMonthly"
    EVERYDAY = "Everyday"
    EVERY_WORKING_DAY = "EveryWorkingDay"
    EVERY7_DAYS = "Every7Days"
    EVERY14_DAYS = "Every14Days"
    EVERY28_DAYS = "Every28Days"
    EVERY30_DAYS = "Every30Days"
    EVERY91_DAYS = "Every91Days"
    EVERY182_DAYS = "Every182Days"
    EVERY364_DAYS = "Every364Days"
    EVERY365_DAYS = "Every365Days"
    EVERY90_DAYS = "Every90Days"
    EVERY92_DAYS = "Every92Days"
    EVERY93_DAYS = "Every93Days"
    EVERY180_DAYS = "Every180Days"
    EVERY183_DAYS = "Every183Days"
    EVERY184_DAYS = "Every184Days"
    EVERY4_MONTHS = "Every4Months"
    R2 = "R2"
    R4 = "R4"
    ZERO = "Zero"
    SCHEDULED = "Scheduled"


class IndexResetTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of IndexResetTypeEnum."""

    IN_ADVANCE = "InAdvance"
    IN_ARREARS = "InArrears"


class IndexSpreadCompoundingMethodEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of IndexSpreadCompoundingMethodEnum."""

    ISDA_COMPOUNDING = "IsdaCompounding"
    NO_COMPOUNDING = "NoCompounding"
    ISDA_FLAT_COMPOUNDING = "IsdaFlatCompounding"


class IndustryEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of IndustryEnum."""

    ADVANCED_MEDICAL_EQUIPMENT_AND_TECHNOLOGY = "AdvancedMedicalEquipmentAndTechnology"
    ADVERTISING_AND_MARKETING = "AdvertisingAndMarketing"
    AEROSPACE_AND_DEFENSE = "AerospaceAndDefense"
    AGRICULTURAL_CHEMICALS = "AgriculturalChemicals"
    AIRLINES = "Airlines"
    AIRPORT_OPERATORS_AND_SERVICES = "AirportOperatorsAndServices"
    ALUMINUM = "Aluminum"
    APPAREL_AND_ACCESSORIES = "ApparelAndAccessories"
    APPAREL_AND_ACCESSORIES_RETAILERS = "ApparelAndAccessoriesRetailers"
    APPLIANCES_TOOLS_AND_HOUSEWARES = "AppliancesToolsAndHousewares"
    AUTO_AND_TRUCK_MANUFACTURERS = "AutoAndTruckManufacturers"
    AUTO_TRUCK_AND_MOTORCYCLE_PARTS = "AutoTruckAndMotorcycleParts"
    AUTO_VEHICLES_PARTS_AND_SERVICE_RETAILERS = "AutoVehiclesPartsAndServiceRetailers"
    BANKS = "Banks"
    BIOTECHNOLOGY_AND_MEDICAL_RESEARCH = "BiotechnologyAndMedicalResearch"
    BLOCKCHAIN_AND_CRYPTOCURRENCY = "BlockchainAndCryptocurrency"
    BREWERS = "Brewers"
    BROADCASTING = "Broadcasting"
    BUSINESS_SUPPORT_SERVICES = "BusinessSupportServices"
    BUSINESS_SUPPORT_SUPPLIES = "BusinessSupportSupplies"
    CASINOS_AND_GAMING = "CasinosAndGaming"
    CHARITY_ORGANIZATIONS = "CharityOrganizations"
    CIVIC_AND_SOCIAL_ORGANIZATIONS = "CivicAndSocialOrganizations"
    CLOSED_END_FUNDS = "ClosedEndFunds"
    COAL = "Coal"
    COMMERCIAL_PRINTING_SERVICES = "CommercialPrintingServices"
    COMMERCIAL_REI_TS = "CommercialREITs"
    COMMODITY_CHEMICALS = "CommodityChemicals"
    COMMUNICATIONS_AND_NETWORKING = "CommunicationsAndNetworking"
    COMPUTER_AND_ELECTRONICS_RETAILERS = "ComputerAndElectronicsRetailers"
    COMPUTER_HARDWARE = "ComputerHardware"
    CONSTRUCTION_AND_ENGINEERING = "ConstructionAndEngineering"
    CONSTRUCTION_MATERIALS = "ConstructionMaterials"
    CONSTRUCTION_SUPPLIES_AND_FIXTURES = "ConstructionSuppliesAndFixtures"
    CONSUMER_GOODS_CONGLOMERATES = "ConsumerGoodsConglomerates"
    CONSUMER_LENDING = "ConsumerLending"
    CONSUMER_PUBLISHING = "ConsumerPublishing"
    CORPORATE_FINANCIAL_SERVICES = "CorporateFinancialServices"
    COURIER_POSTAL_AIR_FREIGHT_AND_LANDBASED_LOGISTICS = "CourierPostalAirFreightAndLandbasedLogistics"
    CROWD_COLLABORATION = "CrowdCollaboration"
    DEPARTMENT_STORES = "DepartmentStores"
    DISCOUNT_STORES = "DiscountStores"
    DISTILLERS_AND_WINERIES = "DistillersAndWineries"
    DIVERSIFIED_CHEMICALS = "DiversifiedChemicals"
    DIVERSIFIED_INDUSTRIAL_GOODS_WHOLESALE = "DiversifiedIndustrialGoodsWholesale"
    DIVERSIFIED_INVESTMENT_SERVICES = "DiversifiedInvestmentServices"
    DIVERSIFIED_MINING = "DiversifiedMining"
    DIVERSIFIED_REI_TS = "DiversifiedREITs"
    DRUG_RETAILERS = "DrugRetailers"
    ELECTRIC_UTILITIES = "ElectricUtilities"
    ELECTRICAL_COMPONENTS_AND_EQUIPMENT = "ElectricalComponentsAndEquipment"
    ELECTRONIC_EQUIPMENT_AND_PARTS = "ElectronicEquipmentAndParts"
    EMPLOYMENT_SERVICES = "EmploymentServices"
    ENTERTAINMENT_PRODUCTION = "EntertainmentProduction"
    ENVIRONMENTAL_ORGANIZATIONS = "EnvironmentalOrganizations"
    ENVIRONMENTAL_SERVICES_AND_EQUIPMENT = "EnvironmentalServicesAndEquipment"
    EXCHANGE_TRADED_FUNDS = "ExchangeTradedFunds"
    FINANCIAL_AND_COMMODITY_MARKET_OPERATORS_AND_SERVICE_PROVIDERS = (
        "FinancialAndCommodityMarketOperatorsAndServiceProviders"
    )
    FINANCIAL_TECHNOLOGY = "FinancialTechnology"
    FISHING_AND_FARMING = "FishingAndFarming"
    FOOD_PROCESSING = "FoodProcessing"
    FOOD_RETAIL_AND_DISTRIBUTION = "FoodRetailAndDistribution"
    FOOTWEAR = "Footwear"
    FOREST_AND_WOOD_PRODUCTS = "ForestAndWoodProducts"
    GOLD = "Gold"
    GOVERNMENT_ADMINISTRATION_ACTIVITIES = "GovernmentAdministrationActivities"
    GOVERNMENT_AND_GOVERNMENT_FINANCE = "GovernmentAndGovernmentFinance"
    GROUND_FREIGHT_AND_LOGISTICS = "GroundFreightAndLogistics"
    HEALTHCARE_FACILITIES_AND_SERVICES = "HealthcareFacilitiesAndServices"
    HEAVY_ELECTRICAL_EQUIPMENT = "HeavyElectricalEquipment"
    HEAVY_MACHINERY_AND_VEHICLES = "HeavyMachineryAndVehicles"
    HIGHWAYS_AND_RAIL_TRACKS = "HighwaysAndRailTracks"
    HOME_FURNISHINGS = "HomeFurnishings"
    HOME_FURNISHINGS_RETAILERS = "HomeFurnishingsRetailers"
    HOME_IMPROVEMENT_PRODUCTS_AND_SERVICES_RETAILERS = "HomeImprovementProductsAndServicesRetailers"
    HOMEBUILDING = "Homebuilding"
    HOTELS_MOTELS_AND_CRUISE_LINES = "HotelsMotelsAndCruiseLines"
    HOUSEHOLD_ELECTRONICS = "HouseholdElectronics"
    HOUSEHOLD_PRODUCTS = "HouseholdProducts"
    ITSERVICES_AND_CONSULTING = "ITServicesAndConsulting"
    INDEPENDENT_POWER_PRODUCERS = "IndependentPowerProducers"
    INDUSTRIAL_MACHINERY_AND_EQUIPMENT = "IndustrialMachineryAndEquipment"
    INSURANCE_FUNDS = "InsuranceFunds"
    INTEGRATED_HARDWARE_AND_SOFTWARE = "IntegratedHardwareAndSoftware"
    INTEGRATED_OIL_AND_GAS = "IntegratedOilAndGas"
    INTEGRATED_TELECOMMUNICATIONS_SERVICES = "IntegratedTelecommunicationsServices"
    INVESTMENT_BANKING_AND_BROKERAGE_SERVICES = "InvestmentBankingAndBrokerageServices"
    INVESTMENT_HOLDING_COMPANIES = "InvestmentHoldingCompanies"
    INVESTMENT_MANAGEMENT_AND_FUND_OPERATORS = "InvestmentManagementAndFundOperators"
    IRON_AND_STEEL = "IronAndSteel"
    LEGAL_AND_SAFETY_PUBLIC_SERVICES = "LegalAndSafetyPublicServices"
    LEISURE_AND_RECREATION = "LeisureAndRecreation"
    LIFE_AND_HEALTH_INSURANCE = "LifeAndHealthInsurance"
    MANAGED_HEALTHCARE = "ManagedHealthcare"
    MARINE_FREIGHT_AND_LOGISTICS = "MarineFreightAndLogistics"
    MARINE_PORT_SERVICES = "MarinePortServices"
    MEDICAL_EQUIPMENT_SUPPLIES_AND_DISTRIBUTION = "MedicalEquipmentSuppliesAndDistribution"
    MINING_SUPPORT_SERVICES_AND_EQUIPMENT = "MiningSupportServicesAndEquipment"
    MISCELLANEOUS_EDUCATIONAL_SERVICE_PROVIDERS = "MiscellaneousEducationalServiceProviders"
    MISCELLANEOUS_INFRASTRUCTURE = "MiscellaneousInfrastructure"
    MISCELLANEOUS_SPECIALTY_RETAILERS = "MiscellaneousSpecialtyRetailers"
    MULTILINE_INSURANCE_AND_BROKERS = "MultilineInsuranceAndBrokers"
    MULTILINE_UTILITIES = "MultilineUtilities"
    MUTUAL_FUNDS = "MutualFunds"
    NATIONAL_SECURITY_AND_INTERNATIONAL_AFFAIRS = "NationalSecurityAndInternationalAffairs"
    NATURAL_GAS_UTILITIES = "NaturalGasUtilities"
    NON_ALCOHOLIC_BEVERAGES = "NonAlcoholicBeverages"
    NON_GOLD_PRECIOUS_METALS_AND_MINERALS = "NonGoldPreciousMetalsAndMinerals"
    NON_PAPER_CONTAINERS_AND_PACKAGING = "NonPaperContainersAndPackaging"
    OFFICE_EQUIPMENT = "OfficeEquipment"
    OIL_AND_GAS_DRILLING = "OilAndGasDrilling"
    OIL_AND_GAS_EXPLORATION_AND_PRODUCTION = "OilAndGasExplorationAndProduction"
    OIL_AND_GAS_REFINING_AND_MARKETING = "OilAndGasRefiningAndMarketing"
    OIL_AND_GAS_TRANSPORTATION_SERVICES = "OilAndGasTransportationServices"
    OIL_RELATED_SERVICES_AND_EQUIPMENT = "OilRelatedServicesAndEquipment"
    ONLINE_SERVICES = "OnlineServices"
    PAPER_PACKAGING = "PaperPackaging"
    PAPER_PRODUCTS = "PaperProducts"
    PASSENGER_TRANSPORTATION_GROUND_AND_SEA = "PassengerTransportationGroundAndSea"
    PENSION_FUNDS = "PensionFunds"
    PERSONAL_PRODUCTS = "PersonalProducts"
    PERSONAL_SERVICES = "PersonalServices"
    PHARMACEUTICALS = "Pharmaceuticals"
    PHONES_AND_HANDHELD_DEVICES = "PhonesAndHandheldDevices"
    PROFESSIONAL_AND_BUSINESS_EDUCATION = "ProfessionalAndBusinessEducation"
    PROFESSIONAL_INFORMATION_SERVICES = "ProfessionalInformationServices"
    PROFESSIONAL_ORGANIZATIONS = "ProfessionalOrganizations"
    PROPERTY_AND_CASUALTY_INSURANCE = "PropertyAndCasualtyInsurance"
    REAL_ESTATE_RENTAL_DEVELOPMENT_AND_OPERATIONS = "RealEstateRentalDevelopmentAndOperations"
    REAL_ESTATE_SERVICES = "RealEstateServices"
    RECREATIONAL_PRODUCTS = "RecreationalProducts"
    REINSURANCE = "Reinsurance"
    RELIGIOUS_ORGANIZATIONS = "ReligiousOrganizations"
    RENEWABLE_ENERGY_EQUIPMENT_AND_SERVICES = "RenewableEnergyEquipmentAndServices"
    RENEWABLE_FUELS = "RenewableFuels"
    RESIDENTIAL_REI_TS = "ResidentialREITs"
    RESTAURANTS_AND_BARS = "RestaurantsAndBars"
    SCHOOL_COLLEGE_AND_UNIVERSITY = "SchoolCollegeAndUniversity"
    SEMICONDUCTOR_EQUIPMENT_AND_TESTING = "SemiconductorEquipmentAndTesting"
    SEMICONDUCTORS = "Semiconductors"
    SHIPBUILDING = "Shipbuilding"
    SOFTWARE = "Software"
    SPECIALIZED_REI_TS = "SpecializedREITs"
    SPECIALTY_CHEMICALS = "SpecialtyChemicals"
    SPECIALTY_MINING_AND_METALS = "SpecialtyMiningAndMetals"
    TEXTILES_AND_LEATHER_GOODS = "TextilesAndLeatherGoods"
    TIRES_AND_RUBBER_PRODUCTS = "TiresAndRubberProducts"
    TOBACCO = "Tobacco"
    TOYS_AND_CHILDREN_PRODUCTS = "ToysAndChildrenProducts"
    UKINVESTMENT_TRUSTS = "UKInvestmentTrusts"
    URANIUM = "Uranium"
    WATER_AND_RELATED_UTILITIES = "WaterAndRelatedUtilities"
    WIRELESS_TELECOMMUNICATIONS_SERVICES = "WirelessTelecommunicationsServices"


class IndustryGroupEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of IndustryGroupEnum."""

    AEROSPACE_AND_DEFENSE = "AerospaceAndDefense"
    AUTOMOBILES_AND_AUTO_PARTS = "AutomobilesAndAutoParts"
    BANKING_AND_INVESTMENT_SERVICES = "BankingAndInvestmentServices"
    BANKING_SERVICES = "BankingServices"
    BEVERAGES = "Beverages"
    BIOTECHNOLOGY_AND_MEDICAL_RESEARCH = "BiotechnologyAndMedicalResearch"
    CHEMICALS = "Chemicals"
    COAL = "Coal"
    COLLECTIVE_INVESTMENTS = "CollectiveInvestments"
    COMMUNICATIONS_AND_NETWORKING = "CommunicationsAndNetworking"
    COMPUTERS_PHONES_AND_HOUSEHOLD_ELECTRONICS = "ComputersPhonesAndHouseholdElectronics"
    CONSTRUCTION_AND_ENGINEERING = "ConstructionAndEngineering"
    CONSTRUCTION_MATERIALS = "ConstructionMaterials"
    CONSUMER_GOODS_CONGLOMERATES = "ConsumerGoodsConglomerates"
    CONTAINERS_AND_PACKAGING = "ContainersAndPackaging"
    DIVERSIFIED_INDUSTRIAL_GOODS_WHOLESALE = "DiversifiedIndustrialGoodsWholesale"
    DIVERSIFIED_RETAIL = "DiversifiedRetail"
    ELECTRIC_UTILITIES_AND_IP_PS = "ElectricUtilitiesAndIPPs"
    ELECTRONIC_EQUIPMENT_AND_PARTS = "ElectronicEquipmentAndParts"
    FINANCIAL_TECHNOLOGY_AND_INFRASTRUCTURE = "FinancialTechnologyAndInfrastructure"
    FOOD_AND_DRUG_RETAILING = "FoodAndDrugRetailing"
    FOOD_AND_TOBACCO = "FoodAndTobacco"
    FREIGHT_AND_LOGISTICS_SERVICES = "FreightAndLogisticsServices"
    GOVERNMENT_ACTIVITY = "GovernmentActivity"
    HEALTHCARE_EQUIPMENT_AND_SUPPLIES = "HealthcareEquipmentAndSupplies"
    HEALTHCARE_PROVIDERS_AND_SERVICES = "HealthcareProvidersAndServices"
    HOMEBUILDING_AND_CONSTRUCTION_SUPPLIES = "HomebuildingAndConstructionSupplies"
    HOTELS_AND_ENTERTAINMENT_SERVICES = "HotelsAndEntertainmentServices"
    HOUSEHOLD_GOODS = "HouseholdGoods"
    INSTITUTIONS_ASSOCIATIONS_AND_ORGANIZATIONS = "InstitutionsAssociationsAndOrganizations"
    INSURANCE = "Insurance"
    INTEGRATED_HARDWARE_AND_SOFTWARE = "IntegratedHardwareAndSoftware"
    INVESTMENT_BANKING_AND_INVESTMENT_SERVICES = "InvestmentBankingAndInvestmentServices"
    INVESTMENT_HOLDING_COMPANIES = "InvestmentHoldingCompanies"
    LEISURE_PRODUCTS = "LeisureProducts"
    MACHINERY_TOOLS_HEAVY_VEHICLES_TRAINS_AND_SHIPS = "MachineryToolsHeavyVehiclesTrainsAndShips"
    MEDIA_AND_PUBLISHING = "MediaAndPublishing"
    METALS_AND_MINING = "MetalsAndMining"
    MISCELLANEOUS_EDUCATIONAL_SERVICE = "MiscellaneousEducationalService"
    MULTILINE_UTILITIES = "MultilineUtilities"
    NATURAL_GAS_UTILITIES = "NaturalGasUtilities"
    OFFICE_EQUIPMENT = "OfficeEquipment"
    OIL_AND_GAS = "OilAndGas"
    OIL_AND_GAS_RELATED_EQUIPMENT_AND_SERVICES = "OilAndGasRelatedEquipmentAndServices"
    PAPER_AND_FOREST_PRODUCTS = "PaperAndForestProducts"
    PASSENGER_TRANSPORTATION_SERVICES = "PassengerTransportationServices"
    PERSONAL_AND_HOUSEHOLD_PRODUCTS_AND_SERVICES = "PersonalAndHouseholdProductsAndServices"
    PHARMACEUTICALS = "Pharmaceuticals"
    PROFESSIONAL_AND_BUSINESS_EDUCATION = "ProfessionalAndBusinessEducation"
    PROFESSIONAL_AND_COMMERCIAL_SERVICES = "ProfessionalAndCommercialServices"
    PROVIDERS = "Providers"
    REAL_ESTATE_OPERATIONS = "RealEstateOperations"
    RENEWABLE_ENERGY = "RenewableEnergy"
    RESIDENTIAL_AND_COMMERCIAL_REI_TS = "ResidentialAndCommercialREITs"
    SCHOOL_COLLEGE_AND_UNIVERSITY = "SchoolCollegeAndUniversity"
    SEMICONDUCTORS_AND_SEMICONDUCTOR_EQUIPMENT = "SemiconductorsAndSemiconductorEquipment"
    SOFTWARE_AND_IT_SERVICES = "SoftwareAndITServices"
    SPECIALTY_RETAILERS = "SpecialtyRetailers"
    TELECOMMUNICATIONS_SERVICES = "TelecommunicationsServices"
    TEXTILES_AND_APPAREL = "TextilesAndApparel"
    TRANSPORT_INFRASTRUCTURE = "TransportInfrastructure"
    URANIUM = "Uranium"
    WATER_AND_RELATED_UTILITIES = "WaterAndRelatedUtilities"


class InflationModeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of InflationModeEnum."""

    UNADJUSTED = "Unadjusted"
    ADJUSTED = "Adjusted"
    DEFAULT = "Default"


class InOrOutEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The type of a barrier option based on whether it is activated or deactivated when the
    underlying asset price reaches a certain barrier.
    """

    IN = "In"
    """The option is activated only when the underlying asset price reaches the barrier."""
    OUT = "Out"
    """The option is deactivated, when the underlying asset price reaches the barrier."""


class InputVolatilityTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of InputVolatilityTypeEnum."""

    IMPLIED = "Implied"
    LOG_NORMAL_VOLATILITY = "LogNormalVolatility"
    NORMAL_VOLATILITY = "NormalVolatility"
    QUOTED = "Quoted"
    SETTLE = "Settle"


class InstrumentTemplateTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The type of instrument represented by the template."""

    INTEREST_RATE_LEG = "InterestRateLeg"
    """An interest rate leg."""
    VANILLA_SWAP = "VanillaSwap"
    """A vanilla interest rate swap contract."""
    TENOR_BASIS_SWAP = "TenorBasisSwap"
    """A tenor basis swap contract."""
    CROSS_CURRENCY_SWAP = "CrossCurrencySwap"
    """A cross currency swap contract."""
    CURRENCY_BASIS_SWAP = "CurrencyBasisSwap"
    """A currency basis swap contract."""
    FX_SPOT = "FxSpot"
    """A FX spot contract contract."""
    FX_FORWARD = "FxForward"
    """A FX forward contract contract."""
    FX_SWAP = "FxSwap"
    """A FX swap contract contract."""
    NON_DELIVERABLE_FORWARD = "NonDeliverableForward"
    """A non-deliverable fx forward contract."""
    DEPOSIT = "Deposit"
    """An interest rate deposit contract."""
    FORWARD_RATE_AGREEMENT = "ForwardRateAgreement"
    """A foward rate agreement contract."""
    MONEY_MARKET_FUTURE = "MoneyMarketFuture"
    """A future contract on short term interest rate."""
    VANILLA_OTC_OPTION = "VanillaOtcOption"
    """Vanilla OTC Option contract."""
    ASIAN_OTC_OPTION = "AsianOtcOption"
    """Asian OTC Option contract."""
    SINGLE_BARRIER_OTC_OPTION = "SingleBarrierOtcOption"
    """Single Barrier OTC Option contract."""
    DOUBLE_BARRIER_OTC_OPTION = "DoubleBarrierOtcOption"
    """Double Barrier OTC Option contract."""
    SINGLE_BINARY_OTC_OPTION = "SingleBinaryOtcOption"
    """Single Binary OTC Option contract."""
    DOUBLE_BINARY_OTC_OPTION = "DoubleBinaryOtcOption"
    """Double Binary OTC Option contract."""


class InstrumentTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of InstrumentTypeEnum."""

    BOND = "Bond"
    BOND_FUTURES = "BondFutures"
    CALENDAR_SPREAD = "CalendarSpread"
    CREDIT_DEFAULT_SWAP = "CreditDefaultSwap"
    CROSS_CURRENCY_SWAP = "CrossCurrencySwap"
    DEPOSIT = "Deposit"
    FRA = "Fra"
    FUTURES = "Futures"
    FX_FORWARD = "FxForward"
    FX_SPOT = "FxSpot"
    INFLATION_SWAP = "InflationSwap"
    INTER_PRODUCT_SPREAD = "InterProductSpread"
    INTEREST_RATE_SWAP = "InterestRateSwap"
    OVERNIGHT_INDEX_SWAP = "OvernightIndexSwap"
    TENOR_BASIS_SWAP = "TenorBasisSwap"


class InterestCalculationConventionEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of InterestCalculationConventionEnum."""

    NONE = "None"
    MONEY_MARKET = "MoneyMarket"
    BOND_BASIS = "BondBasis"


class InterestCalculationMethodEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of InterestCalculationMethodEnum."""

    DCB_30_360 = "Dcb_30_360"
    DCB_30_360_US = "Dcb_30_360_US"
    DCB_30_360_GERMAN = "Dcb_30_360_German"
    DCB_30_360_ISDA = "Dcb_30_360_ISDA"
    DCB_30_365_ISDA = "Dcb_30_365_ISDA"
    DCB_30_365_GERMAN = "Dcb_30_365_German"
    DCB_30_365_BRAZIL = "Dcb_30_365_Brazil"
    DCB_30_ACTUAL_GERMAN = "Dcb_30_Actual_German"
    DCB_30_ACTUAL = "Dcb_30_Actual"
    DCB_30_ACTUAL_ISDA = "Dcb_30_Actual_ISDA"
    DCB_30_E_360_ISMA = "Dcb_30E_360_ISMA"
    DCB_ACTUAL_360 = "Dcb_Actual_360"
    DCB_ACTUAL_364 = "Dcb_Actual_364"
    DCB_ACTUAL_365 = "Dcb_Actual_365"
    DCB_ACTUAL_ACTUAL = "Dcb_Actual_Actual"
    DCB_ACTUAL_ACTUAL_ISDA = "Dcb_Actual_Actual_ISDA"
    DCB_ACTUAL_ACTUAL_AFB = "Dcb_Actual_Actual_AFB"
    DCB_WORKING_DAYS_252 = "Dcb_WorkingDays_252"
    DCB_ACTUAL_365_L = "Dcb_Actual_365L"
    DCB_ACTUAL_365_P = "Dcb_Actual_365P"
    DCB_ACTUAL_LEAP_DAY_365 = "Dcb_ActualLeapDay_365"
    DCB_ACTUAL_LEAP_DAY_360 = "Dcb_ActualLeapDay_360"
    DCB_ACTUAL_36525 = "Dcb_Actual_36525"
    DCB_ACTUAL_365_CANADIAN_CONVENTION = "Dcb_Actual_365_CanadianConvention"
    DCB_CONSTANT = "Dcb_Constant"


class InterestPaymentFrequencyEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of InterestPaymentFrequencyEnum."""

    ANNUAL = "Annual"
    SEMI_ANNUAL = "SemiAnnual"
    QUARTERLY = "Quarterly"
    MONTHLY = "Monthly"
    BI_MONTHLY = "BiMonthly"
    EVERYDAY = "Everyday"
    EVERY_WORKING_DAY = "EveryWorkingDay"
    EVERY7_DAYS = "Every7Days"
    EVERY14_DAYS = "Every14Days"
    EVERY28_DAYS = "Every28Days"
    EVERY30_DAYS = "Every30Days"
    EVERY91_DAYS = "Every91Days"
    EVERY182_DAYS = "Every182Days"
    EVERY364_DAYS = "Every364Days"
    EVERY365_DAYS = "Every365Days"
    EVERY90_DAYS = "Every90Days"
    EVERY92_DAYS = "Every92Days"
    EVERY93_DAYS = "Every93Days"
    EVERY180_DAYS = "Every180Days"
    EVERY183_DAYS = "Every183Days"
    EVERY184_DAYS = "Every184Days"
    EVERY4_MONTHS = "Every4Months"
    R2 = "R2"
    R4 = "R4"
    ZERO = "Zero"
    SCHEDULED = "Scheduled"


class InterestRateCurveInterpolationMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The interpolation method used in the curve bootstrapping."""

    CUBIC_DISCOUNT = "CubicDiscount"
    """Local cubic interpolation of discount factors."""
    CUBIC_RATE = "CubicRate"
    """Local cubic interpolation of rates."""
    CUBIC_SPLINE = "CubicSpline"
    """Natural cubic spline."""
    FORWARD_MONOTONE_CONVEX = "ForwardMonotoneConvex"
    """Forward Monotone Convex interpolation."""
    LINEAR = "Linear"
    """Linear interpolation."""
    LOG = "Log"
    """Log-linear interpolation."""
    HERMITE = "Hermite"
    """Hermite (Bessel) interpolation."""
    AKIMA_METHOD = "AkimaMethod"
    """A smoother variant of the local cubic interpolation."""
    FRITSCH_BUTLAND_METHOD = "FritschButlandMethod"
    """A variant of the monotonic cubic interpolation."""
    KRUGER_METHOD = "KrugerMethod"
    """A variant of the monotonic cubic interpolation."""
    MONOTONIC_CUBIC_NATURAL_SPLINE = "MonotonicCubicNaturalSpline"
    """Monotonic natural cubic spline."""
    MONOTONIC_HERMITE_CUBIC = "MonotonicHermiteCubic"
    """Monotonic Hermite (Bessel) cubic interpolation."""
    TENSION_SPLINE = "TensionSpline"
    """Tension spline."""


class InterestRateTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The interest rate type."""

    FIXED_RATE = "FixedRate"
    """A fixed interest rate."""
    STEP_RATE = "StepRate"
    """A variable (step) interest rate schedule."""
    FLOATING_RATE = "FloatingRate"
    """A floating interest rate."""
    FLOATING_RATE_FORMULA = "FloatingRateFormula"
    """A formula of several floating rates."""


class InterestType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Specifies whether an  interest rate is fixed or linked to a floating reference."""

    FIXED = "Fixed"
    """The interest rate is fixed."""
    FLOAT = "Float"
    """The interest rate is linked to a floating reference."""


class InterestTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of InterestTypeEnum."""

    FIXED = "Fixed"
    FLOAT = "Float"
    STEPPED = "Stepped"


class InterpolationModeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of InterpolationModeEnum."""

    AKIMA_METHOD = "AkimaMethod"
    CUBIC_DISCOUNT = "CubicDiscount"
    CUBIC_RATE = "CubicRate"
    CUBIC_SPLINE = "CubicSpline"
    FORWARD_MONOTONE_CONVEX = "ForwardMonotoneConvex"
    FRITSCH_BUTLAND_METHOD = "FritschButlandMethod"
    HERMITE = "Hermite"
    KRUGER_METHOD = "KrugerMethod"
    LINEAR = "Linear"
    LOG = "Log"
    MONOTONIC_CUBIC_NATURAL_SPLINE = "MonotonicCubicNaturalSpline"
    MONOTONIC_HERMITE_CUBIC = "MonotonicHermiteCubic"
    STEP = "Step"
    TENSION_SPLINE = "TensionSpline"


class IPAAmortizationTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of IPAAmortizationTypeEnum."""

    NONE = "None"
    LINEAR = "Linear"
    ANNUITY = "Annuity"
    SCHEDULE = "Schedule"


class IPABuySellEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of IPABuySellEnum."""

    BUY = "Buy"
    SELL = "Sell"


class IPADirectionEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of IPADirectionEnum."""

    PAID = "Paid"
    RECEIVED = "Received"


class IPADividendTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of IPADividendTypeEnum."""

    NONE = "None"
    FORECAST_TABLE = "ForecastTable"
    HISTORICAL_YIELD = "HistoricalYield"
    FORECAST_YIELD = "ForecastYield"
    IMPLIED_YIELD = "ImpliedYield"
    IMPLIED_TABLE = "ImpliedTable"
    FUTURES = "Futures"


class IPAExerciseStyleEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of IPAExerciseStyleEnum."""

    EURO = "EURO"
    AMER = "AMER"
    BERM = "BERM"


class IPAIndexObservationMethodEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of IPAIndexObservationMethodEnum."""

    LOOKBACK = "Lookback"
    PERIOD_SHIFT = "PeriodShift"
    MIXED = "Mixed"


class IPAVolatilityTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of IPAVolatilityTypeEnum."""

    FLAT = "Flat"
    TERM_STRUCTURE = "TermStructure"


class IrConstituentEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The type of interest rate instrument used as a constituent to construct the curve."""

    FLOATING_RATE_INDEX = "FloatingRateIndex"
    DEPOSIT = "Deposit"
    STIR_FUTURE = "StirFuture"
    FORWARD_RATE_AGREEMENT = "ForwardRateAgreement"
    INTEREST_RATE_SWAP = "InterestRateSwap"
    OVERNIGHT_INDEX_SWAP = "OvernightIndexSwap"
    TENOR_BASIS_SWAP = "TenorBasisSwap"


class IslamicProductCategoryEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of IslamicProductCategoryEnum."""

    MUDARABAH = "Mudarabah"
    MURABAHA = "Murabaha"
    WAKALA = "Wakala"


class IssuerTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of IssuerTypeEnum."""

    AGENCY = "Agency"
    CORPORATE = "Corporate"
    MUNIS = "Munis"
    NON_FINANCIALS = "NonFinancials"
    SOVEREIGN = "Sovereign"
    SUPRANATIONAL = "Supranational"


class MainConstituentAssetClassEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of MainConstituentAssetClassEnum."""

    BOND = "Bond"
    CREDIT_DEFAULT_SWAP = "CreditDefaultSwap"
    DEPOSIT = "Deposit"
    FUTURES = "Futures"
    FX_FORWARD = "FxForward"
    SWAP = "Swap"


class MarketDataAccessDeniedFallbackEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of MarketDataAccessDeniedFallbackEnum."""

    IGNORE_CONSTITUENTS = "IgnoreConstituents"
    RETURN_ERROR = "ReturnError"
    USE_DELAYED_DATA = "UseDelayedData"


class MarketDataLocationEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of MarketDataLocationEnum."""

    OFFSHORE = "Offshore"
    ONSHORE = "Onshore"


class MethodEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of MethodEnum."""

    MONTE_CARLO = "MonteCarlo"
    ANALYTIC = "Analytic"
    AMERICAN_MONTE_CARLO = "AmericanMonteCarlo"
    PDE = "PDE"


class ModelNameEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of ModelNameEnum."""

    BLACK_SCHOLES = "BlackScholes"
    BLACK_SCHOLES_VANNA_VOLGA = "BlackScholesVannaVolga"
    DETERMINISTIC = "Deterministic"
    DET_INTENSITY = "DetIntensity"
    DUPIRE = "Dupire"
    FORWARD = "Forward"
    GAUSSIAN = "Gaussian"
    HESTON = "Heston"
    HULL_WHITE1_FACTOR = "HullWhite1Factor"
    HULL_WHITE2_FACTOR = "HullWhite2Factor"
    LIBOR_MARKET_MODELN_FACTOR = "LiborMarketModelnFactor"
    LOG_NORMAL = "LogNormal"
    MARKET_BLACK_SCHOLES = "MarketBlackScholes"
    NORMAL = "Normal"
    STOCHASTIC_ALPHA_BETA_RHO = "StochasticAlphaBetaRho"
    ANDERSEN = "Andersen"


class ModelTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The type of the model used to determine the price of an instrument."""

    BLACK_SCHOLES_EQUITY = "BlackScholesEquity"
    """The Black-Scholes model applied to the pricing of equity options."""
    BLACK_SCHOLES_FX = "BlackScholesFx"
    """The Black-Scholes model applied to the pricing of FX options."""
    BLACK_SCHOLES_INTEREST_RATE_FUTURE = "BlackScholesInterestRateFuture"
    """The Black-Scholes model applied to the pricing of interest rate futures."""
    HESTON_EQUITY = "HestonEquity"
    """The Heston model applied to the pricing of equity options."""
    BACHELIER = "Bachelier"
    """The Bachelier model applied to the pricing of options."""


class MoneynessTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of MoneynessTypeEnum."""

    FWD = "Fwd"
    SIGMA = "Sigma"
    SPOT = "Spot"


class Month(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The month of the year. Month names written in full."""

    JANUARY = "January"
    FEBRUARY = "February"
    MARCH = "March"
    APRIL = "April"
    MAY = "May"
    JUNE = "June"
    JULY = "July"
    AUGUST = "August"
    SEPTEMBER = "September"
    OCTOBER = "October"
    NOVEMBER = "November"
    DECEMBER = "December"


class MonthEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The month of the year."""

    JANUARY = "January"
    FEBRUARY = "February"
    MARCH = "March"
    APRIL = "April"
    MAY = "May"
    JUNE = "June"
    JULY = "July"
    AUGUST = "August"
    SEPTEMBER = "September"
    OCTOBER = "October"
    NOVEMBER = "November"
    DECEMBER = "December"


class NotionalExchangeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of NotionalExchangeEnum."""

    NONE = "None"
    START = "Start"
    END = "End"
    BOTH = "Both"
    END_ADJUSTMENT = "EndAdjustment"


class NumericalMethodEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The numerical method that involves discretizing the underlying asset price and time to maturity
    to approximate the option's price through iterative calculations.
    """

    BINOMIAL_TREE = "BinomialTree"
    """The method uses a tree-like structure to model the possible price movements of the underlying
    asset over time.
    By working backward from the expiration date, the option price at each node is calculated based
    on the probabilities of the asset price moving up or down.
    """
    TRINOMIAL_TREE = "TrinomialTree"
    """The method is similar to binomial trees, but allows for three possible price movements at each
    step (up, down, or unchanged), potentially offering a more accurate representation of the asset
    price's behavior.
    """
    MONTE_CARLO = "MonteCarlo"
    """The method involves simulating a large number of possible price paths for the underlying asset,
    using random number generation to model asset price movements.
    By averaging the option payoffs across all simulated paths, an estimate of the option price can
    be obtained.
    """
    FORMULA = "Formula"
    """The method uses a formula to price options assuming steady volatility and interest rates."""
    PDE = "Pde"
    """The method is used in option pricing to solve the partial differential equations (PDEs) that
    model the evolution of option prices.
    """


class OptionModel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of OptionModel."""

    OAS = "OAS"
    OASEDUR = "OASEDUR"
    YCMARGIN = "YCMARGIN"


class OptionOwnerEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of OptionOwnerEnum."""

    SELF_ENTITY = "SelfEntity"
    COUNTERPARTY = "Counterparty"


class OptionSolvingVariableEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """name of the option property that is chosen as the variable of the the solving operation."""

    VOLATILITY = "Volatility"
    """The implied volatility of the option is used as a variable parameter."""
    STRIKE = "Strike"
    """The strike price of the option is used as a variable parameter."""


class OutputVolatilityTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of OutputVolatilityTypeEnum."""

    LOG_NORMAL_VOLATILITY = "LogNormalVolatility"
    NORMAL_VOLATILITY = "NormalVolatility"


class PaidLegEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Specifies which one of the two swap legs being defined is the paid leg."""

    FIRST_LEG = "FirstLeg"
    """The first leg is paid."""
    SECOND_LEG = "SecondLeg"
    """The second leg is paid."""


class PartyEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The parties that participate in a transaction."""

    PARTY1 = "Party1"
    PARTY2 = "Party2"


class PayerReceiverEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Specifies whether a given counterparty pays or receives the a payment."""

    PAYER = "Payer"
    """The counterparty is paying."""
    RECEIVER = "Receiver"
    """The counterparty is receiving."""


class PaymentBusinessDayConventionEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of PaymentBusinessDayConventionEnum."""

    MODIFIED_FOLLOWING = "ModifiedFollowing"
    NEXT_BUSINESS_DAY = "NextBusinessDay"
    PREVIOUS_BUSINESS_DAY = "PreviousBusinessDay"
    NO_MOVING = "NoMoving"
    EVERY_THIRD_WEDNESDAY = "EveryThirdWednesday"
    BBSW_MODIFIED_FOLLOWING = "BbswModifiedFollowing"


class PaymentRollConventionEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of PaymentRollConventionEnum."""

    LAST = "Last"
    SAME = "Same"
    SAME1 = "Same1"
    LAST28 = "Last28"
    SAME28 = "Same28"


class PaymentTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The type of a binary option based on when it is paid out."""

    IMMEDIATE = "Immediate"
    """A binary option is paid out immediately."""
    DEFERRED = "Deferred"
    """A binary option is paid out on a deferred basis."""


class PeriodicityEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of PeriodicityEnum."""

    MONTHLY = "Monthly"
    QUARTERLY = "Quarterly"


class PeriodType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The method of the period calculation."""

    WORKING_DAY = "WorkingDay"
    """Only working days are taken into account."""
    NON_WORKING_DAY = "NonWorkingDay"
    """Only non-working days are taken into account."""
    DAY = "Day"
    """All calendar days are taken into account."""
    WEEK = "Week"
    """The period is calculated in weeks."""
    MONTH = "Month"
    """The period is calculated in months."""
    QUARTER = "Quarter"
    """The period is calculated in quarters."""
    YEAR = "Year"
    """The period is calculated in years."""


class PeriodTypeOutput(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The type of the calculated period. Possible values are: Day, WorkingDay, Week, Month, Quarter
    or Year.
    """

    DAY = "Day"
    """The period is expressed in calendar days."""
    WORKING_DAY = "WorkingDay"
    """The period is expressed in working days."""
    WEEK = "Week"
    """The period is expressed in weeks."""
    MONTH = "Month"
    """The period is expressed in months."""
    QUARTER = "Quarter"
    """The period is expressed in quarters."""
    YEAR = "Year"
    """The period is expressed in years."""


class PositionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The type of regular annual holiday rule. Possible values are: AbsolutePositionWhen (for fixed
    dates), RelativePositionWhen (for a holiday that falls on a particular weekday in a month), or
    RelativeToRulePositionWhen (for a holiday that depends on the timing of another holiday).
    """

    ABSOLUTE_POSITION_WHEN = "AbsolutePositionWhen"
    """A rule to determine a fixed holiday. For example, New Year holiday on January 1."""
    RELATIVE_POSITION_WHEN = "RelativePositionWhen"
    """A rule to determine a holiday depending on the day of the week in a certain month. For example,
    Summer holiday on the last Monday of August.
    """
    RELATIVE_TO_RULE_POSITION_WHEN = "RelativeToRulePositionWhen"
    """A rule that references another rule. For example, Easter is most commonly used as a reference
    point.
    """


class PremiumSettlementTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of PremiumSettlementTypeEnum."""

    SPOT = "Spot"
    FORWARD = "Forward"
    SCHEDULE = "Schedule"


class PriceRoundingEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of PriceRoundingEnum."""

    ZERO = "Zero"
    ONE = "One"
    TWO = "Two"
    THREE = "Three"
    FOUR = "Four"
    FIVE = "Five"
    SIX = "Six"
    SEVEN = "Seven"
    EIGHT = "Eight"
    DEFAULT = "Default"
    UNROUNDED = "Unrounded"


class PriceRoundingTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of PriceRoundingTypeEnum."""

    NEAR = "Near"
    UP = "Up"
    DOWN = "Down"
    FLOOR = "Floor"
    CEIL = "Ceil"
    FACE_NEAR = "FaceNear"
    FACE_DOWN = "FaceDown"
    FACE_UP = "FaceUp"
    DEFAULT = "Default"


class PriceSide(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The price side of the instrument which comes from the instrument's quote or from the curve
    (derived from quotes) used to value the instrument.
    """

    BID = "Bid"
    """The bid side is used."""
    ASK = "Ask"
    """The ask side is used."""
    MID = "Mid"
    """The mid is used."""


class PriceSideEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of PriceSideEnum."""

    MID = "Mid"
    BID = "Bid"
    ASK = "Ask"
    LAST = "Last"


class PriceSideWithLastEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The price side of an instrument which comes from its quote or from the curve (derived from
    quotes) used to value the instrument.
    """

    BID = "Bid"
    ASK = "Ask"
    MID = "Mid"
    LAST = "Last"


class ProductEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of ProductEnum."""

    ABSPLASTIC = "ABSPlastic"
    ACETIC_ACID = "AceticAcid"
    ACETONE = "Acetone"
    ACRYLATE_ESTERS = "AcrylateEsters"
    ACRYLIC_ACID = "AcrylicAcid"
    ACRYLONITRILE = "Acrylonitrile"
    ADIPIC_ACID = "AdipicAcid"
    ALFALFA_HAY = "AlfalfaHay"
    ALFALFA_MEAL = "AlfalfaMeal"
    ALFALFA_PELLETS = "AlfalfaPellets"
    ALFALFA_SEED = "AlfalfaSeed"
    ALMONDS = "Almonds"
    ALPHA_METHYLSTYRENE = "AlphaMethylstyrene"
    ALUMINA_BAUXITE = "AluminaBauxite"
    ALUMINIUM = "Aluminium"
    AMMONIA_WATER25_PERCENT = "AmmoniaWater25Percent"
    AMMONIUM_NITRATE = "AmmoniumNitrate"
    ANHYDROUS_AMMONIA = "AnhydrousAmmonia"
    ANHYDROUS_SULFATE = "AnhydrousSulfate"
    ANTHRACENE_FRACTION = "AnthraceneFraction"
    ANTIMONY = "Antimony"
    ARABICA = "Arabica"
    ARSENIC = "Arsenic"
    ASPHALT = "Asphalt"
    ASSIGNED_AMOUNT_UNIT = "AssignedAmountUnit"
    AVOCADO_OIL = "AvocadoOil"
    BARLEY_BRAN = "BarleyBran"
    BASELOAD = "Baseload"
    BEEF = "Beef"
    BEER = "Beer"
    BEESWAX = "Beeswax"
    BENZENE = "Benzene"
    BEVERAGE_WASTE = "BeverageWaste"
    BIODIESEL = "Biodiesel"
    BIRD_SEED = "BirdSeed"
    BISMUTH = "Bismuth"
    BISPHENOL_A = "BisphenolA"
    BLACK_SEED = "BlackSeed"
    BLOCK = "Block"
    BONE_MEAL = "BoneMeal"
    BRASS = "Brass"
    BRAZIL_NUTS = "BrazilNuts"
    BRENT_CRUDES = "BrentCrudes"
    BRONZE = "Bronze"
    BUCKWHEAT = "Buckwheat"
    BUNKER_FUEL = "BunkerFuel"
    BURNING_KEROSENE = "BurningKerosene"
    BUTADIENE = "Butadiene"
    BUTADIENE_LATEXES = "ButadieneLatexes"
    BUTADIENE_NITRILE_RUBBERS = "ButadieneNitrileRubbers"
    BUTADIENE_STYRENE_LATEXES = "ButadieneStyreneLatexes"
    BUTADIENE_STYRENE_RUBBERS = "ButadieneStyreneRubbers"
    BUTANE = "Butane"
    BUTANEDIOL = "Butanediol"
    BUTTER = "Butter"
    BUTYL_ACETATE = "ButylAcetate"
    BUTYL_RUBBERS = "ButylRubbers"
    CADMIUM = "Cadmium"
    CANARY_SEED = "CanarySeed"
    CAPROLACTAM = "Caprolactam"
    CARBAMIDE_FORMALDEHYDE_RESINS = "CarbamideFormaldehydeResins"
    CASHEWS = "Cashews"
    CASSAVA = "Cassava"
    CASTOR_OIL = "CastorOil"
    CAUSTIC_SODA = "CausticSoda"
    CELLULOSIC_BIOFUELS = "CellulosicBiofuels"
    CERTIFIED_EMISSION_REDUCTION = "CertifiedEmissionReduction"
    CHEESE = "Cheese"
    CHESTNUTS = "Chestnuts"
    CHROMITE = "Chromite"
    CHROMIUM = "Chromium"
    CITRUS_PULP = "CitrusPulp"
    CLOTHING = "Clothing"
    CLOUD_COVER = "CloudCover"
    COBALT = "Cobalt"
    COCOA = "Cocoa"
    COCONUT_OIL = "CoconutOil"
    COKING_COAL = "CokingCoal"
    COLA = "Cola"
    COOLING_DEGREE_DAYS = "CoolingDegreeDays"
    COPPER = "Copper"
    COPPER_CONCENTRATES = "CopperConcentrates"
    COPPER_ORE = "CopperOre"
    COPRA = "Copra"
    COPRA_PELLETS = "CopraPellets"
    CORN_OIL = "CornOil"
    CORNFLOUR = "Cornflour"
    COSMETICS = "Cosmetics"
    COTTON = "Cotton"
    COTTON_YARN = "CottonYarn"
    COTTONSEED = "Cottonseed"
    COTTONSEED_MEAL = "CottonseedMeal"
    COTTONSEED_OIL = "CottonseedOil"
    CRAMP = "Cramp"
    CUMENE = "Cumene"
    CYCLOHEXANE = "Cyclohexane"
    DETERGENTS = "Detergents"
    DIAMMONIUM_PHOSPHATE = "DiammoniumPhosphate"
    DIAMOND = "Diamond"
    DIESEL = "Diesel"
    DIETHANOLAMINE = "Diethanolamine"
    DIETHYLENE_GLYCOL = "DiethyleneGlycol"
    DIMETHYL_TEREPHTHALATE = "DimethylTerephthalate"
    DIOCTYLPHTHALATE = "Dioctylphthalate"
    DISTILLERS_DRIED_GRAINS_WITH_SOLUBLES = "DistillersDriedGrainsWithSolubles"
    DIVINYL_RUBBERS = "DivinylRubbers"
    DRUGS = "Drugs"
    DRY_BULK_SINGLE_VOYAGE = "DryBulkSingleVoyage"
    DRY_BULK_TIME_CHARTER = "DryBulkTimeCharter"
    DUAL_PURPOSE_KEROSENE = "DualPurposeKerosene"
    DUBAI_CRUDE = "DubaiCrude"
    DYES = "Dyes"
    EDIBLE_BARLEY = "EdibleBarley"
    EDIBLE_WHEAT = "EdibleWheat"
    EGG = "Egg"
    ELECTRICAL_WIRE = "ElectricalWire"
    EMISSION_REDUCTION_UNIT = "EmissionReductionUnit"
    EMULSION_PVC = "EmulsionPVC"
    EPICHLOROHYDRIN = "Epichlorohydrin"
    EPOXY_RESINS = "EpoxyResins"
    ESSENTIAL_OILS = "EssentialOils"
    ETHANE = "Ethane"
    ETHANOL = "Ethanol"
    ETHYL_TERTIARY_BUTYL_ETHER = "EthylTertiaryButylEther"
    ETHYLBENZENE = "Ethylbenzene"
    ETHYLENE = "Ethylene"
    ETHYLENE_DICHLORIDE = "EthyleneDichloride"
    ETHYLENE_OXIDE = "EthyleneOxide"
    ETHYLENE_PROPYLENE_RUBBERS = "EthylenePropyleneRubbers"
    ETHYLENE_VINYL_ACETATE = "EthyleneVinylAcetate"
    ETHYLHEXANOL = "Ethylhexanol"
    EUROPEAN_AVIATION_ALLOWANC = "EuropeanAviationAllowanc"
    EUROPEAN_UNIT_ALLOWANCE = "EuropeanUnitAllowance"
    EXPANDABLE_POLYSTYRENE = "ExpandablePolystyrene"
    FAT_PRODUCTS = "FatProducts"
    FATTY_ACID = "FattyAcid"
    FATTY_ALCOHOLS = "FattyAlcohols"
    FEATHER_MEAL = "FeatherMeal"
    FEED_BARLEY = "FeedBarley"
    FEED_CONCENTRATE = "FeedConcentrate"
    FEED_CORN = "FeedCorn"
    FEED_WHEAT = "FeedWheat"
    FERROALLOY = "Ferroalloy"
    FERROCHROME = "Ferrochrome"
    FIBER_PRODUCTS = "FiberProducts"
    FISH = "Fish"
    FISH_MEAL = "FishMeal"
    FISH_OIL = "FishOil"
    FLAX = "Flax"
    FLOUR = "Flour"
    FROG_LEGS = "FrogLegs"
    FRUIT = "Fruit"
    FUR_SKINS = "FurSkins"
    GALLIUM = "Gallium"
    GASOLINE = "Gasoline"
    GASOLINE_COMPONENTS = "GasolineComponents"
    GELATINE = "Gelatine"
    GENERAL_PURPOSE_POLYSTYREN = "GeneralPurposePolystyren"
    GERMANIUM = "Germanium"
    GLUTEN_FEED_PELLETS = "GlutenFeedPellets"
    GLUTEN_MEAL = "GlutenMeal"
    GLYCERINE = "Glycerine"
    GLYCOL_ETHERS = "GlycolEthers"
    GOAT_MEAT = "GoatMeat"
    GOLD_BULLION = "GoldBullion"
    GOLD_COINS = "GoldCoins"
    GOLD_INGOTS = "GoldIngots"
    GREAVES = "Greaves"
    GREEN_BEANS = "GreenBeans"
    GROWING_DEGREE_DAYS = "GrowingDegreeDays"
    GUM = "Gum"
    GUNMETAL = "Gunmetal"
    HAZEL_NUTS = "HazelNuts"
    HEATING_DEGREE_DAYS = "HeatingDegreeDays"
    HEATING_OIL_GAS_OIL = "HeatingOilGasOil"
    HEAVY_PYROLYSIS_RESINS = "HeavyPyrolysisResins"
    HEMP = "Hemp"
    HEXANE = "Hexane"
    HIGH_DENSITY_POLYETHYLENE = "HighDensityPolyethylene"
    HIGH_IMPACT_POLYSTYRENE = "HighImpactPolystyrene"
    HIGH_SULPHUR_FUEL_OIL = "HighSulphurFuelOil"
    HOMINY_FEED = "HominyFeed"
    HONEY = "Honey"
    HOPS = "Hops"
    HORTICULTURE = "Horticulture"
    HYDROCHLORIC_ACID = "HydrochloricAcid"
    INDIUM = "Indium"
    IRIDIUM = "Iridium"
    IRON_ORE = "IronOre"
    ISO_BUTANOL = "IsoButanol"
    ISO_PROPANOL = "IsoPropanol"
    ISOCYANATES = "Isocyanates"
    ISOPHTHALIC_ACID = "IsophthalicAcid"
    ISOPRENE_RUBBERS = "IsopreneRubbers"
    JET_FUEL = "JetFuel"
    JUTE = "Jute"
    LAMB_MUTTON = "LambMutton"
    LARD_TALLOW = "LardTallow"
    LEAD = "Lead"
    LEAD_ORE = "LeadOre"
    LEATHER = "Leather"
    LINEAR_ALKYLBENZENE = "LinearAlkylbenzene"
    LINEAR_ALKYLBENZENE_SULPHO = "LinearAlkylbenzeneSulpho"
    LINEAR_LOW_DENSITY_POLYETH = "LinearLowDensityPolyeth"
    LINEN = "Linen"
    LINSEED_FLAXSEED = "LinseedFlaxseed"
    LINSEED_OIL = "LinseedOil"
    LIQUEFIED_NATURAL_GAS = "LiquefiedNaturalGas"
    LIQUID_PYROLYSIS_PRODUCTS = "LiquidPyrolysisProducts"
    LIVE_CATTLE = "LiveCattle"
    LIVE_PIG_HOG = "LivePigHog"
    LIVE_SHEEP_LAMB = "LiveSheepLamb"
    LOW_DENSITY_POLYETHYLENE = "LowDensityPolyethylene"
    LOW_SULPHUR_FUEL_OIL = "LowSulphurFuelOil"
    LOW_SULPHUR_WAXY_RESIDUE = "LowSulphurWaxyResidue"
    LUBRICATING_OILS = "LubricatingOils"
    MAGNESIUM = "Magnesium"
    MALEIC_ANHYDRIDE = "MaleicAnhydride"
    MALT = "Malt"
    MALTING_BARLEY = "MaltingBarley"
    MALTING_WHEAT = "MaltingWheat"
    MANGANESE = "Manganese"
    MANGANESE_ORE = "ManganeseOre"
    MEAT_EXTRACTS = "MeatExtracts"
    MEAT_MEAL = "MeatMeal"
    MELAMINE = "Melamine"
    MERCURY = "Mercury"
    METHANOL = "Methanol"
    METHYL_ETHYL_KETONE = "MethylEthylKetone"
    METHYL_ISOBUTYL_KETONE = "MethylIsobutylKetone"
    METHYL_METHACRYLATE = "MethylMethacrylate"
    METHYL_TERTIARY_BUTYL_ETHER = "MethylTertiaryButylEther"
    METHYLENE_CHLORIDE = "MethyleneChloride"
    MILK = "Milk"
    MILLET_BRAN = "MilletBran"
    MIXED_XYLENES = "MixedXylenes"
    MOLASSES = "Molasses"
    MOLYBDENUM = "Molybdenum"
    MONO_AMMONIUM_PHOSPHATE = "MonoAmmoniumPhosphate"
    MONOETHANOLAMINE = "Monoethanolamine"
    MONOETHYLENE_GLYCOL = "MonoethyleneGlycol"
    MONOPROPYLENE_GLYCOL = "MonopropyleneGlycol"
    MUSTARD = "Mustard"
    NBUTANOL = "NButanol"
    NAPHTHA = "Naphtha"
    NATURAL_GAS_LIQUIDS = "NaturalGasLiquids"
    NICKEL = "Nickel"
    NICKEL_ORE = "NickelOre"
    NITROGEN_FERTILIZERS = "NitrogenFertilizers"
    NITROGEN_PHOSPHORUS_POTASSIUM = "NitrogenPhosphorusPotassium"
    NITROUS_OXIDE = "NitrousOxide"
    NORTH_AMERICAN_SPECIAL_ALUMINIUM_ALLOY = "NorthAmericanSpecialAluminiumAlloy"
    NYLON = "Nylon"
    OXYLENE = "OXylene"
    OAT_BRAN = "OatBran"
    OFF_PEAK = "OffPeak"
    OFFAL = "Offal"
    OLIVE_OIL = "OliveOil"
    OLIVES = "Olives"
    ORANGE_JUICE = "OrangeJuice"
    OTHER_BRAN = "OtherBran"
    OTHER_CRUDES = "OtherCrudes"
    OTHER_LPG = "OtherLPG"
    OTHER_MEAT = "OtherMeat"
    OTHER_NATURAL_GAS = "OtherNaturalGas"
    OTHER_NUTS = "OtherNuts"
    OTHER_OIL_CROPS = "OtherOilCrops"
    OTHER_ROOT_CROPS = "OtherRootCrops"
    OTHER_SEED_CROPS = "OtherSeedCrops"
    PXYLENE = "PXylene"
    PALLADIUM_BULLION = "PalladiumBullion"
    PALLADIUM_COINS = "PalladiumCoins"
    PALLADIUM_INGOTS = "PalladiumIngots"
    PALM_FRUIT_OIL_BLEACHED_AND_NEUTRALIZED = "PalmFruitOilBleachedAndNeutralized"
    PALM_FRUIT_OIL_CRUDE = "PalmFruitOilCrude"
    PALM_FRUIT_OIL_OLEIN_REFINED_BLEACHED_AND_DEODORIZED = "PalmFruitOilOleinRefinedBleachedAndDeodorized"
    PALM_FRUIT_STEARIN_REFINED_BLEACHED_AND_DEODORIZED = "PalmFruitStearinRefinedBleachedAndDeodorized"
    PALM_KERNEL_MEAL = "PalmKernelMeal"
    PALM_KERNEL_OIL_CRUDE = "PalmKernelOilCrude"
    PALM_KERNEL_OIL_PROCESSE = "PalmKernelOilProcesse"
    PALM_KERNEL_PELLETS = "PalmKernelPellets"
    PALM_KERNEL_STEARIN = "PalmKernelStearin"
    PAPER = "Paper"
    PARAFFIN_WAX = "ParaffinWax"
    PASTA = "Pasta"
    PEAKLOAD = "Peakload"
    PEANUT_MEAL = "PeanutMeal"
    PEANUT_OIL = "PeanutOil"
    PEANUTS = "Peanuts"
    PEAS = "Peas"
    PET_FOOD = "PetFood"
    PETROLEUM_SOLVENTS = "PetroleumSolvents"
    PHENOL = "Phenol"
    PHOSPHATE_ROCK = "PhosphateRock"
    PHOSPHORIC_ACID = "PhosphoricAcid"
    PHTHALIC_ANHYDRIDE = "PhthalicAnhydride"
    PISTACHIOS = "Pistachios"
    PLATINUM_BULLION = "PlatinumBullion"
    PLATINUM_COINS = "PlatinumCoins"
    PLATINUM_INGOTS = "PlatinumIngots"
    POLYACETALS = "Polyacetals"
    POLYBUTYLENE_TEREPHTHALATE = "PolybutyleneTerephthalate"
    POLYCARBONATE = "Polycarbonate"
    POLYESTER = "Polyester"
    POLYETHER_POLYOLS = "PolyetherPolyols"
    POLYETHYLENE_TEREPHTHALATE = "PolyethyleneTerephthalate"
    POLYMETHYL_METHACRYLATE = "PolymethylMethacrylate"
    POLYOLS = "Polyols"
    POLYPROPYLENE_BLOCK_COPOLYMER = "PolypropyleneBlockCopolymer"
    POLYPROPYLENE_HOMOPOLYMER = "PolypropyleneHomopolymer"
    POLYPROPYLENE_RANDOM_COPOLYMER = "PolypropyleneRandomCopolymer"
    PORK = "Pork"
    POTASH = "Potash"
    POTATOES = "Potatoes"
    POULTRY = "Poultry"
    PROPANE = "Propane"
    PROPYLENE = "Propylene"
    PROPYLENE_GLYCOL_ETHERS = "PropyleneGlycolEthers"
    PROPYLENE_OXIDE = "PropyleneOxide"
    PULP = "Pulp"
    QUINOA = "Quinoa"
    RABBIT_MEAT = "RabbitMeat"
    RAPEMEAL = "Rapemeal"
    RAPESEED_CANOLA = "RapeseedCanola"
    RAPESEED_CANOLA_OIL = "RapeseedCanolaOil"
    RED_BEANS = "RedBeans"
    RENEWABLE_ENERGY_CERTIFICATE = "RenewableEnergyCertificate"
    RENEWABLE_OBLIGATION_CERTIFICATE = "RenewableObligationCertificate"
    RHODIUM = "Rhodium"
    ROBUSTA = "Robusta"
    ROUGH_RICE = "RoughRice"
    RUBBER = "Rubber"
    RUTHENIUM = "Ruthenium"
    RYE = "Rye"
    SANPLASTIC = "SANPlastic"
    SAFFLOWER = "Safflower"
    SAFFLOWER_OIL = "SafflowerOil"
    SALT = "Salt"
    SCRAP_ALUMINUM = "ScrapAluminum"
    SCRAP_COPPER = "ScrapCopper"
    SCRAP_IRON = "ScrapIron"
    SCRAP_LEAD = "ScrapLead"
    SCRAP_NICKEL = "ScrapNickel"
    SCRAP_TIN = "ScrapTin"
    SCRAP_ZINC = "ScrapZinc"
    SEED_CORN = "SeedCorn"
    SELENIUM = "Selenium"
    SESAME = "Sesame"
    SHEA_BUTTER = "SheaButter"
    SHEA_NUTS = "SheaNuts"
    SHELLFISH = "Shellfish"
    SHRIMP = "Shrimp"
    SILICON = "Silicon"
    SILK = "Silk"
    SILVER_BULLION = "SilverBullion"
    SILVER_COINS = "SilverCoins"
    SILVER_INGOTS = "SilverIngots"
    SISAL = "Sisal"
    SOAP_NOODLES = "SoapNoodles"
    SODA_ASH = "SodaAsh"
    SORBITOL = "Sorbitol"
    SORGHUM_MILO = "SorghumMilo"
    SOYBEAN = "Soybean"
    SOYBEAN_MEAL = "SoybeanMeal"
    SOYBEAN_OIL = "SoybeanOil"
    SOYBEAN_PELLETS = "SoybeanPellets"
    SPICES_HERBS = "SpicesHerbs"
    STAINLESS_STEEL = "StainlessSteel"
    STEEL = "Steel"
    STRAIGHT_RUN_FUEL_OIL = "StraightRunFuelOil"
    STYRENE = "Styrene"
    SUGAR_BEET_PULP = "SugarBeetPulp"
    SUGAR_CANE = "SugarCane"
    SULFURIC_ACID = "SulfuricAcid"
    SULPHUR = "Sulphur"
    SULPHUR_DIOXIDE = "SulphurDioxide"
    SUNFLOWER = "Sunflower"
    SUNFLOWER_OIL = "SunflowerOil"
    SUNFLOWER_SEED_MEAL = "SunflowerSeedMeal"
    SUSPENSION_PVC = "SuspensionPVC"
    SWEET_POTATOES = "SweetPotatoes"
    SYNTHETIC_SWEET_CRUDE = "SyntheticSweetCrude"
    TALL_OIL = "TallOil"
    TANKER_CLEAN_SINGLE_VOYAGE = "TankerCleanSingleVoyage"
    TANKER_CLEAN_TIME_CHARTER = "TankerCleanTimeCharter"
    TANKER_DIRTY_SINGLE_VOYAGE = "TankerDirtySingleVoyage"
    TANKER_DIRTY_TIME_CHARTER = "TankerDirtyTimeCharter"
    TANTALITE = "Tantalite"
    TAPIOCA_MEAL = "TapiocaMeal"
    TEA = "Tea"
    TEREPHTHALIC_ACID = "TerephthalicAcid"
    THERMAL_COAL = "ThermalCoal"
    TIMBER_LUMBER = "TimberLumber"
    TIN = "Tin"
    TIN_ORE = "TinOre"
    TITANIUM = "Titanium"
    TITANIUM_DIOXIDE = "TitaniumDioxide"
    TOBACCO = "Tobacco"
    TOLUENE = "Toluene"
    TRIETHANOLAMINE = "Triethanolamine"
    TRIETHYLENE_GLYCOL = "TriethyleneGlycol"
    TRIPLE_SIMPLE_PHOSPHATE = "TripleSimplePhosphate"
    TRITICALE = "Triticale"
    TUNG_OIL = "TungOil"
    TUNGSTATE = "Tungstate"
    TUNGSTEN = "Tungsten"
    USLIGHT_SWEET_CRUDES = "USLightSweetCrudes"
    URANIUM = "Uranium"
    UREA = "Urea"
    UREA_AMMONIUM_NITRATE = "UreaAmmoniumNitrate"
    VANADIUM = "Vanadium"
    VEAL = "Veal"
    VEGETABLE_OIL = "VegetableOil"
    VINYL_ACETATE = "VinylAcetate"
    VINYL_CHLORIDE_MONOMER = "VinylChlorideMonomer"
    VOLUNTARY_CARBON_UNIT = "VoluntaryCarbonUnit"
    VOLUNTARY_EMISSION_REDUCTION = "VoluntaryEmissionReduction"
    WALNUTS = "Walnuts"
    WHEAT_BRAN = "WheatBran"
    WHEAT_FLOUR = "WheatFlour"
    WHEAT_STARCH = "WheatStarch"
    WHEY = "Whey"
    WHITE_CERTIFICATE = "WhiteCertificate"
    WHITE_SPIRIT = "WhiteSpirit"
    WINE = "Wine"
    WOLFRAMITE = "Wolframite"
    WOOD_PRODUCTS = "WoodProducts"
    WOODY_BIOMASS = "WoodyBiomass"
    WOOL = "Wool"
    YOGHURT = "Yoghurt"
    ZINC = "Zinc"
    ZINC_ORE = "ZincOre"


class ProductTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of ProductTypeEnum."""

    CAP = "Cap"
    SWAPTION = "Swaption"


class ProjectedIndexCalculationMethodEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of ProjectedIndexCalculationMethodEnum."""

    CONSTANT_INDEX = "ConstantIndex"
    FORWARD_INDEX = "ForwardIndex"
    CONSTANT_COUPON_PAYMENT = "ConstantCouponPayment"


class QuotationModeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of QuotationModeEnum."""

    UNKNOWN = "Unknown"
    CASH_CLEAN_PRICE = "CashCleanPrice"
    CASH_GROSS_PRICE = "CashGrossPrice"
    PERCENT_CLEAN_PRICE = "PercentCleanPrice"
    PERCENT_GROSS_PRICE = "PercentGrossPrice"
    YIELD = "Yield"
    MONEY_MARKET_YIELD = "MoneyMarketYield"
    DISCOUNT = "Discount"
    SPREAD = "Spread"
    SIMPLE_MARGIN = "SimpleMargin"
    DISCOUNT_MARGIN = "DiscountMargin"


class QuoteFallbackLogicEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of QuoteFallbackLogicEnum."""

    NONE = "None"
    BEST_FIELD = "BestField"


class RatingEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of RatingEnum."""

    A = "A"
    A1 = "A1"
    A2 = "A2"
    A3 = "A3"
    AA = "AA"
    AAA = "AAA"
    AAHIGH = "AAHigh"
    AALOW = "AALow"
    AAMINUS = "AAMinus"
    AAPLUS = "AAPlus"
    AHIGH = "AHigh"
    ALOW = "ALow"
    AMINUS = "AMinus"
    APLUS = "APlus"
    AA1 = "Aa1"
    AA2 = "Aa2"
    AA3 = "Aa3"
    AAA_MOODYS = "Aaa"
    B = "B"
    B1 = "B1"
    B2 = "B2"
    B3 = "B3"
    BB = "BB"
    BBB = "BBB"
    BBBHIGH = "BBBHigh"
    BBBLOW = "BBBLow"
    BBBMINUS = "BBBMinus"
    BBBPLUS = "BBBPlus"
    BBHIGH = "BBHigh"
    BBLOW = "BBLow"
    BBMINUS = "BBMinus"
    BBPLUS = "BBPlus"
    BHIGH = "BHigh"
    BLOW = "BLow"
    BMINUS = "BMinus"
    BPLUS = "BPlus"
    BA1 = "Ba1"
    BA2 = "Ba2"
    BA3 = "Ba3"
    BAA1 = "Baa1"
    BAA2 = "Baa2"
    BAA3 = "Baa3"
    C = "C"
    CC = "CC"
    CCC = "CCC"
    CCCHIGH = "CCCHigh"
    CCCLOW = "CCCLow"
    CCCMINUS = "CCCMinus"
    CCCPLUS = "CCCPlus"
    CCHIGH = "CCHigh"
    CCLOW = "CCLow"
    CHIGH = "CHigh"
    CLOW = "CLow"
    CA = "Ca"
    CAA1 = "Caa1"
    CAA2 = "Caa2"
    CAA3 = "Caa3"
    D = "D"
    DD = "DD"
    DDD = "DDD"
    F1 = "F1"
    F1_PLUS = "F1Plus"
    F2 = "F2"
    F3 = "F3"


class RatingScaleSourceEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of RatingScaleSourceEnum."""

    DBRS = "DBRS"
    FITCH = "Fitch"
    MOODYS = "Moodys"
    REFINITIV = "Refinitiv"
    SAND_P = "SAndP"


class RedemptionDateTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of RedemptionDateTypeEnum."""

    REDEMPTION_AT_MATURITY_DATE = "RedemptionAtMaturityDate"
    REDEMPTION_AT_CALL_DATE = "RedemptionAtCallDate"
    REDEMPTION_AT_PUT_DATE = "RedemptionAtPutDate"
    REDEMPTION_AT_WORST_DATE = "RedemptionAtWorstDate"
    REDEMPTION_AT_BEST_DATE = "RedemptionAtBestDate"
    REDEMPTION_AT_SINK_DATE = "RedemptionAtSinkDate"
    REDEMPTION_AT_PAR_DATE = "RedemptionAtParDate"
    REDEMPTION_AT_PREMIUM_DATE = "RedemptionAtPremiumDate"
    REDEMPTION_AT_PERPETUITY = "RedemptionAtPerpetuity"
    REDEMPTION_AT_CUSTOM_DATE = "RedemptionAtCustomDate"
    REDEMPTION_AT_MAKE_WHOLE_CALL_DATE = "RedemptionAtMakeWholeCallDate"
    REDEMPTION_AT_AVERAGE_LIFE = "RedemptionAtAverageLife"
    REDEMPTION_AT_PARTIAL_CALL_DATE = "RedemptionAtPartialCallDate"
    REDEMPTION_AT_PARTIAL_PUT_DATE = "RedemptionAtPartialPutDate"
    REDEMPTION_AT_NEXT_DATE = "RedemptionAtNextDate"
    NATIVE_REDEMPTION_DATE = "NativeRedemptionDate"


class ReferenceDate(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Specifies the reference date when computing a date from a tenor."""

    SPOT_DATE = "SpotDate"
    """The market spot date is the reference date."""
    START_DATE = "StartDate"
    """The start date of the schedule is the reference date."""
    VALUATION_DATE = "ValuationDate"
    """The valuation date is the reference date."""
    END_DATE = "EndDate"
    """The contract end date is the reference date."""


class ReferenceEntityTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of ReferenceEntityTypeEnum."""

    BOND_ISIN = "BondIsin"
    BOND_RIC = "BondRic"
    CHAIN_RIC = "ChainRic"
    ORGANISATION_ID = "OrganisationId"
    TICKER = "Ticker"


class RepoCurveTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of RepoCurveTypeEnum."""

    REPO_CURVE = "RepoCurve"
    DEPOSIT_CURVE = "DepositCurve"
    LIBOR_FIXING = "LiborFixing"


class RepoRateFrequencyEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of RepoRateFrequencyEnum."""

    ANNUAL = "Annual"
    SEMI_ANNUAL = "SemiAnnual"
    QUARTERLY = "Quarterly"
    MONTHLY = "Monthly"


class RepoRateTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of RepoRateTypeEnum."""

    MONEY_MARKET = "MoneyMarket"
    ACTUAL = "Actual"
    CONTINUOUS = "Continuous"
    DISCOUNT = "Discount"
    COMPOUNDED = "Compounded"
    SIMPLE_JAPANESE = "SimpleJapanese"
    COMPOUNDED_JAPANESE = "CompoundedJapanese"


class RescheduleType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The type of rescheduling for the observation period."""

    LAG_DAYS_RESCHEDULE_DESCRIPTION = "LagDaysRescheduleDescription"
    """The rule for rescheduling a holiday using day lags. For example, if a holiday falls on Sunday,
    it is rescheduled by the number of days defined by the lag.
    """
    RELATIVE_RESCHEDULE_DESCRIPTION = "RelativeRescheduleDescription"
    """The rule for rescheduling a holiday to a specific day. For example, if a holiday falls on
    Sunday, it is rescheduled to the first Monday after the holiday.
    """


class ResourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Resource type."""

    CALENDAR = "Calendar"
    FLOATING_RATE_INDEX_DEFINITION = "FloatingRateIndexDefinition"
    INTEREST_RATE_CURVE = "InterestRateCurve"
    FX_FORWARD_CURVE = "FxForwardCurve"
    ANALYTICS = "Analytics"
    LOAN = "Loan"
    FX_SPOT = "FxSpot"
    FX_FORWARD = "FxForward"
    NON_DELIVERABLE_FORWARD = "NonDeliverableForward"
    DEPOSIT = "Deposit"
    SPACE = "Space"
    IR_SWAP = "IrSwap"
    IR_LEG = "IrLeg"
    FLOATING_RATE_INDEX = "FloatingRateIndex"
    INSTRUMENT = "Instrument"
    INSTRUMENT_TEMPLATE = "InstrumentTemplate"
    FORWARD_RATE_AGREEMENT = "ForwardRateAgreement"
    OPTION = "Option"
    FINANCIAL_MODEL = "FinancialModel"
    EQ_VOL_SURFACE = "EqVolSurface"
    FX_VOL_SURFACE = "FxVolSurface"
    CMDTY_VOL_SURFACE = "CmdtyVolSurface"
    IR_CAP_VOL_SURFACE = "IrCapVolSurface"
    IR_SWAPTION_VOL_CUBE = "IrSwaptionVolCube"


class RiskTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of RiskTypeEnum."""

    CREDIT = "Credit"
    CROSS_CURRENCY = "CrossCurrency"
    INFLATION = "Inflation"
    INTEREST_RATE = "InterestRate"


class RoundingModeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The direction of the rounding."""

    CEILING = "Ceiling"
    """The number is rounded to the minimum of the closest value and the ceiling."""
    DOWN = "Down"
    """The number is truncated."""
    FLOOR = "Floor"
    """The number is rounded to the maximum of the closest value and the floor."""
    NEAR = "Near"
    """The number is rounded to the closest value."""
    UP = "Up"
    """The number is truncated and 1 is added to the previous decimal value."""


class SectorEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of SectorEnum."""

    AGRICULTURE = "Agriculture"
    ENERGY = "Energy"
    METALS = "Metals"
    OTHER = "Other"
    TRANSPORTATION = "Transportation"
    WEATHER = "Weather"


class SeniorityEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of SeniorityEnum."""

    SECURED = "Secured"
    SENIOR_UNSECURED = "SeniorUnsecured"
    SUBORDINATED = "Subordinated"
    JUNIOR_SUBORDINATED = "JuniorSubordinated"
    PREFERENCE = "Preference"
    NONE = "None"


class SettlementType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Specifies whether a payment is made by exchanging a cash amount or a physical asset."""

    CASH = "Cash"
    """A cash amount is exchanged."""
    PHYSICAL = "Physical"
    """A physical asset is exchanged."""


class SettlementTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of SettlementTypeEnum."""

    PHYSICAL = "Physical"
    CASH = "Cash"
    CCP = "CCP"


class ShiftTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of ShiftTypeEnum."""

    ADDITIVE = "Additive"
    RELATIVE = "Relative"
    SCALED = "Scaled"


class ShiftUnitEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of ShiftUnitEnum."""

    ABSOLUTE = "Absolute"
    BP = "Bp"
    PERCENT = "Percent"


class SolvingLegEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """A swap leg to which the the target or variable property applies."""

    FIRST_LEG = "FirstLeg"
    """The solution is calculated for the first leg."""
    SECOND_LEG = "SecondLeg"
    """The solution is calculated for the second leg."""


class SolvingMethodEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The method used to select the variable parameter value."""

    BI_SECTION = "BiSection"
    """An approximation method to find the roots of the given equation by repeatedly dividing an
    interval in half until it narrows down to a root.
    """
    BRENT = "Brent"
    """A hybrid root-finding algorithm combining the bisection method, the secant method and inverse
    quadratic interpolation.
    """
    SECANT = "Secant"
    """A root-finding procedure in numerical analysis that uses a series of roots of secant lines to
    better approximate a root of a continoius function.
    """


class SortingOrderEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of SortingOrderEnum."""

    ASC = "Asc"
    DESC = "Desc"


class SpreadCompoundingModeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The mode used to define how the spread is applied to a compound interest rate."""

    ISDA_COMPOUNDING = "IsdaCompounding"
    """The index and the spread are compounded together."""
    ISDA_FLAT_COMPOUNDING = "IsdaFlatCompounding"
    """The spread is compounded with the index only for the first reset. After that only the index is
    compounded.
    """
    NO_COMPOUNDING = "NoCompounding"
    """The spread is not compounded. It is added to the compounded index."""


class SpreadRoundingEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of SpreadRoundingEnum."""

    ZERO = "Zero"
    ONE = "One"
    TWO = "Two"
    THREE = "Three"
    FOUR = "Four"
    FIVE = "Five"
    SIX = "Six"
    SEVEN = "Seven"
    EIGHT = "Eight"
    DEFAULT = "Default"
    UNROUNDED = "Unrounded"


class SpreadRoundingTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of SpreadRoundingTypeEnum."""

    NEAR = "Near"
    UP = "Up"
    DOWN = "Down"
    FLOOR = "Floor"
    CEIL = "Ceil"
    FACE_NEAR = "FaceNear"
    FACE_DOWN = "FaceDown"
    FACE_UP = "FaceUp"
    DEFAULT = "Default"


class StartDateMovingConventionEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of StartDateMovingConventionEnum."""

    MODIFIED_FOLLOWING = "ModifiedFollowing"
    NEXT_BUSINESS_DAY = "NextBusinessDay"
    PREVIOUS_BUSINESS_DAY = "PreviousBusinessDay"
    NO_MOVING = "NoMoving"
    EVERY_THIRD_WEDNESDAY = "EveryThirdWednesday"
    BBSW_MODIFIED_FOLLOWING = "BbswModifiedFollowing"


class Status(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The status of the resource."""

    ACTIVE = "Active"
    DELETED = "Deleted"


class StepModeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of StepModeEnum."""

    CONSTANT_FORWARD_RATES_ONLY = "ConstantForwardRatesOnly"
    CONSTANT_FORWARD_RATES_THEN_ZERO_COUPON_RATES = "ConstantForwardRatesThenZeroCouponRates"
    NONE = "None"


class StoreType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of StoreType."""

    TABLE = "table"
    CURVE = "curve"
    PREPAY_DIALS = "prepay-dials"
    OUTPUT_FORMAT = "output-format"
    VOL_SURFACE = "vol-surface"
    YBPORT_UDI = "ybport-udi"
    CMO_MODIFICATION = "cmo-modification"
    SCENARIO_V1 = "scenario-v1"
    CURRENT_COUPON_SPREAD = "currentCouponSpread"


class StrikeTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """An object defining the way the strike price is expressed when constructing the volatility
    surface.
    """

    ABSOLUTE = "Absolute"
    BASIS_POINT = "BasisPoint"
    DELTA = "Delta"
    MONEYNESS = "Moneyness"
    PERCENT = "Percent"
    RELATIVE = "Relative"


class StubRuleEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Specifies whether the first or last coupon period is unregular."""

    LONG_FIRST = "LongFirst"
    """All payment dates are calculated backwards from the end date of the schedule. The generation
    stops so that the first period is a long period.
    """
    LONG_LAST = "LongLast"
    """All payment dates are calculated backwards from the start date of the schedule. The generation
    stops so that the last period is a long period.
    """
    SHORT_FIRST = "ShortFirst"
    """All payment dates are calculated backwards from the end date of the schedule. The generation
    stops so that the first period is a short period.
    """
    SHORT_LAST = "ShortLast"
    """All payment dates are calculated backwards from the start date of the schedule. The generation
    stops so that the last period is a short period.
    """


class SubSectorEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of SubSectorEnum."""

    BASE_METALS_ORES = "BaseMetalsOres"
    BIOFUELS = "Biofuels"
    CHEMICALS = "Chemicals"
    CLOUD = "Cloud"
    COAL = "Coal"
    DAIRY = "Dairy"
    DRY_BULK_FREIGHT = "DryBulkFreight"
    EMISSIONS = "Emissions"
    FERTILIZER = "Fertilizer"
    FORESTRY_FIBRE = "ForestryFibre"
    GAS_PRODUCTS = "GasProducts"
    GRAINS = "Grains"
    IRON_STEEL = "IronSteel"
    LIVESTOCK = "Livestock"
    MEALS_FEEDS_PULSES = "MealsFeedsPulses"
    MINOR_METALS_MINERALS = "MinorMetalsMinerals"
    MISCELLANEOUS_AGRICULTURE = "MiscellaneousAgriculture"
    OIL_PRODUCTS = "OilProducts"
    OILSEEDS = "Oilseeds"
    PETROCHEMICALS = "Petrochemicals"
    POWER = "Power"
    PRECIOUS_METALS_MINERALS = "PreciousMetalsMinerals"
    RENEWABLE_ENERGY = "RenewableEnergy"
    SCRAP_SECONDARY_ALLOYS = "ScrapSecondaryAlloys"
    SOFTS = "Softs"
    TANKER_FREIGHT = "TankerFreight"
    TEMPERATURE = "Temperature"


class SwapSolvingVariableEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The list of swap variable parameters for which the solution is calculated."""

    FIXED_RATE = "FixedRate"
    """The solution is calculated for the fixed rate."""
    SPREAD = "Spread"
    """The solution is calculated for the spread."""


class SwaptionTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of SwaptionTypeEnum."""

    PAYER = "Payer"
    RECEIVER = "Receiver"


class TenorReferenceDateEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of TenorReferenceDateEnum."""

    SPOT_DATE = "SpotDate"
    VALUATION_DATE = "ValuationDate"


class TenorType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The tenor type."""

    ODD = "Odd"
    """A period selected from a list that includes both standard and non-standard periods.
    The standard periods are: ON, TN, SN, SW, 1M, 2M, 3M, 6M, 9M, 1Y, 2Y.
    The non-standard periods are: 2W, 3W, 2M, 4M, 5M, 7M, 8M, 10M, 11M, 15M, 18M, 21M.
    """
    LONG = "Long"
    """Long-term tenor. The length of long-term tenors depends on the asset class."""
    IMM = "IMM"
    """The end date of the tenor is the third Wednesday of either: March, June, September or December.

    * IMM1 means the next of the 4 possible days.
    * IMM2 means the one after next of the 4 possible days.
    * IMM3 means the second after next of the 4 possible days.
    * IMM4 means the third after next of the 4 possible days.

    For example, if the current date is 23rd of April, IMM1 is the third Wdnesday in June, IMM2 is
    the third wednesday in September, etc..
    """
    BEGINNING_OF_MONTH = "BeginningOfMonth"
    """The end date of the tenor is the first business day of a month.
    Possible values are: JANB, FEBB, MARB, APRB, MAYB, JUNB, JULB, AUGB, SEPB, OCTB, NOVB, DECB.
    The first three letters of each value represents the month. So, JANB is the first business day
    of January, FEBB is the first business day of February, etc..
    """
    END_OF_MONTH = "EndOfMonth"
    """The end date of the tenor is the last business day of a month.
    Possible values are: JANM, FEBM, MARM, APRM, MAYM, JUNM, JULM, AUGM, SEPM, OCTM, NOVM, DECM.
    The first three letters of each value represents the month. So, JANM is the last business day
    of January, FEBM is the last business day of February, etc..
    """


class TimeStampEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The mode used to select the timestamp for an instrument."""

    OPEN = "Open"
    """The opening price of the valuation date, or if it is not available, the close price of the
    previous day is used.
    """
    CLOSE = "Close"
    """The close price of the valuation date is used."""
    SETTLE = "Settle"
    """The settle price of the valuation date is used."""
    DEFAULT = "Default"
    """The real-time price is used (if available) when the valuation date is today, and the close
    price when the valuation date is in the past.
    """


class TimezoneEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of TimezoneEnum."""

    AFRICA_ABIDJAN = "Africa/Abidjan"
    AFRICA_ACCRA = "Africa/Accra"
    AFRICA_ADDIS_ABABA = "Africa/Addis_Ababa"
    AFRICA_ALGIERS = "Africa/Algiers"
    AFRICA_ASMARA = "Africa/Asmara"
    AFRICA_ASMERA = "Africa/Asmera"
    AFRICA_BAMAKO = "Africa/Bamako"
    AFRICA_BANGUI = "Africa/Bangui"
    AFRICA_BANJUL = "Africa/Banjul"
    AFRICA_BISSAU = "Africa/Bissau"
    AFRICA_BLANTYRE = "Africa/Blantyre"
    AFRICA_BRAZZAVILLE = "Africa/Brazzaville"
    AFRICA_BUJUMBURA = "Africa/Bujumbura"
    AFRICA_CAIRO = "Africa/Cairo"
    AFRICA_CASABLANCA = "Africa/Casablanca"
    AFRICA_CEUTA = "Africa/Ceuta"
    AFRICA_CONAKRY = "Africa/Conakry"
    AFRICA_DAKAR = "Africa/Dakar"
    AFRICA_DAR_ES_SALAAM = "Africa/Dar_es_Salaam"
    AFRICA_DJIBOUTI = "Africa/Djibouti"
    AFRICA_DOUALA = "Africa/Douala"
    AFRICA_EL_AAIUN = "Africa/El_Aaiun"
    AFRICA_FREETOWN = "Africa/Freetown"
    AFRICA_GABORONE = "Africa/Gaborone"
    AFRICA_HARARE = "Africa/Harare"
    AFRICA_JOHANNESBURG = "Africa/Johannesburg"
    AFRICA_JUBA = "Africa/Juba"
    AFRICA_KAMPALA = "Africa/Kampala"
    AFRICA_KHARTOUM = "Africa/Khartoum"
    AFRICA_KIGALI = "Africa/Kigali"
    AFRICA_KINSHASA = "Africa/Kinshasa"
    AFRICA_LAGOS = "Africa/Lagos"
    AFRICA_LIBREVILLE = "Africa/Libreville"
    AFRICA_LOME = "Africa/Lome"
    AFRICA_LUANDA = "Africa/Luanda"
    AFRICA_LUBUMBASHI = "Africa/Lubumbashi"
    AFRICA_LUSAKA = "Africa/Lusaka"
    AFRICA_MALABO = "Africa/Malabo"
    AFRICA_MAPUTO = "Africa/Maputo"
    AFRICA_MASERU = "Africa/Maseru"
    AFRICA_MBABANE = "Africa/Mbabane"
    AFRICA_MOGADISHU = "Africa/Mogadishu"
    AFRICA_MONROVIA = "Africa/Monrovia"
    AFRICA_NAIROBI = "Africa/Nairobi"
    AFRICA_NDJAMENA = "Africa/Ndjamena"
    AFRICA_NIAMEY = "Africa/Niamey"
    AFRICA_NOUAKCHOTT = "Africa/Nouakchott"
    AFRICA_OUAGADOUGOU = "Africa/Ouagadougou"
    AFRICA_PORTO_NOVO = "Africa/Porto-Novo"
    AFRICA_SAO_TOME = "Africa/Sao_Tome"
    AFRICA_TIMBUKTU = "Africa/Timbuktu"
    AFRICA_TRIPOLI = "Africa/Tripoli"
    AFRICA_TUNIS = "Africa/Tunis"
    AFRICA_WINDHOEK = "Africa/Windhoek"
    AMERICA_ADAK = "America/Adak"
    AMERICA_ANCHORAGE = "America/Anchorage"
    AMERICA_ANGUILLA = "America/Anguilla"
    AMERICA_ANTIGUA = "America/Antigua"
    AMERICA_ARAGUAINA = "America/Araguaina"
    AMERICA_ARGENTINA_BUENOS_AIRES = "America/Argentina/Buenos_Aires"
    AMERICA_ARGENTINA_CATAMARCA = "America/Argentina/Catamarca"
    AMERICA_ARGENTINA_COMOD_RIVADAVIA = "America/Argentina/ComodRivadavia"
    AMERICA_ARGENTINA_CORDOBA = "America/Argentina/Cordoba"
    AMERICA_ARGENTINA_JUJUY = "America/Argentina/Jujuy"
    AMERICA_ARGENTINA_LA_RIOJA = "America/Argentina/La_Rioja"
    AMERICA_ARGENTINA_MENDOZA = "America/Argentina/Mendoza"
    AMERICA_ARGENTINA_RIO_GALLEGOS = "America/Argentina/Rio_Gallegos"
    AMERICA_ARGENTINA_SALTA = "America/Argentina/Salta"
    AMERICA_ARGENTINA_SAN_JUAN = "America/Argentina/San_Juan"
    AMERICA_ARGENTINA_SAN_LUIS = "America/Argentina/San_Luis"
    AMERICA_ARGENTINA_TUCUMAN = "America/Argentina/Tucuman"
    AMERICA_ARGENTINA_USHUAIA = "America/Argentina/Ushuaia"
    AMERICA_ARUBA = "America/Aruba"
    AMERICA_ASUNCION = "America/Asuncion"
    AMERICA_ATIKOKAN = "America/Atikokan"
    AMERICA_ATKA = "America/Atka"
    AMERICA_BAHIA = "America/Bahia"
    AMERICA_BAHIA_BANDERAS = "America/Bahia_Banderas"
    AMERICA_BARBADOS = "America/Barbados"
    AMERICA_BELEM = "America/Belem"
    AMERICA_BELIZE = "America/Belize"
    AMERICA_BLANC_SABLON = "America/Blanc-Sablon"
    AMERICA_BOA_VISTA = "America/Boa_Vista"
    AMERICA_BOGOTA = "America/Bogota"
    AMERICA_BOISE = "America/Boise"
    AMERICA_BUENOS_AIRES = "America/Buenos_Aires"
    AMERICA_CAMBRIDGE_BAY = "America/Cambridge_Bay"
    AMERICA_CAMPO_GRANDE = "America/Campo_Grande"
    AMERICA_CANCUN = "America/Cancun"
    AMERICA_CARACAS = "America/Caracas"
    AMERICA_CATAMARCA = "America/Catamarca"
    AMERICA_CAYENNE = "America/Cayenne"
    AMERICA_CAYMAN = "America/Cayman"
    AMERICA_CHICAGO = "America/Chicago"
    AMERICA_CHIHUAHUA = "America/Chihuahua"
    AMERICA_CIUDAD_JUAREZ = "America/Ciudad_Juarez"
    AMERICA_CORAL_HARBOUR = "America/Coral_Harbour"
    AMERICA_CORDOBA = "America/Cordoba"
    AMERICA_COSTA_RICA = "America/Costa_Rica"
    AMERICA_CRESTON = "America/Creston"
    AMERICA_CUIABA = "America/Cuiaba"
    AMERICA_CURACAO = "America/Curacao"
    AMERICA_DANMARKSHAVN = "America/Danmarkshavn"
    AMERICA_DAWSON = "America/Dawson"
    AMERICA_DAWSON_CREEK = "America/Dawson_Creek"
    AMERICA_DENVER = "America/Denver"
    AMERICA_DETROIT = "America/Detroit"
    AMERICA_DOMINICA = "America/Dominica"
    AMERICA_EDMONTON = "America/Edmonton"
    AMERICA_EIRUNEPE = "America/Eirunepe"
    AMERICA_EL_SALVADOR = "America/El_Salvador"
    AMERICA_ENSENADA = "America/Ensenada"
    AMERICA_FORT_NELSON = "America/Fort_Nelson"
    AMERICA_FORT_WAYNE = "America/Fort_Wayne"
    AMERICA_FORTALEZA = "America/Fortaleza"
    AMERICA_GLACE_BAY = "America/Glace_Bay"
    AMERICA_GODTHAB = "America/Godthab"
    AMERICA_GOOSE_BAY = "America/Goose_Bay"
    AMERICA_GRAND_TURK = "America/Grand_Turk"
    AMERICA_GRENADA = "America/Grenada"
    AMERICA_GUADELOUPE = "America/Guadeloupe"
    AMERICA_GUATEMALA = "America/Guatemala"
    AMERICA_GUAYAQUIL = "America/Guayaquil"
    AMERICA_GUYANA = "America/Guyana"
    AMERICA_HALIFAX = "America/Halifax"
    AMERICA_HAVANA = "America/Havana"
    AMERICA_HERMOSILLO = "America/Hermosillo"
    AMERICA_INDIANA_INDIANAPOLIS = "America/Indiana/Indianapolis"
    AMERICA_INDIANA_KNOX = "America/Indiana/Knox"
    AMERICA_INDIANA_MARENGO = "America/Indiana/Marengo"
    AMERICA_INDIANA_PETERSBURG = "America/Indiana/Petersburg"
    AMERICA_INDIANA_TELL_CITY = "America/Indiana/Tell_City"
    AMERICA_INDIANA_VEVAY = "America/Indiana/Vevay"
    AMERICA_INDIANA_VINCENNES = "America/Indiana/Vincennes"
    AMERICA_INDIANA_WINAMAC = "America/Indiana/Winamac"
    AMERICA_INDIANAPOLIS = "America/Indianapolis"
    AMERICA_INUVIK = "America/Inuvik"
    AMERICA_IQALUIT = "America/Iqaluit"
    AMERICA_JAMAICA = "America/Jamaica"
    AMERICA_JUJUY = "America/Jujuy"
    AMERICA_JUNEAU = "America/Juneau"
    AMERICA_KENTUCKY_LOUISVILLE = "America/Kentucky/Louisville"
    AMERICA_KENTUCKY_MONTICELLO = "America/Kentucky/Monticello"
    AMERICA_KNOX_IN = "America/Knox_IN"
    AMERICA_KRALENDIJK = "America/Kralendijk"
    AMERICA_LA_PAZ = "America/La_Paz"
    AMERICA_LIMA = "America/Lima"
    AMERICA_LOS_ANGELES = "America/Los_Angeles"
    AMERICA_LOUISVILLE = "America/Louisville"
    AMERICA_LOWER_PRINCES = "America/Lower_Princes"
    AMERICA_MACEIO = "America/Maceio"
    AMERICA_MANAGUA = "America/Managua"
    AMERICA_MANAUS = "America/Manaus"
    AMERICA_MARIGOT = "America/Marigot"
    AMERICA_MARTINIQUE = "America/Martinique"
    AMERICA_MATAMOROS = "America/Matamoros"
    AMERICA_MAZATLAN = "America/Mazatlan"
    AMERICA_MENDOZA = "America/Mendoza"
    AMERICA_MENOMINEE = "America/Menominee"
    AMERICA_MERIDA = "America/Merida"
    AMERICA_METLAKATLA = "America/Metlakatla"
    AMERICA_MEXICO_CITY = "America/Mexico_City"
    AMERICA_MIQUELON = "America/Miquelon"
    AMERICA_MONCTON = "America/Moncton"
    AMERICA_MONTERREY = "America/Monterrey"
    AMERICA_MONTEVIDEO = "America/Montevideo"
    AMERICA_MONTREAL = "America/Montreal"
    AMERICA_MONTSERRAT = "America/Montserrat"
    AMERICA_NASSAU = "America/Nassau"
    AMERICA_NEW_YORK = "America/New_York"
    AMERICA_NIPIGON = "America/Nipigon"
    AMERICA_NOME = "America/Nome"
    AMERICA_NORONHA = "America/Noronha"
    AMERICA_NORTH_DAKOTA_BEULAH = "America/North_Dakota/Beulah"
    AMERICA_NORTH_DAKOTA_CENTER = "America/North_Dakota/Center"
    AMERICA_NORTH_DAKOTA_NEW_SALEM = "America/North_Dakota/New_Salem"
    AMERICA_NUUK = "America/Nuuk"
    AMERICA_OJINAGA = "America/Ojinaga"
    AMERICA_PANAMA = "America/Panama"
    AMERICA_PANGNIRTUNG = "America/Pangnirtung"
    AMERICA_PARAMARIBO = "America/Paramaribo"
    AMERICA_PHOENIX = "America/Phoenix"
    AMERICA_PORT_AU_PRINCE = "America/Port-au-Prince"
    AMERICA_PORT_OF_SPAIN = "America/Port_of_Spain"
    AMERICA_PORTO_ACRE = "America/Porto_Acre"
    AMERICA_PORTO_VELHO = "America/Porto_Velho"
    AMERICA_PUERTO_RICO = "America/Puerto_Rico"
    AMERICA_PUNTA_ARENAS = "America/Punta_Arenas"
    AMERICA_RAINY_RIVER = "America/Rainy_River"
    AMERICA_RANKIN_INLET = "America/Rankin_Inlet"
    AMERICA_RECIFE = "America/Recife"
    AMERICA_REGINA = "America/Regina"
    AMERICA_RESOLUTE = "America/Resolute"
    AMERICA_RIO_BRANCO = "America/Rio_Branco"
    AMERICA_ROSARIO = "America/Rosario"
    AMERICA_SANTA_ISABEL = "America/Santa_Isabel"
    AMERICA_SANTAREM = "America/Santarem"
    AMERICA_SANTIAGO = "America/Santiago"
    AMERICA_SANTO_DOMINGO = "America/Santo_Domingo"
    AMERICA_SAO_PAULO = "America/Sao_Paulo"
    AMERICA_SCORESBYSUND = "America/Scoresbysund"
    AMERICA_SHIPROCK = "America/Shiprock"
    AMERICA_SITKA = "America/Sitka"
    AMERICA_ST_BARTHELEMY = "America/St_Barthelemy"
    AMERICA_ST_JOHNS = "America/St_Johns"
    AMERICA_ST_KITTS = "America/St_Kitts"
    AMERICA_ST_LUCIA = "America/St_Lucia"
    AMERICA_ST_THOMAS = "America/St_Thomas"
    AMERICA_ST_VINCENT = "America/St_Vincent"
    AMERICA_SWIFT_CURRENT = "America/Swift_Current"
    AMERICA_TEGUCIGALPA = "America/Tegucigalpa"
    AMERICA_THULE = "America/Thule"
    AMERICA_THUNDER_BAY = "America/Thunder_Bay"
    AMERICA_TIJUANA = "America/Tijuana"
    AMERICA_TORONTO = "America/Toronto"
    AMERICA_TORTOLA = "America/Tortola"
    AMERICA_VANCOUVER = "America/Vancouver"
    AMERICA_VIRGIN = "America/Virgin"
    AMERICA_WHITEHORSE = "America/Whitehorse"
    AMERICA_WINNIPEG = "America/Winnipeg"
    AMERICA_YAKUTAT = "America/Yakutat"
    AMERICA_YELLOWKNIFE = "America/Yellowknife"
    ANTARCTICA_CASEY = "Antarctica/Casey"
    ANTARCTICA_DAVIS = "Antarctica/Davis"
    ANTARCTICA_DUMONT_D_URVILLE = "Antarctica/DumontDUrville"
    ANTARCTICA_MACQUARIE = "Antarctica/Macquarie"
    ANTARCTICA_MAWSON = "Antarctica/Mawson"
    ANTARCTICA_MC_MURDO = "Antarctica/McMurdo"
    ANTARCTICA_PALMER = "Antarctica/Palmer"
    ANTARCTICA_ROTHERA = "Antarctica/Rothera"
    ANTARCTICA_SOUTH_POLE = "Antarctica/South_Pole"
    ANTARCTICA_SYOWA = "Antarctica/Syowa"
    ANTARCTICA_TROLL = "Antarctica/Troll"
    ANTARCTICA_VOSTOK = "Antarctica/Vostok"
    ARCTIC_LONGYEARBYEN = "Arctic/Longyearbyen"
    ASIA_ADEN = "Asia/Aden"
    ASIA_ALMATY = "Asia/Almaty"
    ASIA_AMMAN = "Asia/Amman"
    ASIA_ANADYR = "Asia/Anadyr"
    ASIA_AQTAU = "Asia/Aqtau"
    ASIA_AQTOBE = "Asia/Aqtobe"
    ASIA_ASHGABAT = "Asia/Ashgabat"
    ASIA_ASHKHABAD = "Asia/Ashkhabad"
    ASIA_ATYRAU = "Asia/Atyrau"
    ASIA_BAGHDAD = "Asia/Baghdad"
    ASIA_BAHRAIN = "Asia/Bahrain"
    ASIA_BAKU = "Asia/Baku"
    ASIA_BANGKOK = "Asia/Bangkok"
    ASIA_BARNAUL = "Asia/Barnaul"
    ASIA_BEIRUT = "Asia/Beirut"
    ASIA_BISHKEK = "Asia/Bishkek"
    ASIA_BRUNEI = "Asia/Brunei"
    ASIA_CALCUTTA = "Asia/Calcutta"
    ASIA_CHITA = "Asia/Chita"
    ASIA_CHOIBALSAN = "Asia/Choibalsan"
    ASIA_CHONGQING = "Asia/Chongqing"
    ASIA_CHUNGKING = "Asia/Chungking"
    ASIA_COLOMBO = "Asia/Colombo"
    ASIA_DACCA = "Asia/Dacca"
    ASIA_DAMASCUS = "Asia/Damascus"
    ASIA_DHAKA = "Asia/Dhaka"
    ASIA_DILI = "Asia/Dili"
    ASIA_DUBAI = "Asia/Dubai"
    ASIA_DUSHANBE = "Asia/Dushanbe"
    ASIA_FAMAGUSTA = "Asia/Famagusta"
    ASIA_GAZA = "Asia/Gaza"
    ASIA_HARBIN = "Asia/Harbin"
    ASIA_HEBRON = "Asia/Hebron"
    ASIA_HO_CHI_MINH = "Asia/Ho_Chi_Minh"
    ASIA_HONG_KONG = "Asia/Hong_Kong"
    ASIA_HOVD = "Asia/Hovd"
    ASIA_IRKUTSK = "Asia/Irkutsk"
    ASIA_ISTANBUL = "Asia/Istanbul"
    ASIA_JAKARTA = "Asia/Jakarta"
    ASIA_JAYAPURA = "Asia/Jayapura"
    ASIA_JERUSALEM = "Asia/Jerusalem"
    ASIA_KABUL = "Asia/Kabul"
    ASIA_KAMCHATKA = "Asia/Kamchatka"
    ASIA_KARACHI = "Asia/Karachi"
    ASIA_KASHGAR = "Asia/Kashgar"
    ASIA_KATHMANDU = "Asia/Kathmandu"
    ASIA_KATMANDU = "Asia/Katmandu"
    ASIA_KHANDYGA = "Asia/Khandyga"
    ASIA_KOLKATA = "Asia/Kolkata"
    ASIA_KRASNOYARSK = "Asia/Krasnoyarsk"
    ASIA_KUALA_LUMPUR = "Asia/Kuala_Lumpur"
    ASIA_KUCHING = "Asia/Kuching"
    ASIA_KUWAIT = "Asia/Kuwait"
    ASIA_MACAO = "Asia/Macao"
    ASIA_MACAU = "Asia/Macau"
    ASIA_MAGADAN = "Asia/Magadan"
    ASIA_MAKASSAR = "Asia/Makassar"
    ASIA_MANILA = "Asia/Manila"
    ASIA_MUSCAT = "Asia/Muscat"
    ASIA_NICOSIA = "Asia/Nicosia"
    ASIA_NOVOKUZNETSK = "Asia/Novokuznetsk"
    ASIA_NOVOSIBIRSK = "Asia/Novosibirsk"
    ASIA_OMSK = "Asia/Omsk"
    ASIA_ORAL = "Asia/Oral"
    ASIA_PHNOM_PENH = "Asia/Phnom_Penh"
    ASIA_PONTIANAK = "Asia/Pontianak"
    ASIA_PYONGYANG = "Asia/Pyongyang"
    ASIA_QATAR = "Asia/Qatar"
    ASIA_QOSTANAY = "Asia/Qostanay"
    ASIA_QYZYLORDA = "Asia/Qyzylorda"
    ASIA_RANGOON = "Asia/Rangoon"
    ASIA_RIYADH = "Asia/Riyadh"
    ASIA_SAIGON = "Asia/Saigon"
    ASIA_SAKHALIN = "Asia/Sakhalin"
    ASIA_SAMARKAND = "Asia/Samarkand"
    ASIA_SEOUL = "Asia/Seoul"
    ASIA_SHANGHAI = "Asia/Shanghai"
    ASIA_SINGAPORE = "Asia/Singapore"
    ASIA_SREDNEKOLYMSK = "Asia/Srednekolymsk"
    ASIA_TAIPEI = "Asia/Taipei"
    ASIA_TASHKENT = "Asia/Tashkent"
    ASIA_TBILISI = "Asia/Tbilisi"
    ASIA_TEHRAN = "Asia/Tehran"
    ASIA_TEL_AVIV = "Asia/Tel_Aviv"
    ASIA_THIMBU = "Asia/Thimbu"
    ASIA_THIMPHU = "Asia/Thimphu"
    ASIA_TOKYO = "Asia/Tokyo"
    ASIA_TOMSK = "Asia/Tomsk"
    ASIA_UJUNG_PANDANG = "Asia/Ujung_Pandang"
    ASIA_ULAANBAATAR = "Asia/Ulaanbaatar"
    ASIA_ULAN_BATOR = "Asia/Ulan_Bator"
    ASIA_URUMQI = "Asia/Urumqi"
    ASIA_UST_NERA = "Asia/Ust-Nera"
    ASIA_VIENTIANE = "Asia/Vientiane"
    ASIA_VLADIVOSTOK = "Asia/Vladivostok"
    ASIA_YAKUTSK = "Asia/Yakutsk"
    ASIA_YANGON = "Asia/Yangon"
    ASIA_YEKATERINBURG = "Asia/Yekaterinburg"
    ASIA_YEREVAN = "Asia/Yerevan"
    ATLANTIC_AZORES = "Atlantic/Azores"
    ATLANTIC_BERMUDA = "Atlantic/Bermuda"
    ATLANTIC_CANARY = "Atlantic/Canary"
    ATLANTIC_CAPE_VERDE = "Atlantic/Cape_Verde"
    ATLANTIC_FAEROE = "Atlantic/Faeroe"
    ATLANTIC_FAROE = "Atlantic/Faroe"
    ATLANTIC_JAN_MAYEN = "Atlantic/Jan_Mayen"
    ATLANTIC_MADEIRA = "Atlantic/Madeira"
    ATLANTIC_REYKJAVIK = "Atlantic/Reykjavik"
    ATLANTIC_SOUTH_GEORGIA = "Atlantic/South_Georgia"
    ATLANTIC_ST_HELENA = "Atlantic/St_Helena"
    ATLANTIC_STANLEY = "Atlantic/Stanley"
    AUSTRALIA_ACT = "Australia/ACT"
    AUSTRALIA_ADELAIDE = "Australia/Adelaide"
    AUSTRALIA_BRISBANE = "Australia/Brisbane"
    AUSTRALIA_BROKEN_HILL = "Australia/Broken_Hill"
    AUSTRALIA_CANBERRA = "Australia/Canberra"
    AUSTRALIA_CURRIE = "Australia/Currie"
    AUSTRALIA_DARWIN = "Australia/Darwin"
    AUSTRALIA_EUCLA = "Australia/Eucla"
    AUSTRALIA_HOBART = "Australia/Hobart"
    AUSTRALIA_LHI = "Australia/LHI"
    AUSTRALIA_LINDEMAN = "Australia/Lindeman"
    AUSTRALIA_LORD_HOWE = "Australia/Lord_Howe"
    AUSTRALIA_MELBOURNE = "Australia/Melbourne"
    AUSTRALIA_NSW = "Australia/NSW"
    AUSTRALIA_NORTH = "Australia/North"
    AUSTRALIA_PERTH = "Australia/Perth"
    AUSTRALIA_QUEENSLAND = "Australia/Queensland"
    AUSTRALIA_SOUTH = "Australia/South"
    AUSTRALIA_SYDNEY = "Australia/Sydney"
    AUSTRALIA_TASMANIA = "Australia/Tasmania"
    AUSTRALIA_VICTORIA = "Australia/Victoria"
    AUSTRALIA_WEST = "Australia/West"
    AUSTRALIA_YANCOWINNA = "Australia/Yancowinna"
    BRAZIL_ACRE = "Brazil/Acre"
    BRAZIL_DE_NORONHA = "Brazil/DeNoronha"
    BRAZIL_EAST = "Brazil/East"
    BRAZIL_WEST = "Brazil/West"
    CET = "CET"
    CST6CDT = "CST6CDT"
    CANADA_ATLANTIC = "Canada/Atlantic"
    CANADA_CENTRAL = "Canada/Central"
    CANADA_EASTERN = "Canada/Eastern"
    CANADA_MOUNTAIN = "Canada/Mountain"
    CANADA_NEWFOUNDLAND = "Canada/Newfoundland"
    CANADA_PACIFIC = "Canada/Pacific"
    CANADA_SASKATCHEWAN = "Canada/Saskatchewan"
    CANADA_YUKON = "Canada/Yukon"
    CHILE_CONTINENTAL = "Chile/Continental"
    CHILE_EASTER_ISLAND = "Chile/EasterIsland"
    CUBA = "Cuba"
    EET = "EET"
    EST = "EST"
    EST5EDT = "EST5EDT"
    EGYPT = "Egypt"
    EIRE = "Eire"
    ETC_GMT = "Etc/GMT"
    ETC_GMT_PLUS_0 = "Etc/GMT+0"
    ETC_GMT_PLUS_1 = "Etc/GMT+1"
    ETC_GMT_PLUS_10 = "Etc/GMT+10"
    ETC_GMT_PLUS_11 = "Etc/GMT+11"
    ETC_GMT_PLUS_12 = "Etc/GMT+12"
    ETC_GMT_PLUS_2 = "Etc/GMT+2"
    ETC_GMT_PLUS_3 = "Etc/GMT+3"
    ETC_GMT_PLUS_4 = "Etc/GMT+4"
    ETC_GMT_PLUS_5 = "Etc/GMT+5"
    ETC_GMT_PLUS_6 = "Etc/GMT+6"
    ETC_GMT_PLUS_7 = "Etc/GMT+7"
    ETC_GMT_PLUS_8 = "Etc/GMT+8"
    ETC_GMT_PLUS_9 = "Etc/GMT+9"
    ETC_GMT_MINUS_0 = "Etc/GMT-0"
    ETC_GMT_MINUS_1 = "Etc/GMT-1"
    ETC_GMT_MINUS_10 = "Etc/GMT-10"
    ETC_GMT_MINUS_11 = "Etc/GMT-11"
    ETC_GMT_MINUS_12 = "Etc/GMT-12"
    ETC_GMT_MINUS_13 = "Etc/GMT-13"
    ETC_GMT_MINUS_14 = "Etc/GMT-14"
    ETC_GMT_MINUS_2 = "Etc/GMT-2"
    ETC_GMT_MINUS_3 = "Etc/GMT-3"
    ETC_GMT_MINUS_4 = "Etc/GMT-4"
    ETC_GMT_MINUS_5 = "Etc/GMT-5"
    ETC_GMT_MINUS_6 = "Etc/GMT-6"
    ETC_GMT_MINUS_7 = "Etc/GMT-7"
    ETC_GMT_MINUS_8 = "Etc/GMT-8"
    ETC_GMT_MINUS_9 = "Etc/GMT-9"
    ETC_GMT0 = "Etc/GMT0"
    ETC_GREENWICH = "Etc/Greenwich"
    ETC_UCT = "Etc/UCT"
    ETC_UTC = "Etc/UTC"
    ETC_UNIVERSAL = "Etc/Universal"
    ETC_ZULU = "Etc/Zulu"
    EUROPE_AMSTERDAM = "Europe/Amsterdam"
    EUROPE_ANDORRA = "Europe/Andorra"
    EUROPE_ASTRAKHAN = "Europe/Astrakhan"
    EUROPE_ATHENS = "Europe/Athens"
    EUROPE_BELFAST = "Europe/Belfast"
    EUROPE_BELGRADE = "Europe/Belgrade"
    EUROPE_BERLIN = "Europe/Berlin"
    EUROPE_BRATISLAVA = "Europe/Bratislava"
    EUROPE_BRUSSELS = "Europe/Brussels"
    EUROPE_BUCHAREST = "Europe/Bucharest"
    EUROPE_BUDAPEST = "Europe/Budapest"
    EUROPE_BUSINGEN = "Europe/Busingen"
    EUROPE_CHISINAU = "Europe/Chisinau"
    EUROPE_COPENHAGEN = "Europe/Copenhagen"
    EUROPE_DUBLIN = "Europe/Dublin"
    EUROPE_GIBRALTAR = "Europe/Gibraltar"
    EUROPE_GUERNSEY = "Europe/Guernsey"
    EUROPE_HELSINKI = "Europe/Helsinki"
    EUROPE_ISLE_OF_MAN = "Europe/Isle_of_Man"
    EUROPE_ISTANBUL = "Europe/Istanbul"
    EUROPE_JERSEY = "Europe/Jersey"
    EUROPE_KALININGRAD = "Europe/Kaliningrad"
    EUROPE_KIEV = "Europe/Kiev"
    EUROPE_KIROV = "Europe/Kirov"
    EUROPE_KYIV = "Europe/Kyiv"
    EUROPE_LISBON = "Europe/Lisbon"
    EUROPE_LJUBLJANA = "Europe/Ljubljana"
    EUROPE_LONDON = "Europe/London"
    EUROPE_LUXEMBOURG = "Europe/Luxembourg"
    EUROPE_MADRID = "Europe/Madrid"
    EUROPE_MALTA = "Europe/Malta"
    EUROPE_MARIEHAMN = "Europe/Mariehamn"
    EUROPE_MINSK = "Europe/Minsk"
    EUROPE_MONACO = "Europe/Monaco"
    EUROPE_MOSCOW = "Europe/Moscow"
    EUROPE_NICOSIA = "Europe/Nicosia"
    EUROPE_OSLO = "Europe/Oslo"
    EUROPE_PARIS = "Europe/Paris"
    EUROPE_PODGORICA = "Europe/Podgorica"
    EUROPE_PRAGUE = "Europe/Prague"
    EUROPE_RIGA = "Europe/Riga"
    EUROPE_ROME = "Europe/Rome"
    EUROPE_SAMARA = "Europe/Samara"
    EUROPE_SAN_MARINO = "Europe/San_Marino"
    EUROPE_SARAJEVO = "Europe/Sarajevo"
    EUROPE_SARATOV = "Europe/Saratov"
    EUROPE_SIMFEROPOL = "Europe/Simferopol"
    EUROPE_SKOPJE = "Europe/Skopje"
    EUROPE_SOFIA = "Europe/Sofia"
    EUROPE_STOCKHOLM = "Europe/Stockholm"
    EUROPE_TALLINN = "Europe/Tallinn"
    EUROPE_TIRANE = "Europe/Tirane"
    EUROPE_TIRASPOL = "Europe/Tiraspol"
    EUROPE_ULYANOVSK = "Europe/Ulyanovsk"
    EUROPE_UZHGOROD = "Europe/Uzhgorod"
    EUROPE_VADUZ = "Europe/Vaduz"
    EUROPE_VATICAN = "Europe/Vatican"
    EUROPE_VIENNA = "Europe/Vienna"
    EUROPE_VILNIUS = "Europe/Vilnius"
    EUROPE_VOLGOGRAD = "Europe/Volgograd"
    EUROPE_WARSAW = "Europe/Warsaw"
    EUROPE_ZAGREB = "Europe/Zagreb"
    EUROPE_ZAPOROZHYE = "Europe/Zaporozhye"
    EUROPE_ZURICH = "Europe/Zurich"
    GB = "GB"
    GB_EIRE = "GB-Eire"
    GMT = "GMT"
    GMT_PLUS_0 = "GMT+0"
    GMT_MINUS_0 = "GMT-0"
    GMT0 = "GMT0"
    GREENWICH = "Greenwich"
    HST = "HST"
    HONGKONG = "Hongkong"
    ICELAND = "Iceland"
    INDIAN_ANTANANARIVO = "Indian/Antananarivo"
    INDIAN_CHAGOS = "Indian/Chagos"
    INDIAN_CHRISTMAS = "Indian/Christmas"
    INDIAN_COCOS = "Indian/Cocos"
    INDIAN_COMORO = "Indian/Comoro"
    INDIAN_KERGUELEN = "Indian/Kerguelen"
    INDIAN_MAHE = "Indian/Mahe"
    INDIAN_MALDIVES = "Indian/Maldives"
    INDIAN_MAURITIUS = "Indian/Mauritius"
    INDIAN_MAYOTTE = "Indian/Mayotte"
    INDIAN_REUNION = "Indian/Reunion"
    IRAN = "Iran"
    ISRAEL = "Israel"
    JAMAICA = "Jamaica"
    JAPAN = "Japan"
    KWAJALEIN = "Kwajalein"
    LIBYA = "Libya"
    MET = "MET"
    MST = "MST"
    MST7MDT = "MST7MDT"
    MEXICO_BAJA_NORTE = "Mexico/BajaNorte"
    MEXICO_BAJA_SUR = "Mexico/BajaSur"
    MEXICO_GENERAL = "Mexico/General"
    NZ = "NZ"
    NZ_CHAT = "NZ-CHAT"
    NAVAJO = "Navajo"
    PRC = "PRC"
    PST8PDT = "PST8PDT"
    PACIFIC_APIA = "Pacific/Apia"
    PACIFIC_AUCKLAND = "Pacific/Auckland"
    PACIFIC_BOUGAINVILLE = "Pacific/Bougainville"
    PACIFIC_CHATHAM = "Pacific/Chatham"
    PACIFIC_CHUUK = "Pacific/Chuuk"
    PACIFIC_EASTER = "Pacific/Easter"
    PACIFIC_EFATE = "Pacific/Efate"
    PACIFIC_ENDERBURY = "Pacific/Enderbury"
    PACIFIC_FAKAOFO = "Pacific/Fakaofo"
    PACIFIC_FIJI = "Pacific/Fiji"
    PACIFIC_FUNAFUTI = "Pacific/Funafuti"
    PACIFIC_GALAPAGOS = "Pacific/Galapagos"
    PACIFIC_GAMBIER = "Pacific/Gambier"
    PACIFIC_GUADALCANAL = "Pacific/Guadalcanal"
    PACIFIC_GUAM = "Pacific/Guam"
    PACIFIC_HONOLULU = "Pacific/Honolulu"
    PACIFIC_JOHNSTON = "Pacific/Johnston"
    PACIFIC_KANTON = "Pacific/Kanton"
    PACIFIC_KIRITIMATI = "Pacific/Kiritimati"
    PACIFIC_KOSRAE = "Pacific/Kosrae"
    PACIFIC_KWAJALEIN = "Pacific/Kwajalein"
    PACIFIC_MAJURO = "Pacific/Majuro"
    PACIFIC_MARQUESAS = "Pacific/Marquesas"
    PACIFIC_MIDWAY = "Pacific/Midway"
    PACIFIC_NAURU = "Pacific/Nauru"
    PACIFIC_NIUE = "Pacific/Niue"
    PACIFIC_NORFOLK = "Pacific/Norfolk"
    PACIFIC_NOUMEA = "Pacific/Noumea"
    PACIFIC_PAGO_PAGO = "Pacific/Pago_Pago"
    PACIFIC_PALAU = "Pacific/Palau"
    PACIFIC_PITCAIRN = "Pacific/Pitcairn"
    PACIFIC_POHNPEI = "Pacific/Pohnpei"
    PACIFIC_PONAPE = "Pacific/Ponape"
    PACIFIC_PORT_MORESBY = "Pacific/Port_Moresby"
    PACIFIC_RAROTONGA = "Pacific/Rarotonga"
    PACIFIC_SAIPAN = "Pacific/Saipan"
    PACIFIC_SAMOA = "Pacific/Samoa"
    PACIFIC_TAHITI = "Pacific/Tahiti"
    PACIFIC_TARAWA = "Pacific/Tarawa"
    PACIFIC_TONGATAPU = "Pacific/Tongatapu"
    PACIFIC_TRUK = "Pacific/Truk"
    PACIFIC_WAKE = "Pacific/Wake"
    PACIFIC_WALLIS = "Pacific/Wallis"
    PACIFIC_YAP = "Pacific/Yap"
    POLAND = "Poland"
    PORTUGAL = "Portugal"
    ROC = "ROC"
    ROK = "ROK"
    SINGAPORE = "Singapore"
    TURKEY = "Turkey"
    UCT = "UCT"
    US_ALASKA = "US/Alaska"
    US_ALEUTIAN = "US/Aleutian"
    US_ARIZONA = "US/Arizona"
    US_CENTRAL = "US/Central"
    US_EAST_INDIANA = "US/East-Indiana"
    US_EASTERN = "US/Eastern"
    US_HAWAII = "US/Hawaii"
    US_INDIANA_STARKE = "US/Indiana-Starke"
    US_MICHIGAN = "US/Michigan"
    US_MOUNTAIN = "US/Mountain"
    US_PACIFIC = "US/Pacific"
    US_SAMOA = "US/Samoa"
    UTC = "UTC"
    UNIVERSAL = "Universal"
    W_SU = "W-SU"
    WET = "WET"
    ZULU = "Zulu"


class TypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of TypeEnum."""

    STRING = "String"
    FLOAT = "Float"
    DATE_TIME = "DateTime"
    INTEGER = "Integer"
    OBJECT = "Object"
    DATE = "Date"
    BOOL = "Bool"
    STRING_ARRAY = "StringArray"
    FLOAT_ARRAY = "FloatArray"
    DATE_ARRAY = "DateArray"
    OBJECT_ARRAY = "ObjectArray"
    INVALID_FIELD = "InvalidField"


class UnderlyingTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The type of the underlying asset."""

    FX = "Fx"
    BOND = "Bond"
    IRS = "Irs"
    COMMODITY = "Commodity"
    EQUITY = "Equity"
    BOND_FUTURE = "BondFuture"


class UnitEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The unit that describes the value."""

    ABSOLUTE = "Absolute"
    """The value is expressed in absolute units."""
    BASIS_POINT = "BasisPoint"
    """The value is expressed in basis points (scaled by 10,000)."""
    PERCENTAGE = "Percentage"
    """The value is expressed in percentages (scaled by 100)."""


class Visible(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of Visible."""

    Y = "Y"
    U = "U"
    N = "N"


class VolatilityAdjustmentTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of VolatilityAdjustmentTypeEnum."""

    CONSTANT_CAP = "ConstantCap"
    CONSTANT_CAPLET = "ConstantCaplet"
    NORMALIZED_CAP = "NormalizedCap"
    NORMALIZED_CAPLET = "NormalizedCaplet"
    SHIFTED_CAP = "ShiftedCap"


class VolatilityTermStructureTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of VolatilityTermStructureTypeEnum."""

    HISTORICAL = "Historical"
    IMPLIED = "Implied"


class VolatilityTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The type of the volatility."""

    DEFAULT = "Default"
    """If the Volatility Surface service fails to return a volatility, its default value is used."""
    IMPLIED = "Implied"
    """The volatility anticipated for the underlying asset for the remaining life of the option
    (implied by the option premium). It is available only for listed options.
    """
    SURFACE = "Surface"
    """The value is derived from the Volatility Surface service."""
    HISTORICAL = "Historical"
    """The volatility of the underlying asset over the past period."""


class VolModelTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """An object defining the different type of model used to represent the volatilities."""

    NORMAL = "Normal"
    LOG_NORMAL = "LogNormal"


class WeekDay(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The day of the week. Day names written in full."""

    MONDAY = "Monday"
    TUESDAY = "Tuesday"
    WEDNESDAY = "Wednesday"
    THURSDAY = "Thursday"
    FRIDAY = "Friday"
    SATURDAY = "Saturday"
    SUNDAY = "Sunday"


class XAxisEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of XAxisEnum."""

    DATE = "Date"
    DELTA = "Delta"
    EXPIRY = "Expiry"
    MONEYNESS = "Moneyness"
    STRIKE = "Strike"
    TENOR = "Tenor"


class YAxisEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of YAxisEnum."""

    DATE = "Date"
    DELTA = "Delta"
    EXPIRY = "Expiry"
    MONEYNESS = "Moneyness"
    STRIKE = "Strike"
    TENOR = "Tenor"


class YbRestCurveType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of YbRestCurveType."""

    GVT = "GVT"
    GVT_TSYM = "GVT_TSYM"
    GVT_TSYM_MUNI = "GVT_TSYM_MUNI"
    GVT_AGN = "GVT_AGN"
    GVT_MUNI = "GVT_MUNI"
    GVT_BUND = "GVT_BUND"
    SWAP = "SWAP"
    SWAP_RFR = "SWAP_RFR"
    SWAP_MUNI = "SWAP_MUNI"
    SWAP_LIB6M = "SWAP_LIB6M"


class YbRestFrequency(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of YbRestFrequency."""

    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    YEARLY = "YEARLY"


class YearBasisEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The number of days used to represent a year."""

    YB_252 = "YB_252"
    """252 days in a year, the conventional number of days in a year when taking only working days
    into account.
    """
    YB_360 = "YB_360"
    """360 days in a year."""
    YB_364 = "YB_364"
    """364 days in a year."""
    YB_365 = "YB_365"
    """365 days in a year."""
    YB_36525 = "YB_36525"
    """365.25 days in a year."""
    YB_366 = "YB_366"
    """366 days in a year."""
    YB_ACTUAL = "YB_Actual"
    """365 days or 366 days in a year, taking leap years into account."""


class YieldRoundingEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of YieldRoundingEnum."""

    ZERO = "Zero"
    ONE = "One"
    TWO = "Two"
    THREE = "Three"
    FOUR = "Four"
    FIVE = "Five"
    SIX = "Six"
    SEVEN = "Seven"
    EIGHT = "Eight"
    DEFAULT = "Default"
    UNROUNDED = "Unrounded"


class YieldRoundingTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of YieldRoundingTypeEnum."""

    NEAR = "Near"
    UP = "Up"
    DOWN = "Down"
    FLOOR = "Floor"
    CEIL = "Ceil"
    FACE_NEAR = "FaceNear"
    FACE_DOWN = "FaceDown"
    FACE_UP = "FaceUp"
    DEFAULT = "Default"


class YieldTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of YieldTypeEnum."""

    NATIVE = "Native"
    US_GOVT = "UsGovt"
    US_T_BILLS = "UsTBills"
    ISMA = "Isma"
    EUROLAND = "Euroland"
    DISCOUNT_ACTUAL_360 = "Discount_Actual_360"
    DISCOUNT_ACTUAL_365 = "Discount_Actual_365"
    MONEY_MARKET_ACTUAL_360 = "MoneyMarket_Actual_360"
    MONEY_MARKET_ACTUAL_365 = "MoneyMarket_Actual_365"
    MONEY_MARKET_ACTUAL_ACTUAL = "MoneyMarket_Actual_Actual"
    BOND_ACTUAL_364 = "Bond_Actual_364"
    JAPANESE_SIMPLE = "Japanese_Simple"
    JAPANESE_COMPOUNDED = "Japanese_Compounded"
    MOOSMUELLER = "Moosmueller"
    BRAESS_FANGMEYER = "Braess_Fangmeyer"
    WEEKEND = "Weekend"
    TURKISH_COMPOUNDED = "TurkishCompounded"
    ANNUAL_EQUIVALENT = "Annual_Equivalent"
    SEMIANNUAL_EQUIVALENT = "Semiannual_Equivalent"
    QUARTERLY_EQUIVALENT = "Quarterly_Equivalent"
    MARKET_REFERENCE = "MarketReference"


class ZAxisEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of ZAxisEnum."""

    DATE = "Date"
    DELTA = "Delta"
    EXPIRY = "Expiry"
    MONEYNESS = "Moneyness"
    STRIKE = "Strike"
    TENOR = "Tenor"


class ZcTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """An enum that describes the type of the value provided in the zero coupon curve."""

    RATE = "Rate"
    """The zero coupon curve values are provided as rates."""
    DISCOUNT_FACTOR = "DiscountFactor"
    """The zero coupon curve values are provided as discount factor."""
