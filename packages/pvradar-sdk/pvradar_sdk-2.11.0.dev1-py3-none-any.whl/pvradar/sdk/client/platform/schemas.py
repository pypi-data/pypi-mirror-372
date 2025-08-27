from typing import Any, Literal, NotRequired, TypedDict

# Legacy Powermax types


class ILocation(TypedDict):
    lat: float
    lon: float


class IProjectManifest(TypedDict):
    id: str
    countryAlpha2: NotRequired[str]
    countryName: NotRequired[str]
    currency: NotRequired[str]
    location: ILocation
    name: str
    orgId: str
    ownerUsername: str
    productionSource: str
    projectGoal: str
    soilingOptions: NotRequired[Any]
    #
    # engine integration
    default_tz: NotRequired[str]
    interval: NotRequired[str]


class IPlantRevenueParams(TypedDict):
    ppaPriceMW: NotRequired[float]
    energyPriceHistoryResource: NotRequired[str]


class ICommodityPrices(TypedDict):
    labor: NotRequired[float]  # EUR/FTE year
    fuel: NotRequired[float]  # EUR/liter
    water: NotRequired[float]  # EUR/m^3
    inflationRate: NotRequired[float]
    isInflationApplied: bool


class IPlantFinParams(TypedDict):
    finLifetime: int
    currency: str  # Replace `str` with an Enum or a specific type if `Currency` is defined elsewhere
    discountRate: float
    defaultInflationRate: float
    revenue: IPlantRevenueParams
    commodityPrices: ICommodityPrices


AssemblyType = Literal[
    'vtable',
    'timed-vtable',
    'record',
    'value',
    'free',
    'timed-vtable-list',
    'tagged-digest',
]

