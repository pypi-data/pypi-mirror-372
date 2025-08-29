from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional, Union

from pydantic import AnyUrl, BaseModel, Field, confloat, constr

from . import enums, geojson


class IcarMetaDataType(BaseModel):
    """
    Generic meta data on this event
    """

    source: str = Field(
        ...,
        description="Source where data is retrieved from. URI  or reverse DNS that identifies the source system.",
    )
    sourceId: Optional[str] = Field(
        None,
        description="Unique Id within Source (e.g. UUID, IRI, URI, or composite ID if needed) for the resource in the original source system. \n Systems should generate (if needed), store, and return sourceId if at all possible.\nICAR ADE working group intend to make use of metadata, source and sourceId mandatory in the next major release (2.0).",
    )
    isDeleted: Optional[bool] = Field(
        None,
        description="Boolean value indicating if this resource has been deleted in the source system.",
    )
    modified: datetime = Field(
        ...,
        description="RFC3339 UTC date/time of last modification (see https://ijmacd.github.io/rfc3339-iso8601/ for format guidance).",
    )
    created: Optional[datetime] = Field(
        None,
        description="RFC3339 UTC date/time of creation (see https://ijmacd.github.io/rfc3339-iso8601/ for format guidance).",
    )
    creator: Optional[str] = Field(
        None, description="Person or organisation who created the object"
    )
    validFrom: Optional[datetime] = Field(
        None,
        description="RFC3339 UTC start of period when the resource is valid (see https://ijmacd.github.io/rfc3339-iso8601/ for format guidance).",
    )
    validTo: Optional[datetime] = Field(
        None,
        description="RFC3339 UTC end of the period when the resoure is valid (see https://ijmacd.github.io/rfc3339-iso8601/ for format guidance).",
    )


class IcarIdentifierType(BaseModel):
    """
    Identifies a resource.
    """

    id: str = Field(
        ...,
        description="A unique identification for the resource issued under the auspices of the scheme.",
    )
    scheme: str = Field(
        ...,
        description="The identifier (in reverse domain format) of an official scheme that manages unique identifiers.",
    )


class IcarLocationIdentifierType(IcarIdentifierType):
    """
    Location identifier based on a scheme and ID.
    """


class IcarFeedIdentifierType(IcarIdentifierType):
    """
    Provides a scheme + identifier mechanism for feed types (see location-scheme.md for the icar list for scheme fao.org).).
    """


class IcarPropertyIdentifierType(IcarIdentifierType):
    """
    Provides a scheme + identifier mechanism for feed properties (see location-scheme.md for the icar list for scheme icar.org).
    """


class IcarFeedPropertyType(BaseModel):
    """
    property of the feed.
    """

    propertyIdentifier: Optional[IcarPropertyIdentifierType] = Field(
        None, description="identifies the property of the feed"
    )
    value: Optional[float] = Field(None, description="the value of the property.")
    units: Optional[enums.UncefactMassUnitsType] = Field(
        None,
        description="Units specified in UN/CEFACT 3-letter form. Default if not specified is KGM.",
    )
    method: Optional[enums.IcarMethodType] = Field(
        None, description="The method to come to the value of the property"
    )
    name: Optional[str] = Field(
        None, description="name of the property (used on the location)."
    )


class IcarFeedsInRationType(BaseModel):
    """
    Feeds that are added to a specific ration.
    """

    feedId: Optional[IcarFeedIdentifierType] = Field(
        None, description="identifies the feed"
    )
    percentage: Optional[float] = Field(
        None, description="the percentage of the feed in the ration."
    )


class IcarTraitLabelIdentifierType(IcarIdentifierType):
    """
    Trait identifier based on a scheme and ID.
    """


class IcarAnimalIdentifierType(IcarIdentifierType):
    """
    Identifies an animal using a scheme and ID.
    """


class IcarFeedDurationType(BaseModel):
    """
    The length in time of the feeding
    """

    unitCode: Optional[enums.UnitCode] = Field(
        None, description="UN/CEFACT Common Code for Units of Measurement."
    )
    value: Optional[float] = Field(
        None, description="The duration of the feeding in the units specified."
    )


class IcarFeedQuantityType(BaseModel):
    """
    The amount of feed
    """

    unitCode: enums.UncefactMassUnitsType = Field(
        ...,
        description="Units specified in UN/CEFACT 3-letter form. Default if not specified is KGM.",
    )
    value: float = Field(..., description="The feed quantity in the units specified.")


class IcarCostType(BaseModel):
    """
    The amount of costs
    """

    currency: str = Field(
        ...,
        description="The currency of the cost expressed using the ISO 4217 3-character code (such as AUD, GBP, USD, EUR).",
    )
    value: float = Field(..., description="The costs in the units specified.")


class IcarConsumedFeedType(BaseModel):
    """
    gives the consumed feed and the amount the animal/group was entitled to. Amounts are real weights
    """

    feedId: IcarFeedIdentifierType = Field(
        ..., description="The identifier for the feed consumed"
    )
    entitlement: Optional[IcarFeedQuantityType] = Field(
        None, description="The amount of feed the animal/group was entitled to receive"
    )
    delivered: Optional[IcarFeedQuantityType] = Field(
        None,
        description="The amount of feed the animal/group received. If not present, it can be assumed that the delivered will be equal to entitlement",
    )
    feedConsumption: Optional[IcarFeedQuantityType] = Field(
        None, description="The amount of feed the animal/group has consumed"
    )
    dryMatterPercentage: Optional[float] = Field(
        None,
        description="The dry matter content of the feed provided or consumed, expressed as a percentage.",
    )
    totalCost: Optional[IcarCostType] = Field(
        None,
        description="Total cost applied to this feeding. Based on the delivered or entitled amount",
    )


class IcarConsumedRationType(BaseModel):
    """
    Gives the consumed amount of a mixed ration, and the amount the animal/group was entitled to. Amounts are real weights.
    """

    rationId: str = Field(..., description="The identifier for the ration consumed")
    entitlement: Optional[IcarFeedQuantityType] = Field(
        None, description="The amount of feed the animal/group was entitled to receive"
    )
    delivered: Optional[IcarFeedQuantityType] = Field(
        None,
        description="The amount of feed the animal/group received. If not present, it can be assumed that the delivered will be equal to entitlement",
    )
    feedConsumption: Optional[IcarFeedQuantityType] = Field(
        None, description="The amount of feed the animal/group has consumed"
    )
    dryMatterPercentage: Optional[float] = Field(
        None,
        description="The dry matter content of the ration provided or consumed, expressed as a percentage.",
    )
    totalCost: Optional[IcarCostType] = Field(
        None,
        description="Total cost applied to this feeding. Based on the delivered or entitled amount",
    )


class IcarResourceReferenceType(BaseModel):
    """
    Defines a reference to another resource.
    """

    field_context: Optional[str] = Field(
        None,
        alias="@context",
        description="Deprecated. Tells us the type of the referenced resource object (eg. icarAnimalCore).",
    )
    field_id: Optional[AnyUrl] = Field(
        None,
        alias="@id",
        description="Deprecated - use href and identifier. Uniform resource idendentifier (URI) of the referenced resource.",
    )
    field_type: Optional[str] = Field(
        None,
        alias="@type",
        description="Deprecated - use reltype. Specifies whether this is a single resource Link or a Collection.",
    )
    identifier: Optional[IcarIdentifierType] = Field(
        None, description="Provides the identifier of the referenced resource."
    )
    reltype: Optional[str] = Field(
        None,
        description="Defines the relationship between the current resource and the referenced resource. Defined in well-known/relationshipCatalog.md",
    )
    href: Optional[AnyUrl] = Field(
        None, description="Where provided, this is the URI to the referenced resource."
    )


class IcarDeviceRegistrationIdentifierType(IcarIdentifierType):
    """
    A device registration scheme and ID that identifies a registered device. The primary scheme used should be `org.icar`.
    """


class IcarDeviceReferenceType(IcarResourceReferenceType):
    """
    Device reference details.
    """

    model: Optional[str] = Field(
        None,
        description="ICAR registered device model, which represents manufacturer, model, hardware and software versions.",
    )
    serial: Optional[str] = Field(
        None, description="Optionally, the serial number of the device."
    )
    manufacturerName: Optional[str] = Field(
        None,
        description="The manufacturer of the device. This is called `manufacturerName` to distinguish it from the manufacturer-specific parameters in icarDevice.",
    )
    registration: Optional[IcarDeviceRegistrationIdentifierType] = Field(
        None,
        description="A registration identifier for the device (most devices should eventually have a registration issued by `org.icar` or other entity).",
    )


class IcarRecommendedFeedType(BaseModel):
    """
    Gives the recommendation to be fed to an animal or group of animals of a certain feed.
    """

    feedId: Optional[IcarFeedIdentifierType] = Field(
        None, description="The identifier for the feed recommended"
    )
    entitlement: Optional[IcarFeedQuantityType] = Field(
        None, description="The amount of feed the animal is recommended to reveive"
    )


class IcarRecommendedRationType(BaseModel):
    """
    Gives the recommendation to be fed to an animal or group of animals of a certain ration.
    """

    rationId: Optional[str] = Field(
        None, description="The identifier for the ration recommended"
    )
    entitlement: Optional[IcarFeedQuantityType] = Field(
        None,
        description="The amount of this ration the animal is recommended to receive",
    )


class IcarDeviceManufacturerType(BaseModel):
    """
    Describes the devices on a certain location.
    """

    id: str = Field(
        ...,
        description="Unique id of the manufacturer. Domain name/url --> lely.com, …",
    )
    deviceType: Optional[str] = Field(
        None,
        description="A device type registered within the database proposed by the Sensor Working Group. This could be a UUID but we prefer a meaningful string.",
    )
    deviceName: Optional[str] = Field(
        None, description="Name given to the device by the manufacturer."
    )
    deviceDescription: Optional[str] = Field(
        None, description="Description of the device by the manufacturer."
    )
    deviceConfiguration: Optional[str] = Field(
        None, description="Configuration of the device."
    )


class IcarProductIdentifierType(IcarIdentifierType):
    """
    Provides a scheme + identifier mechanism for product types.
    """


class IcarProductReferenceType(IcarResourceReferenceType):
    """
    Product Reference refers to a specific product. It is based on the generalised resource reference type.
    """

    identifiers: Optional[List[IcarProductIdentifierType]] = Field(
        None,
        description="An array of product identifiers. This allows a product to have multiple identifiers for manufacturers, distributors, official registrations, etc.",
    )
    family: enums.IcarProductFamilyType = Field(
        ..., description="The product family to which this product belongs."
    )
    name: Optional[str] = Field(None, description="The name of the product.")
    gtin: Optional[str] = Field(None, description="GS1 global trade item number.")
    unspc: Optional[str] = Field(
        None,
        description="UN service and product code (the code, not the accompanying description).",
    )