AssemblyName = Literal[
    'project-manifest',
    'variant-summary',
    # --------------------------------------
    'pvsyst-prj',
    'pvsyst-vc',
    'pvsyst-vc-hourly',
    'pvsyst-vc-monthly',
    'pvsyst-met',
    'pvsyst-met-hourly',
    'pvsyst-pan',  # requires article in dims
    'pvsyst-ond',  # requires article in dims
    'sam-pvwatts-params',  # params used for sam (without solar resource)
    # --------------------------------------
    # journey definition
    'journey-route-base',
    'journey-route-transform',
    'journey-route-transform-cleaning',
    'journey-route',
    'journey-route-optimized',
    'journey-route-solved',
    # --------------------------------------
    # additional input
    'precip-history-daily',
    'cleaning-precip-history-daily',  # precip but only containing values that clean
    'soiling-profile-external',
    # --------------------------------------
    # albedo
    'albedo-history',
    'albedo-history-daily',
    'albedo-history-collapsed-daily',
    'natural-albedo-monthly',
    'albedo-enhancer-soiling-profile',
    'albedo-enhancer-mean-soiling-monthly',
    'albedo-enhancer-provider-cashflow',
    'albedo-enhancer-client-cashflow',
    'albedo-enhancer-provider-cashflow-cumulative',
    'albedo-soiled-enhancer-monthly',
    'albedo-enhancer-summary',
    # --------------------------------------
    # input funnel
    'tmy-hourly',
    'tmy-hourly-tmy3',
    'tmy-summary',
    'technical-params-source',
    'technical-params-base',  # as defined by user for the variant
    'technical-params',  # as defined in permutation
    'technical-summary',  # human-friendly representation of tech. params
    'design',
    'layout-evaluation',
    'prod-profile-source',
    'prod-profile-source-daily',
    'prod-profile-source-summary',
    'loss-profile-source',
    'prod-profile-source-united',
    'poa-profile-batch-source',
    'poa-profile-batch-base',
    'grid-limit-history',
    'grid-limit-profile',  # hourly grid limit for given yearIndex
    # --------------------------------------
    # poa funnel
    'poa-profile-batch',
    'precip-profile-daily',
    'bifacial-profile-batch',
    'natural-cleaning-profile',
    # --------------------------------------
    # soiling and cleaning
    'soiling-profile-base',
    'soiling-profile-natural',
    'soiling-profile-batch',
    'soiling-profile',  # same as batch but just subarray 0
    'soiling-profile-daily',  # aggregation of just subarray 0
    'soiling-profile-monthly',  # aggregation of just subarray 0
    'cleaning-profile-natural',
    'cleaning-profile-batch',
    'bifacial-profile-batch',
    'soiling-manifest',
    'soiling-recipe-envelope',  # requires article in request
    'soiling-deposition-history-daily',  # requires article in request
    'soiling-deposition-history-combined',  # all particles used in the model in one table
    'soiling-deposition-profile',  # hourly, contains all particle, done for specific yearIndex
    'soiling-history-monthly',  # average SL for each month over 20 years (used for boxplot)
    'external-poa-profile',  # time series of POA provided externally (potentially for multiple subarrays)
    'soiling-diversity',  # soiling for all available data calculated as continuous time series
    'soiling-forecast',  # soiling for entire lifetime
    'soiling-lifetime-summary',
    'cleaning-profile-natural',
    'cleaning-profile-batch',
    'cleaning-lifetime-summary',
    # --------------------------------------
    # energy funnel
    'loss-profile',
    'inv-profile-batch',
    'inv-profile-combined',
    'prod-profile',
    'prod-profile-daily',
    'prod-profile-summary',
    'prod-loss-rough-daily',
    'prod-poa-profile-monthly',  # table combining total POA and total production
    # --------------------------------------
    # breakdown funnel
    'prod-breakdown',
    'prod-breakdown-daily',
    'prod-breakdown-summary',
    'journey-breakdown',
    'journey-breakdown-daily',
    'journey-breakdown-flat',
    'journey-breakdown-flat-daily',
    'journey-breakdown-flat-summary',
    'journey-technical-summary',
    'journey-breakdown-flow',  # a table consisting of journey-breakdown-flat-summary for each year
    # --------------------------------------
    # financial funnel
    'plant-fin-params',
    'energy-price-history',  # hourly prices
    'energy-price-profile',  # hourly prices for given yearIndex
    'strategy-packages-solved',  # map: strategy name -> solved package
    'journey-revenue-tagged-digest',
    'journey-cost-tagged-digest',
    'fin-digest-flow',
    'journey-cashflow',
    'journey-cashflow-summary',
    'journey-kpi-summary',
    'journey-fin-details',
    'cashflow-cleaning',
    # --------------------------------------
    # risk assessment
    'loss-diversity-monthly',
    # --------------------------------------
    # reflection assemblies
    'optimization-param-sweep',
    'optimization-history',
    'optimization-progress',
    'computation-progress',
    'journey-optimization-summary',
    # --------------------------------------
    # forms
    'wizard-form-project',
    'wizard-form-basic-design',
    'wizard-form-layout',
    'wizard-form-soiling',
    'wizard-form-albedo',
    'wizard-form-albedo-enhancer-offer',
    'wizard-form-cleaning-example',
    'wizard-form-fin',
    'wizard-form-packages',
    'wizard-form-snow',
    'step-forms',
]


class IDimRecord(TypedDict):
    absYear: NotRequired[int]
    yearIndex: NotRequired[int]
    step: NotRequired[int]
    viewModelContext: NotRequired[str]
    groupBy: NotRequired[str]

    article: NotRequired[str]  # names, models, and IDs of equipment items
    bifacialityFactor: NotRequired[float]
    soilingModel: NotRequired[str]
    rainSample: NotRequired[str]

    bifacialityScale: NotRequired[float]
    soilingScale: NotRequired[float]
    cleaningScale: NotRequired[float]


class IAssemblyBadge(TypedDict):
    name: AssemblyName
    assemblyType: AssemblyType
    conveyorType: str
    dims: NotRequired[IDimRecord]


class IAssembly(TypedDict):
    badge: IAssemblyBadge
    subject: Any