class IcarFeedReferenceType(IcarProductReferenceType):
    """
    Feed Reference defines a feed product.
    """

    category: Optional[enums.IcarFeedCategoryType] = Field(
        None, description="Defines the category of the feed product."
    )
    type: Optional[IcarFeedIdentifierType] = Field(
        None, description="The scheme + id identifying the type of feed."
    )


class IcarBreedIdentifierType(IcarIdentifierType):
    """
    Identifies a breed using a scheme and ID. Allows country or species-specific breeds that are a superset of the ICAR list.
    """


class IcarInventoryClassificationType(BaseModel):
    """
    This type is used to categorise animals by shared characteristics - so you can say the equivalent of 200 x 2-year-old in-calf Jersey heifers.
    """

    name: str = Field(
        ..., description="Human-readable name for this inventory grouping."
    )
    count: Optional[float] = Field(
        None,
        description="The count or number of animals in this inventory classification.",
    )
    species: enums.IcarAnimalSpecieType = Field(
        ..., description="The species of animals."
    )
    sex: Optional[enums.IcarAnimalGenderType] = Field(
        None, description="The sex of animals."
    )
    primaryBreed: Optional[IcarBreedIdentifierType] = Field(
        None, description="Primary breed defined using an identifier and scheme."
    )
    birthPeriod: Optional[
        constr(
            pattern=r"^(([0-9]{4})|([0-9]{4}-[0-1][0-9])|([0-9]{4}-[0-1][0-9]-[0-3][0-9](Z?)(/|--)[0-9]{4}-[0-1][0-9]-[0-3][0-9](Z?)))$"
        )
    ] = Field(
        None,
        description="The range of birth dates. Use YYYY (all one year), YYYY-MM (one month), or two RFC3339 date-times separated by / to represent a range.",
    )
    reproductiveStatus: Optional[enums.IcarAnimalReproductionStatusType] = Field(
        None, description="The reproductive/pregnancy status of animals."
    )
    lactationStatus: Optional[enums.IcarAnimalLactationStatusType] = Field(
        None, description="The lactation status of animals."
    )
    productionPurposes: Optional[List[enums.IcarProductionPurposeType]] = Field(
        None, description="Array of production purposes."
    )
    reference: Optional[str] = Field(
        None,
        description="An external reference (identifier or name) to further identify the group of animals.",
    )


class IcarAnimalSetReferenceType(IcarResourceReferenceType):
    """
    References an animal set through its unique ID in the source system, optionally also specifying its URL (@ID).
    """

    identifier: IcarIdentifierType = Field(
        ..., description="Provides the identifier of the referenced resource."
    )


class IcarDiagnosisIdentifierType(IcarIdentifierType):
    """
    Provides a scheme + identifier mechanism for diagnosis codes (e.g. VENOM or ICAR coding).
    """


class IcarPositionType(BaseModel):
    """
    The possible positions for treatment or diagnosis
    """

    position: Optional[enums.IcarPositionOnAnimalType] = Field(
        None,
        description="Position on the animal where the diagnosis or treatment occurred.",
    )


class IcarDiagnosisType(BaseModel):
    """
    Provides properties for a single animal health diagnosis.
    """

    id: Optional[str] = Field(None, description="Unique identifier for this diagnosis.")
    name: Optional[str] = Field(
        None, description="Name indicating the health condition diagnosed."
    )
    description: Optional[str] = Field(
        None, description="Description of the diagnosis or problem."
    )
    diagnosisCode: Optional[IcarDiagnosisIdentifierType] = Field(
        None,
        description="Descibes the scheme (eg venom or ICAR) and the code (ID) within that scheme.",
    )
    site: Optional[str] = Field(
        None, description="Site on the animal involved in the diagnosis or disease."
    )
    stage: Optional[enums.IcarDiagnosisStageType] = Field(
        None, description="Identifies the clinical stage of disease progression."
    )
    severity: Optional[enums.IcarDiagnosisSeverityType] = Field(
        None, description="Identifies the clinical severity of the problem."
    )
    severityScore: Optional[float] = Field(
        None,
        description="Clinical severity expressed as a numeric score for systems that record this.",
    )
    positions: Optional[List[IcarPositionType]] = Field(
        None, description="The positions to be treated"
    )


class IcarMedicineIdentifierType(IcarIdentifierType):
    """
    Identifies a medicine registraton with a national Scheme and a registered ID within that scheme.
    """


class IcarMedicineReferenceType(IcarProductReferenceType):
    """
    Provides basic details about a medicine and links to a medicine resource (if available).
    """

    approved: Optional[str] = Field(
        None,
        description="An indicator whether the medicine or remedy is an approved medicine",
    )
    registeredIdentifier: Optional[IcarMedicineIdentifierType] = Field(
        None,
        description="The registered identifier of the medicine expressed as a scheme and id.",
    )


class IcarMedicineBatchType(BaseModel):
    """
    Defines a batch of medicine or product with an expiry date.
    """

    identifier: Optional[str] = Field(None, description="The ID, batch or lot number.")
    expiryDate: Optional[datetime] = Field(
        None,
        description="The RFC3339 UTC expiry date of the batch (see https://ijmacd.github.io/rfc3339-iso8601/ for format guidance).",
    )


class IcarMedicineWithdrawalType(BaseModel):
    productType: Optional[enums.IcarWithdrawalProductType] = Field(
        None, description="Product or food item affected by this withdrawal."
    )
    endDate: Optional[datetime] = Field(
        None,
        description="RFC3339 UTC end date of withdrawal calculated based on treatment date and medicine rules (see https://ijmacd.github.io/rfc3339-iso8601/ for format guidance).",
    )
    market: Optional[str] = Field(
        None,
        description="The market to which the withdrawal applies, using a scheme such as au.gov.apvma.esi or au.gov.apvma.whp",
    )


class IcarMedicineDoseType(BaseModel):
    """
    Provides details of a dose of medicine or other product.
    """

    doseQuantity: Optional[float] = Field(
        None, description="Quantity of medicine or product administered."
    )
    doseUnits: Optional[enums.UncefactDoseUnitsType] = Field(
        None, description="Units of measurement in UN/CEFACT 3-letter form"
    )


class IcarMedicineCourseSummaryType(BaseModel):
    """
    Describes a course of treatment with total product, start and end dates
    """

    startDate: Optional[datetime] = Field(
        None,
        description="RFC3339 UTC start date of the treatment course (see https://ijmacd.github.io/rfc3339-iso8601/ for format guidance)",
    )
    endDate: Optional[datetime] = Field(
        None,
        description="RFC3339 UTC End date of the treatment course (see https://ijmacd.github.io/rfc3339-iso8601/ for format guidance)",
    )
    medicine: Optional[IcarMedicineReferenceType] = Field(
        None, description="Medicine details used in the course."
    )
    procedure: Optional[str] = Field(
        None, description="Medicine application method or non-medicine procedure."
    )
    site: Optional[str] = Field(
        None, description="Body site where the treatment or procedure was administered."
    )
    reasonForAdministration: Optional[str] = Field(
        None,
        description="This attribute can be used when medicine has been administered without a diagnosis",
    )
    totalDose: Optional[IcarMedicineDoseType] = Field(
        None, description="Total dose proposed or administered."
    )
    numberOfTreatments: Optional[float] = Field(
        None, description="The number of treatments included in the course."
    )
    treatmentInterval: Optional[int] = Field(
        None, description="The interval between treatments specified in HOURS."
    )
    batches: Optional[List[IcarMedicineBatchType]] = Field(
        None,
        description="Batches and expiry details of the medicine (there may be several).",
    )
    planOrActual: Optional[enums.PlanOrActual] = Field(
        None,
        description="Indicator showing if the attributes in the course Summary are actual information for the treatments or the plan",
    )
    withdrawals: Optional[List[IcarMedicineWithdrawalType]] = Field(
        None, description="Provides withholding details for the treatment administered"
    )


class IcarGroupSpecifierType(BaseModel):
    """
    definition of the groups for which statistics are provided. None of these are mandatory and can be used when convenient.
    """

    lactationNumberRangeMin: Optional[float] = Field(
        None, description="minimum number of lactations for the animals in the group."
    )
    lactationNumberRangeMax: Optional[float] = Field(
        None, description="maximum number of lactations for the animals in the group."
    )
    daysInMilkRangeMin: Optional[float] = Field(
        None, description="minimum number of days in milk for the animals in the group."
    )
    daysInMilkRangeMax: Optional[float] = Field(
        None, description="maximum number of days in milk for the animals in the group."
    )
    animalSetId: Optional[str] = Field(
        None, description="Unique identifier in the source system for this animal set."
    )


class IcarMetricType(IcarIdentifierType):
    """
    Identifies a metric using a scheme and ID. Allows country or species-specific metrics that are a superset of the ICAR list.
    """


class IcarStatisticsType(BaseModel):
    """
    The statistics that have been calculated.
    """

    metric: Optional[IcarMetricType] = Field(
        None,
        description="The metric code for a specific statistics. See https://github.com/adewg/ICAR/wiki/Schemes for more info",
    )
    unit: Optional[str] = Field(
        None,
        description="The unit of the metric. This must be appropriate to the metric and UN-CEFACT unit codes should be used where possible.",
    )
    aggregation: Optional[enums.IcarAggregationType] = Field(
        None, description="The aggregation applied to the metric."
    )
    value: Optional[float] = Field(None, description="The value of the metric.")


class IcarStatisticsGroupType(BaseModel):
    """
    definition of the groups for which statistics are provided
    """

    icarGroupType: Optional[enums.IcarGroupType] = None
    denominator: Optional[float] = Field(
        None, description="Number of animals in the group."
    )
    icarGroupSpecifier: Optional[List[IcarGroupSpecifierType]] = Field(
        None,
        description="A set of group specifiers that in combination define the animals in the group.",
    )
    statistics: Optional[List[IcarStatisticsType]] = Field(
        None, description="An array of statistics for this group."
    )


class IcarPositionObservationType(BaseModel):
    """
    This type may be included in a position observation event to identify either a named position (such as a barn or pen) or a geographic location.
    """

    positionName: Optional[str] = Field(
        None,
        description="The name of a location, such as a barn, pen, building, or field.",
    )
    site: Optional[str] = Field(
        None,
        description="Identifier for a sorting site (icarSortingSiteResource) for this position.",
    )
    geometry: Optional[
        Union[
            geojson.Geometry1,
            geojson.Geometry2,
            geojson.Geometry3,
            geojson.Geometry4,
            geojson.Geometry5,
            geojson.Geometry6,
        ]
    ] = Field(
        None,
        description="A GeoJSON geometry (such as a latitude/longitude point) that specifies the position.",
        title="GeoJSON Geometry",
    )


class IcarObservationStatisticsType(IcarStatisticsType):
    """
    Aggregated statistics for a animal behaviour or similar observation over a time period.
    """

    startDateTime: datetime = Field(
        ...,
        description="The start date/time of the aggregation period for this particular statistic.",
    )
    duration: enums.IcarDurationType = Field(
        ...,
        description="The type of period duration (e.g. 1D, 24H, 1W). A call may return statistics with different durations.",
    )
    isIncomplete: Optional[bool] = Field(
        None,
        description="This flag is present with the value true, when there is insufficient or incomplete data in the duration.",
    )


class IcarMilkDurationType(BaseModel):
    """
    The length in time of the milking
    """

    unitCode: Optional[enums.UnitCode] = Field(
        None, description="UN/CEFACT Common Code for Units of Measurement."
    )
    value: Optional[float] = None


class IcarMilkingMilkWeightType(BaseModel):
    """
    The amount of milk milked
    """

    unitCode: enums.UnitCode2 = Field(
        ..., description="UN/CEFACT Common Code for Units of Measurement."
    )
    value: float


class IcarQuarterMilkingSampleType(BaseModel):
    bottleIdentifierType: Optional[enums.IcarBottleIdentifierType] = Field(
        None,
        description="The type of bottle identifiertype according to ICAR_BottleIdentifierCode",
    )
    rackNumber: Optional[str] = Field(None, description="Number of the sample rack")
    bottlePosition: Optional[str] = Field(
        None, description="Position of the bottle in the sample rack"
    )
    bottleIdentifier: Optional[str] = Field(
        None, description="Bottle identifier read from barcode or RFID"
    )
    validSampleFillingIndicator: Optional[enums.IcarValidSampleFillingIndicatorType] = (
        Field(
            None,
            description="Indicator of valid sample filling according to ICAR_ValidSampleFillingIndicatorCode list",
        )
    )
    operator: Optional[str] = Field(
        None, description="The operator that took the sample"
    )


class IcarMilkCharacteristicsType(BaseModel):
    """
    Characteristics of the milk produced.
    """

    characteristic: str = Field(
        ...,
        description="Treat this field as an enum, with the list and units in https://github.com/adewg/ICAR/blob/ADE-1/enums/icarMilkCharacteristicCodeType.json.",
    )
    value: str = Field(..., description="the value of the characteristic measured")
    unit: Optional[str] = Field(
        None,
        description="Use the units for characteristics in https://github.com/adewg/ICAR/blob/ADE-1/enums/icarMilkCharacteristicCodeType.json. Only override when your units for a characteristic are different. Use UN/CEFACT codes.",
    )
    measuringDevice: Optional[str] = Field(
        None,
        description="a more readable device class ID that contains manufacturer, device, hardware and software versions in a way that is similar to the USB specification. This will need more investigation.",
    )


class IcarQuarterMilkingType(BaseModel):
    icarQuarterId: Optional[enums.IcarQuarterId] = Field(
        None, description="the unique id of the quarter milking"
    )
    xposition: Optional[float] = Field(
        None,
        description="Optional milking robot X position. Vendors may choose not to provide this.",
    )
    yposition: Optional[float] = Field(
        None,
        description="Optional milking robot Y position. Vendors may choose not to provide this.",
    )
    zposition: Optional[float] = Field(
        None,
        description="Optional milking robot Z position. Vendors may choose not to provide this.",
    )
    quarterMilkingDuration: Optional[IcarMilkDurationType] = None
    quarterMilkingWeight: Optional[IcarMilkingMilkWeightType] = None
    icarQuarterMilkingSample: Optional[List[IcarQuarterMilkingSampleType]] = None
    icarQuarterCharacteristics: Optional[List[IcarMilkCharacteristicsType]] = None


class IcarAnimalMilkingSampleType(BaseModel):
    bottleIdentifierType: Optional[enums.IcarBottleIdentifierType] = Field(
        None,
        description="The type of bottle identifiertype according to ICAR_BottleIdentifierCode",
    )
    rackNumber: Optional[str] = Field(None, description="Number of the sample rack")
    bottlePosition: Optional[str] = Field(
        None, description="Position of the bottle in the sample rack"
    )
    bottleIdentifier: Optional[str] = Field(
        None, description="Bottle identifier read from barcode or RFID"
    )
    validSampleFillingIndicator: Optional[enums.IcarValidSampleFillingIndicatorType] = (
        Field(
            None,
            description="Indicator of valid sample filling according to ICAR_ValidSampleFillingIndicatorCode list",
        )
    )
    operator: Optional[str] = Field(
        None, description="The operator that took the sample"
    )


class IcarMilkingPredictionType(BaseModel):
    """
    The amount of milk, fat and protein milked in a defined period of time
    """

    milkWeight: IcarMilkingMilkWeightType
    fatWeight: Optional[IcarMilkingMilkWeightType] = None
    proteinWeight: Optional[IcarMilkingMilkWeightType] = None
    hours: Optional[float] = Field(
        None,
        description="The number of hours in which the mentioned milk, fat and protein were produced. Most commonly used is a 24 hours production.",
    )


class IcarTraitAmountType(BaseModel):
    unitCode: enums.UnitCode3 = Field(
        ..., description="UN/CEFACT Common Code for Units of Measurement."
    )
    value: float


class IcarMilkRecordingMethodType(BaseModel):
    """
    milk recording method information.
    """

    milkRecordingProtocol: Optional[enums.IcarMilkRecordingProtocolType] = Field(
        None,
        description="Protocol A: Official MRO representative, Protocol B: Herd owner or its nominee, Protocol C: Official MRO representative or herd owner or its nominee.",
    )
    milkRecordingScheme: Optional[enums.IcarMilkRecordingSchemeType] = Field(
        None,
        description="all milkings at testday, all milkings in period, one milking at testday.",
    )
    milkingsPerDay: Optional[enums.IcarMilkingsPerDayType] = Field(
        None,
        description="1 per day, 2, 3, 4, Continuous Milkings (e.g. robotic milking).",
    )
    milkSamplingScheme: Optional[enums.IcarMilkSamplingSchemeType] = Field(
        None,
        description="proportional size sampling of all milkings, constant size sampling of all milkings, sampling of one milking at alternating moments (Alternative Sampling), sampling of one milking at the same moments (Corrected Sampling), sampling of one milking at changing moments (AMS), sampling of multiple milkings at changing moments (AMS).",
    )
    recordingInterval: Optional[float] = Field(
        None,
        description="A number in days of the interval between milk recordings. In case of e.g.4 weeks, use 30.",
    )
    milkSamplingMoment: Optional[enums.IcarMilkSamplingMomentType] = Field(
        None,
        description="Composite = composite sample from morning and evening, Morning, Evening.",
    )
    icarCertified: Optional[bool] = Field(
        None, description="indicates whether this information is certified by ICAR"
    )
    milkingType: Optional[enums.IcarMilkingType] = Field(
        None,
        description="Official milk result supplied by milk recording organisation, Measure by ICAR approved equipment, Measure by not approved equipment",
    )


class IcarMassMeasureType(BaseModel):
    """
    Defines a mass or weight measurement type that can be used in events or other resources.
    """

    measurement: Optional[confloat(ge=0.0)] = Field(
        None,
        description="The weight observation, in the units specified (usually kilograms).",
    )
    units: Optional[enums.UncefactMassUnitsType] = Field(
        None,
        description="Units specified in UN/CEFACT 3-letter form. Default if not specified is KGM.",
    )
    method: Optional[enums.IcarWeightMethodType] = Field(
        None,
        description="The method of observation. Loadcell is the default if not specified.",
    )
    resolution: Optional[float] = Field(
        None,
        description="The smallest measurement difference that can be discriminated given the current device settings. Specified in Units, for instance 0.5 (kilograms).",
    )


class IcarIndividualWeightType(BaseModel):
    """
    The Animal-Weight entity records a liveweight for an individual animal in a Group Weight. Either animal or weight may be null.
    """

    animal: Optional[IcarAnimalIdentifierType] = Field(
        None, description="Unique animal scheme and identifier combination."
    )
    weight: Optional[float] = Field(None, description="The weight measurement")


class IcarBVBaseIdentifierType(IcarIdentifierType):
    """
    Breeding value base identifier based on a scheme and ID.
    """


class IcarBreedingValueType(BaseModel):
    traitLabel: Optional[IcarTraitLabelIdentifierType] = Field(
        None,
        description="The scheme and id of the trait for which a breeding value is calculated",
    )
    calculationType: Optional[enums.IcarBreedingValueCalculationType] = Field(
        None,
        description="Indicates the calculation method/type for the breeding value.",
    )
    value: Optional[float] = Field(None, description="The breeding value.")
    reliability: Optional[float] = Field(
        None, description="The reliability of the breeding value"
    )
    resolution: Optional[float] = Field(
        None,
        description="The smallest difference that is relevant for this breeding value (to guide display). To assist in the interpretation of floating point values.",
    )


class IcarConformationScoreType(BaseModel):
    """
    conformation score
    """

    traitGroup: Optional[enums.IcarConformationTraitGroupType] = Field(
        None,
        description="Defines whether the trait is a composite trait or a linear trait.",
    )
    score: float = Field(
        ...,
        description="Conformation score with values of 1 to 9 numeric in case of linear traits and for composites in most cases between 50 and 99",
    )
    traitScored: enums.IcarConformationTraitType = Field(
        ...,
        description="Scored conformation trait type according ICAR guidelines. See https://www.icar.org/Guidelines/05-Conformation-Recording.pdf",
    )
    method: Optional[enums.IcarConformationScoringMethodType] = Field(
        None, description="Method of conformation scoring"
    )
    device: Optional[IcarDeviceReferenceType] = Field(
        None,
        description="Optional information about the device used for the automated scoring.",
    )


class Fraction(BaseModel):
    breed: Optional[IcarBreedIdentifierType] = Field(
        None, description="The breed for this breed fraction using a scheme and id."
    )
    fraction: Optional[float] = Field(
        None, description="The proportion of the denominator that this breed comprises."
    )


class IcarBreedFractionsType(BaseModel):
    """
    Defines the breeds of the animal by fraction expressed as a denominator and, for each breed, a numerator.
    """

    denominator: int = Field(
        ...,
        description="The denominator of breed fractions - for instance 16, 64, or 100.",
    )
    fractions: Optional[List[Fraction]] = Field(
        None, description="The numerators of breed fractions for each breed proportion."
    )


class IcarCoatColorIdentifierType(IcarIdentifierType):
    """
    Coat color identifier based on a scheme and Id.
    """


class IcarParentageType(BaseModel):
    """
    Use this type to define a parent of an animal.
    """

    parentOf: IcarAnimalIdentifierType = Field(
        ...,
        description="References the child of this parent (allowing you to build multi-generation pedigrees).",
    )
    gender: enums.IcarAnimalGenderType = Field(
        ...,
        description="Specifies Male or Female gender so you can recognise Sire or Dam.",
    )
    relation: Optional[enums.IcarAnimalRelationType] = Field(
        None,
        description="Identifies type of parent: Genetic (default), Recipient, Adoptive (Foster/Rearing).",
    )
    identifier: IcarAnimalIdentifierType = Field(
        ..., description="Unique animal scheme and identifier combination."
    )
    officialName: Optional[str] = Field(None, description="Official herdbook name.")


class PostalAddress(BaseModel):
    """
    An address object from schema.org (see https://schema.org/PostalAddress).
    """

    addressCountry: Optional[str] = Field(
        None,
        description="The country. For example, USA. You can also provide the two-letter ISO 3166-1 alpha-2 country code.",
    )
    addressLocality: Optional[str] = Field(
        None,
        description="The locality in which the street address is, and which is in the region. For example, Mountain View.",
    )
    addressRegion: Optional[str] = Field(
        None,
        description="The region in which the locality is, and which is in the country. For example, California or another appropriate first-level Administrative division",
    )
    postOfficeBoxNumber: Optional[str] = Field(
        None, description="The post office box number for PO box addresses."
    )
    postalCode: Optional[str] = Field(
        None, description="The postal code. For example, 94043."
    )
    streetAddress: Optional[str] = Field(
        None, description="The street address. For example, 1600 Amphitheatre Pkwy."
    )


class IcarOrganizationIdentityType(BaseModel):
    """
    The identity of an organization in livestock supply chains. Based on a minimal set of identifiers from schema.org/organization.
    """

    name: str = Field(..., description="Name of the organisation")
    leiCode: Optional[str] = Field(
        None,
        description="An organization identifier that uniquely identifies a legal entity as defined in ISO 17442.",
    )
    globalLocationNumber: Optional[str] = Field(
        None,
        description="The Global Location Number (GLN, sometimes also referred to as International Location Number or ILN) of the respective organization, person, or place. The GLN is a 13-digit number used to identify parties and physical locations.",
    )
    uri: Optional[AnyUrl] = Field(
        None,
        description="A uniform resource identifier that is the unique reference or for this organisation, such as its web site.",
    )


class IcarOrganizationIdentifierType(IcarIdentifierType):
    """
    Scheme and identifier based mechanism for identifying organisations, including registered establishments and scheme memberships.
    """


class IcarOrganizationType(IcarOrganizationIdentityType):
    """
    Details for an organization that support its role in livestock systems or supply chains. Conceptually extends schema.org/organization.
    """

    establishmentIdentifiers: Optional[List[IcarOrganizationIdentifierType]] = Field(
        None,
        description="Scheme and identifier combinations that provide official registrations for a business or establishment",
    )
    address: Optional[PostalAddress] = Field(
        None,
        description="Postal address or physical address in postal format, including country. Optional as this may already be specified in a consignment.",
    )
    parentOrganization: Optional[IcarOrganizationIdentityType] = Field(
        None,
        description="The larger organization that this organization is a sub-organization of, if any.",
    )
    membershipIdentifiers: Optional[List[IcarOrganizationIdentifierType]] = Field(
        None,
        description="Scheme and identifier combinations that identity membership in programmes",
    )


class IcarInterestedPartyType(IcarOrganizationType):
    """
    Identifies the interests an organization has in an entity, for example in a consignment or in a processingLot. Extends the organization object.
    """

    interests: List[str] = Field(
        ...,
        description="Identifies the type of interest that the party has in a consignment or animal.",
    )


class IcarDeclarationIdentifierType(IcarIdentifierType):
    """
    A scheme and ID combination that uniquely identifies a claim or declaration in an assurance programme or equivalent.
    """


class IcarConsignmentDeclarationType(BaseModel):
    """
    A Consignment Declaration provides a claim or declaration, usually by the source of animals, regarding the assurance or other status of animals in the consignment.
    """

    declarationId: Optional[IcarDeclarationIdentifierType] = Field(
        None,
        description="Identifies the specific declaration being made using a scheme and an id.",
    )
    declaredValue: Optional[str] = Field(
        None, description="The value of the declaration."
    )


class IcarConsignmentType(BaseModel):
    """
    Consignment information for a movement (arrival, departure).
    """

    id: Optional[IcarIdentifierType] = Field(
        None, description="Official identifier for the movement."
    )
    originLocation: Optional[IcarLocationIdentifierType] = Field(
        None,
        description="The location of the origin of the consignment expressed as a scheme and id.",
    )
    originAddress: Optional[str] = Field(
        None, description="Origin address for movement."
    )
    originPostalAddress: Optional[PostalAddress] = Field(
        None,
        description="A structured, schema.org-style address for the origin location.",
    )
    originOrganization: Optional[IcarOrganizationType] = Field(
        None,
        description="The organisational details of the origin, including any necessary identifiers.",
    )
    destinationLocation: Optional[IcarLocationIdentifierType] = Field(
        None,
        description="The location of the destination of the consignment expressed as a scheme and id.",
    )
    destinationAddress: Optional[str] = Field(
        None, description="Destination address for movement."
    )
    destinationPostalAddress: Optional[PostalAddress] = Field(
        None,
        description="A structured, schema.org-style address for the destination location.",
    )
    destinationOrganization: Optional[IcarOrganizationType] = Field(
        None,
        description="The organisational details of the destination, including any necessary identifiers.",
    )
    loadingDateTime: Optional[datetime] = Field(
        None,
        description="RFC3339 UTC date and time animals were loaded for transport (see https://ijmacd.github.io/rfc3339-iso8601/ for format guidance).",
    )
    unloadingDateTime: Optional[datetime] = Field(
        None,
        description="RFC3339 UTC date and time animals were unloaded after transport (see https://ijmacd.github.io/rfc3339-iso8601/ for format guidance).",
    )
    expectedDuration: Optional[float] = Field(
        None, description="Expected duration of transportation in hours."
    )
    transportOperator: Optional[str] = Field(
        None,
        description="Transport operator official name (should really be schema.org/organization).",
    )
    vehicle: Optional[str] = Field(
        None, description="Identification of the vehicle (for example, licence plate)."
    )
    transportReference: Optional[str] = Field(
        None, description="Shipping or transporter reference."
    )
    isolationFacilityUsed: Optional[bool] = Field(
        None, description="True if an isolation facility was used for the movement."
    )
    farmAssuranceReference: Optional[IcarIdentifierType] = Field(
        None, description="Identification reference of a farm assurance operation."
    )
    countConsigned: Optional[int] = Field(
        None,
        description="The number of animals despatched or consigned from the origin.",
    )
    countReceived: Optional[int] = Field(
        None, description="The number of animals received at the destination."
    )
    hoursOffFeed: Optional[int] = Field(
        None,
        description="The number of hours since animals in the consignment had access to feed.",
    )
    hoursOffWater: Optional[int] = Field(
        None,
        description="The number of hours since animals in the consignment had access to water.",
    )
    references: Optional[List[IcarIdentifierType]] = Field(
        None,
        description="References associated with the consignment. These may be additional to the single transport reference (for instance, to support multi-mode transport).",
    )
    interestedParties: Optional[List[IcarInterestedPartyType]] = Field(
        None,
        description="Identifies the parties and their interests in the consignment.",
    )
    declarations: Optional[List[IcarConsignmentDeclarationType]] = Field(
        None,
        description="Country, species or scheme -specific declarations for the consignment.",
    )


class IcarReasonIdentifierType(IcarIdentifierType):
    """
    Extended reason identifier based on a scheme and ID.
    """


class IcarAnimalStateType(BaseModel):
    """
    State information about an animal
    """

    currentLactationParity: Optional[float] = Field(
        None, description="The current parity of the animal."
    )
    lastCalvingDate: Optional[date] = Field(
        None,
        description="RFC3339 UTC date (see https://ijmacd.github.io/rfc3339-iso8601/).",
    )
    lastInseminationDate: Optional[date] = Field(
        None,
        description="RFC3339 UTC date (see https://ijmacd.github.io/rfc3339-iso8601/).",
    )
    lastDryingOffDate: Optional[date] = Field(
        None,
        description="RFC3339 UTC date (see https://ijmacd.github.io/rfc3339-iso8601/).",
    )


class IcarReproHeatWindowType(BaseModel):
    """
    The optimum breeding window for an animal in heat
    """

    startDateTime: datetime = Field(
        ...,
        description="RFC3339 UTC date/time when the optimum insemination window starts (see https://ijmacd.github.io/rfc3339-iso8601/ for format guidance).",
    )
    endDateTime: Optional[datetime] = Field(
        None,
        description="RFC3339 UTC date/time when the optimum insemination window ends (see https://ijmacd.github.io/rfc3339-iso8601/ for format guidance).",
    )
    windowName: Optional[str] = Field(
        None, description="The name of the optimum insemination breeding window."
    )


class IcarSireRecommendationType(BaseModel):
    """
    Gives one possible sire recommended to use on an animal.
    """

    recommendationType: Optional[enums.IcarRecommendationType] = None
    sireIdentifiers: Optional[List[IcarAnimalIdentifierType]] = Field(
        None,
        description="Unique scheme/identifier combinations for the sire, including official ID and Herdbook.",
    )
    sireOfficialName: Optional[str] = Field(
        None, description="Official herdbook name of the sire."
    )
    sireURI: Optional[str] = Field(
        None, description="URI to an AnimalCoreResource for the sire."
    )
    isSexedSemen: Optional[bool] = Field(
        None, description="True if this is sexed semen."
    )
    sexedGender: Optional[enums.IcarAnimalGenderType] = Field(
        None, description="Specify Male or Female for sexed semen only."
    )
    parity: Optional[int] = Field(
        None, description="The parity of the cow for which the recommendation is valid."
    )
    sireRank: Optional[int] = Field(
        None,
        description="The rank of the sire in the recommendation, 1 = first choice, 2 = second, ....",
    )
