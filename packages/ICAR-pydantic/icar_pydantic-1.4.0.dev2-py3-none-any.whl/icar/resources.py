from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field, RootModel

from . import enums, types


class IcarResponseMessageResource(BaseModel):
    """
    An RFC7807 compliant problem response for JSON APIs.
    """

    type: Optional[str] = Field(
        None,
        description="Machine readable URI or code that defines the type of error or warning.",
    )
    severity: Optional[enums.IcarBatchResultSeverityType] = Field(
        None, description="Distinguish errors, warnings, and informational messages."
    )
    status: Optional[int] = Field(
        None, description="The HTTP status code applicable to this problem."
    )
    title: Optional[str] = Field(
        None,
        description="A short, human-readable summary of the problem that SHOULD NOT change from occurrence to occurrence of the problem, except for purposes of localization.",
    )
    detail: Optional[str] = Field(
        None,
        description="A human-readable explanation specific to this occurrence of the problem. Like title, this field’s value can be localized.",
    )
    instance: Optional[str] = Field(
        None,
        description="A URI reference or internal JSON document reference to the specific data item that caused the problem.",
    )


class IcarResource(BaseModel):
    """
    Base class for a resource, defining self-link and meta data. Resources should use AllOf to incorporate this class.
    """

    resourceType: str = Field(
        ...,
        description="Uniform resource identifier (URI) or shortname of the logical resourceType. The ResourceType catalog defines the set of allowed resourceTypes.",
    )
    field_self: Optional[str] = Field(
        None,
        alias="@self",
        description="Uniform resource identifier (URI) of the resource (rel=self).",
    )
    meta: Optional[types.IcarMetaDataType] = Field(
        None,
        description="Meta-data for the resource. Mandatory if you wish to support synchronisation.\n Systems should maintain and provide meta data if at all possible.\nICAR ADE working group intend meta to be required in the next major release of ADE.",
    )
    location: Optional[types.IcarLocationIdentifierType] = Field(
        None, description="Unique location scheme and identifier combination."
    )


class IcarEventCoreResource(IcarResource):
    """
    Core schema for representing an event.
    """

    id: Optional[str] = Field(
        None, description="Unique identifier in the source system for this event."
    )
    eventDateTime: Optional[datetime] = Field(
        None,
        description="RFC3339 UTC date and time (see https://ijmacd.github.io/rfc3339-iso8601/).",
    )
    traitLabel: Optional[types.IcarTraitLabelIdentifierType] = Field(
        None,
        description="If the event represents a formal trait, identifies the recording system and trait.",
    )
    responsible: Optional[str] = Field(
        None,
        description="Use if an observation is manually recorded, or an event is carried out or authorised by a person. SHOULD be a person object.",
    )
    contemporaryGroup: Optional[str] = Field(
        None,
        description="For manually recorded events, record any contemporary group code that would affect statistical analysis.",
    )
    remark: Optional[str] = Field(
        None,
        description="A comment or remark field for additional user-specified information about the event.",
    )


class IcarAnimalEventCoreResource(IcarEventCoreResource):
    """
    Extends icarEventCoreResource to add a single individual animal identifier.
    """

    animal: types.IcarAnimalIdentifierType = Field(
        ..., description="Unique animal scheme and identifier combination."
    )


class IcarFeedReportResource(IcarResource):
    """
    Reporting the feed consumed during a certain time period
    """

    animals: Optional[List[types.IcarAnimalIdentifierType]] = Field(
        None,
        description="As per JSON-LD Hydra syntax, animals provides the array of animals part of the feeding report. This could also be a report for one animal.",
    )
    reportStartDateTime: Optional[datetime] = Field(
        None,
        description="The RFC3339 UTC moment the period of the reporting started (see https://ijmacd.github.io/rfc3339-iso8601/ for format guidance).",
    )
    reportEndDateTime: Optional[datetime] = Field(
        None,
        description="The RFC3339 UTC moment the period of the reporting ended (see https://ijmacd.github.io/rfc3339-iso8601/ for format guidance).",
    )
    feedVisitDuration: Optional[types.IcarFeedDurationType] = None
    consumedFeed: Optional[List[types.IcarConsumedFeedType]] = None
    consumedRation: Optional[List[types.IcarConsumedRationType]] = None


class SupportedMessage(BaseModel):
    messages: Optional[enums.IcarMessageType] = None


class IcarDeviceResource(IcarResource):
    """
    This resource is used to describe an instance of a device at a location.
    """

    id: str = Field(
        ...,
        description="Unique identifier on location level in the source system for this device.",
    )
    serial: Optional[str] = Field(
        None, description="Optionally, the serial number of the device."
    )
    name: Optional[str] = Field(
        None, description="Name given to the device by the farmer."
    )
    description: Optional[str] = Field(
        None, description="Description of the device by the farmer."
    )
    softwareVersion: Optional[str] = Field(
        None, description="Version of the software installed on the device."
    )
    hardwareVersion: Optional[str] = Field(
        None, description="Version of the hardware installed in the device."
    )
    isActive: Optional[bool] = Field(
        None, description="Indicates whether the device is active at this moment."
    )
    supportedMessages: Optional[List[SupportedMessage]] = Field(
        None, description="Identifies message types supported for the device"
    )
    manufacturer: Optional[types.IcarDeviceManufacturerType] = Field(
        None, description="The device data as defined by the manufacturer."
    )
    registration: Optional[types.IcarDeviceRegistrationIdentifierType] = Field(
        None,
        description="A registration identifier for the device (most devices should eventually have a registration issued by `org.icar` or other entity).",
    )


class IcarInventoryTransactionType(IcarEventCoreResource):
    """
    Inventory Transaction defines a transaction on a product inventory where the transaction may be a receipt, disposal, on hand, stocktake, use
    """

    transactionKind: enums.IcarInventoryTransactionKindType = Field(
        ..., description="Identifies the transaction kind."
    )
    quantity: float = Field(
        ...,
        description="The overall volume, weight or count of the product in the transaction in the units defined.",
    )
    units: str = Field(
        ...,
        description="The units of the quantity specified.  Where applicable it is recommended that uncefact mass and volume units are used.",
    )
    supplierName: Optional[str] = Field(
        None,
        description="The supplier of the product in this transaction.  This is particularly relevant if the transaction is a receipt.",
    )
    expiryDate: Optional[datetime] = Field(
        None, description="The expiry date of the product supplied in the transaction."
    )
    totalCost: Optional[float] = Field(
        None, description="Total cost applied to this transaction"
    )
    currency: Optional[str] = Field(
        None,
        description="The currency of the cost expressed using the ISO 4217 3-character code (such as AUD, GBP, USD, EUR).",
    )
    packSize: Optional[float] = Field(
        None,
        description="The volume or weight of the product in a pack in the units defined. Especially relevant for Vet Medicines.",
    )
    numberOfPacks: Optional[float] = Field(
        None,
        description="The number of packs of the product in the transaction. Especially relevant for Vet Medicines. Could be a decimal number for a part-pack.",
    )


class IcarAnimalSetResource(IcarResource):
    """
    Core schema for representing animal sets (often called groups or sessions).
    """

    id: str = Field(
        ..., description="Unique identifier in the source system for this animal set."
    )
    name: Optional[str] = Field(None, description="Human readable name of the set.")
    reference: Optional[str] = Field(
        None,
        description="This property can be used by parties for any other reference information used to synchronise systems or display to the user.",
    )
    purpose: Optional[enums.IcarSetPurposeType] = Field(
        None, description="Purpose of the animal set."
    )
    member: List[types.IcarAnimalIdentifierType] = Field(
        ...,
        description="As per JSON-LD Hydra syntax, member provides the array of objects, in this case animals assigned to the set.",
    )


class IcarGroupEventCoreResource(IcarEventCoreResource):
    """
    Extends icarEventCoreResource to support event observations on groups of animals.
    """

    groupMethod: enums.IcarGroupEventMethodType = Field(
        ...,
        description="Indicates whether the event references an existing animal set, has an embedded animal set, or an inventory classification.",
    )
    countObserved: Optional[int] = Field(
        None,
        description="Summarises the number of animals observed in the event. Generally the number of animals in the group, but sometimes a sample.",
    )
    inventoryClassification: Optional[types.IcarInventoryClassificationType] = Field(
        None,
        description="Describe the group of animals by their characteristics rather than animal identifiers.",
    )
    embeddedAnimalSet: Optional[IcarAnimalSetResource] = Field(
        None,
        description="Specifies the set of animals as a list of member animal identifiers.",
    )
    animalSetReference: Optional[types.IcarAnimalSetReferenceType] = Field(
        None, description="Reference an existing animal set by ID and optionally URI"
    )


class IcarBatchResult(BaseModel):
    """
    Returned by a batch POST event to return identity (meta), errors, and warnings for a resource.
    """

    id: Optional[str] = Field(
        None,
        description="Unique identifier created in the system for this event. SHOULD be a UUID.",
    )
    meta: Optional[types.IcarMetaDataType] = Field(
        None,
        description="Metadata for the posted resource. Allows specification of the source, source Id to synchronise data.",
    )
    messages: Optional[List[IcarResponseMessageResource]] = Field(
        None,
        description="An array of errors for this resource. The messages array may be unspecified OR null.",
    )


class IcarDiagnosisEventResource(IcarAnimalEventCoreResource):
    """
    A standalone diagnosis of one or more animal health conditions.
    """

    diagnoses: Optional[List[types.IcarDiagnosisType]] = Field(
        None,
        description="Diagnosis of the animal health condition. An array allows for several conditions to be recorded at once.",
    )


class IcarTreatmentEventResource(IcarAnimalEventCoreResource):
    """
    Defines a single animal health treatment, which may be medication or procedure.
    """

    medicine: Optional[types.IcarMedicineReferenceType] = Field(
        None, description="A reference to the medicine used (where applicable)."
    )
    procedure: Optional[str] = Field(
        None, description="Medicine application method or a non-medicine procedure."
    )
    batches: Optional[List[types.IcarMedicineBatchType]] = Field(
        None, description="Batches and expiry details for the medicine administered."
    )
    withdrawals: Optional[List[types.IcarMedicineWithdrawalType]] = Field(
        None, description="Withholding details for the treatment administered."
    )
    dose: Optional[types.IcarMedicineDoseType] = Field(
        None, description="Details of medicine dose administered"
    )
    site: Optional[str] = Field(
        None, description="Body site where the treatment was administered."
    )
    positions: Optional[List[types.IcarPositionType]] = Field(
        None, description="The positions to be treated"
    )
    comment: Optional[str] = Field(
        None, description="A comment recorded about the treatment or its outcome."
    )


class IcarGroupTreatmentEventResource(IcarGroupEventCoreResource):
    """
    Defines a health treatment applied to a group of animals.
    """

    medicine: Optional[types.IcarMedicineReferenceType] = Field(
        None, description="A reference to the medicine used (where applicable)."
    )
    procedure: Optional[str] = Field(
        None, description="Medicine application method or a non-medicine procedure."
    )
    batches: Optional[List[types.IcarMedicineBatchType]] = Field(
        None, description="Batches and expiry details for the medicine administered."
    )
    withdrawals: Optional[List[types.IcarMedicineWithdrawalType]] = Field(
        None, description="Withholding details for the treatment administered."
    )
    dosePerAnimal: Optional[types.IcarMedicineDoseType] = Field(
        None, description="The actual or average medicine dose administered per animal."
    )
    totalMedicineUsed: Optional[types.IcarMedicineDoseType] = Field(
        None, description="The total amount of medicine used."
    )
    site: Optional[str] = Field(
        None, description="Body site where the treatment was administered."
    )
    positions: Optional[List[types.IcarPositionType]] = Field(
        None, description="The positions to be treated"
    )


class IcarTreatmentProgramEventResource(IcarAnimalEventCoreResource):
    """
    An animal health event combining diagnosis and planned or actual treatment course or events.
    """

    diagnoses: Optional[List[types.IcarDiagnosisType]] = Field(
        None, description="Decribes the diagnosis of one or more conditions"
    )
    courses: Optional[List[types.IcarMedicineCourseSummaryType]] = Field(
        None,
        description="Details the course of treatments at a summary (start and end date) level. The array allows for different medicines/procedures.",
    )
    treatments: Optional[List[IcarTreatmentEventResource]] = Field(
        None,
        description="The list of the treatments (medicines or procedures) applied.",
    )


class IcarHealthStatusObservedEventResource(IcarAnimalEventCoreResource):
    """
    Event for recording animal health status
    """

    observedStatus: Optional[enums.IcarAnimalHealthStatusType] = Field(
        None,
        description="Health status of the animal (such as Healthy, Suspicious, Ill, InTreatment, ToBeCulled). A null value is not supported.",
    )


class IcarAnimalSetJoinEventResource(IcarAnimalEventCoreResource):
    """
    The animal set join event records animals joining animal set resources, i.e. additions of animals to a set.
    """

    animalSetId: str = Field(
        ...,
        description="Unique identifier in the source system for the animal set to be joined.",
    )


class IcarAnimalSetLeaveEventResource(IcarAnimalEventCoreResource):
    """
    The animal set leave event records animals leaving animal set resources, i.e. removals of animals from a set.
    """

    animalSetId: str = Field(
        ...,
        description="Unique identifier in the source system for the animal set to be left.",
    )


class IcarInventoryTransactionResource(IcarInventoryTransactionType):
    """
    Generic inventory transaction resource.  Some product families have specific transaction resources (e.g. medicines, feeds).
    """

    product: types.IcarProductReferenceType = Field(
        ..., description="The product in this inventory transaction."
    )


class IcarRemarkEventResource(IcarAnimalEventCoreResource):
    """
    This event resource is used to record a note or remark made by a farmer or other person.
    """

    note: Optional[str] = Field(
        None,
        description="Unstructured, human-readable note or remark about the animal.\nConsider using `responsible` to identify the person who recorded it.",
    )


class IcarStatisticsResource(IcarResource):
    """
    Describes the statistics for a certain location.
    """

    id: str = Field(
        ...,
        description="Unique identifier on location level in the source system for this statistics.",
    )
    location: types.IcarLocationIdentifierType = Field(
        ..., description="Unique location scheme and identifier combination."
    )
    purpose: enums.IcarStatisticsPurposeType = Field(
        ..., description="Defines the purpose for these statistics."
    )
    dateFrom: date = Field(
        ..., description="The start of the period for which statistics are calculated."
    )
    dateTo: date = Field(
        ..., description="The end of the period for which statistics are calculated."
    )
    group: List[types.IcarStatisticsGroupType] = Field(
        ...,
        description="An array of groups for which statistics are calculated, each of which has statistics for that group.",
    )


class IcarTestDayResource(IcarResource):
    """
    Information about test day for milk sampling.
    """

    id: str = Field(..., description="Unique identifier for this test day.")
    beginDate: datetime = Field(
        ...,
        description="The RFC3339 UTC datetime of the beginning of the milk sampling (see https://ijmacd.github.io/rfc3339-iso8601/ for format guidance).",
    )
    endDate: datetime = Field(
        ...,
        description="The RFC3339 UTC datetime of the end of the milk sampling (see https://ijmacd.github.io/rfc3339-iso8601/ for format guidance).",
    )


class IcarLactationStatusObservedEventResource(IcarAnimalEventCoreResource):
    """
    This event records an observed lactation status without necessarily a parturition, drying off, or other event.
    """

    observedStatus: Optional[enums.IcarAnimalLactationStatusType] = Field(
        None, description="The lactation status at the time of observation."
    )


class IcarDailyMilkingAveragesResource(IcarResource):
    """
    Resource containing daily averages calculated from milking visit of a single animal
    """

    id: Optional[str] = Field(
        None, description="Unique identifier in the source system for this event."
    )
    animal: types.IcarAnimalIdentifierType = Field(
        ..., description="Unique animal scheme and identifier combination."
    )
    averageDate: date = Field(
        ..., description="The date on which the average has been calculated."
    )
    milkYieldAvg24h: Optional[types.IcarTraitAmountType] = Field(
        None, description="The average-amount of milk produced within 24h."
    )
    milkYieldAvg7days: Optional[types.IcarTraitAmountType] = Field(
        None, description="The average-amount of milk produced within 7 days."
    )


class IcarMilkPredictionResource(IcarAnimalEventCoreResource):
    """
    This returns a prediction of the expected milk, fat and protein for a cow for the remaining the lactation. A prediction of this production on the next testday is included and it also gives indication of when the peak production is reached. The eventDateTime for this event is the date of the prediction is made.
    """

    averagePredictedProduction: Optional[types.IcarMilkingPredictionType] = None
    daysInMilkAtLactationPeak: Optional[int] = Field(
        None,
        description="The days in milk in a lactation when the peak production is expected to occur.",
    )
    lactationPeakProduction: Optional[types.IcarMilkingPredictionType] = None
    predictedProductionNextMR: Optional[types.IcarMilkingPredictionType] = None


class IcarLactationResource(IcarResource):
    """
    Lactation information of an animal.
    """

    id: str = Field(
        ..., description="Unique identifier in the source system for this event."
    )
    animal: types.IcarAnimalIdentifierType = Field(
        ..., description="Unique animal scheme and identifier combination."
    )
    beginDate: Optional[datetime] = Field(
        None,
        description="The RFC3339 UTC date of the beginning of the lactation (see https://ijmacd.github.io/rfc3339-iso8601/ for format guidance).",
    )
    endDate: Optional[datetime] = Field(
        None,
        description="The RFC3339 UTC end date of the the lactation. This occurs when the animal is dried off, dies or calves again.",
    )
    parity: Optional[float] = Field(
        None, description="The parity of the animal during this lactation."
    )
    lactationLength: Optional[float] = Field(
        None, description="The length of the lactation until this moment."
    )
    milkAmount: Optional[types.IcarTraitAmountType] = Field(
        None, description="The amount of milk produced in this lactation."
    )
    fatAmount: Optional[types.IcarTraitAmountType] = Field(
        None, description="The amount of fat produced in this lactation."
    )
    proteinAmount: Optional[types.IcarTraitAmountType] = Field(
        None, description="The amount of protein produced in this lactation."
    )
    lactosisAmount: Optional[types.IcarTraitAmountType] = Field(
        None, description="The amount of lactosis produced in this lactation."
    )
    lastTestDay: Optional[datetime] = Field(
        None,
        description="The RCF3339 UTC date of the last test day in the lactation (see https://ijmacd.github.io/rfc3339-iso8601/ for format guidance).",
    )
    lactationType: Optional[enums.IcarLactationType] = Field(
        None,
        description="This type of lactation based on lactation length that is delivered.",
    )
    milkRecordingMethod: Optional[types.IcarMilkRecordingMethodType] = None


class IcarWithdrawalEventResource(IcarAnimalEventCoreResource):
    """
    A withdrawal resource used to indicate that product should be separated (e.g. colostrum from newly lactating cows).
    """

    endDateTime: Optional[datetime] = Field(
        None,
        description="RFC3339 UTC date and time (see https://ijmacd.github.io/rfc3339-iso8601/).",
    )
    productType: enums.IcarWithdrawalProductType = Field(
        ..., description="Product or food item affected by this withdrawal."
    )


class IcarBreedingValueResource(IcarResource):
    """
    Breeding values of an animal.
    """

    id: str = Field(
        ..., description="Unique identifier in the source system for this event."
    )
    animal: types.IcarAnimalIdentifierType = Field(
        ..., description="Unique animal scheme and identifier combination."
    )
    base: Optional[types.IcarBVBaseIdentifierType] = Field(
        None, description="The scheme and the id of the base of the breeding value."
    )
    version: Optional[str] = Field(
        None,
        description=" string which sets the version for the breeding value estimation - this can be a date, or a version name, or something the calculation center is using to identify their seperate runs.",
    )
    breedingValues: Optional[List[types.IcarBreedingValueType]] = None


class IcarLocationResource(IcarResource):
    """
    A location scheme / location id combination.
    """

    identifier: types.IcarLocationIdentifierType = Field(
        ..., description="Unique location scheme and identifier combination."
    )
    alternativeIdentifiers: Optional[List[types.IcarLocationIdentifierType]] = Field(
        None,
        description="Alternative identifiers for the location. Must be a 1:1 mapping, meaning that when querying resources with an alternative identifier (instead of the 'main' identifier), the response may not be different.",
    )
    name: Optional[str] = Field(
        None, description="The human readable name of the location."
    )
    timeZoneId: Optional[str] = Field(
        None,
        description="The time zone ID of the location according to the IANA time zone database (https://www.iana.org/time-zones), e.g. Europe/Paris. Can be used to convert UTC times in events, resources etc. back to the locations time zone while also taking daylight saving times into account.",
    )


class HeatReportScrSenseTime(BaseModel):
    """
    Specific info when the heat was detected by SenseTime from SCR
    """

    breedingWindow: Optional[int] = Field(None, description="Number of hours to AI.")
    heatIndex: Optional[int] = Field(
        None, description="Gives an indication of the certainty of the heat indication."
    )


class HeatReportNedapCowControl(BaseModel):
    """
    Specific info when the heat was detected by CowControl from NEDAP
    """

    expirationDateTime: Optional[datetime] = Field(
        None,
        description="RFC3339 UTC date/time when the heat will end (see https://ijmacd.github.io/rfc3339-iso8601/ for format guidance).",
    )
    heatChance: Optional[int] = Field(
        None, description="Gives an indication of the certainty of the heat indication."
    )


class IcarMilkingDryOffEventResource(IcarAnimalEventCoreResource):
    """
    Records that the animal has been dried off from milking. If necessary, also record a separate health treatment event.
    """


class IcarReproAbortionEventResource(IcarAnimalEventCoreResource):
    """
    The abortion event records an observation that an abortion has taken place. There are no other parameters.
    """


class IcarReproDoNotBreedEventResource(IcarAnimalEventCoreResource):
    """
    The do not breed event records an observation that an animal has been assigned not to be bred. There are no other parameters.
    """

    doNotBreed: Optional[bool] = Field(
        True,
        description="Set this attribute to true if the animal should not be bred, false if it may now be bred.",
    )
    extendedReasons: Optional[List[types.IcarReasonIdentifierType]] = Field(
        None, description="Extended reason codes why this animal should not be bred."
    )


class IcarGestationResource(IcarResource):
    """
    This resource holds computed or predicted gestation information for animals at a location.
    - Use this resource to understand potential sire and expected calving date.
    - This resource should be recomputed when a heat, repro-status observation, or pregnancy check event is recorded.
    """

    id: str = Field(
        ...,
        description="Unique identifier in the source system for this computed resource.",
    )
    animal: types.IcarAnimalIdentifierType = Field(
        ..., description="Unique animal scheme and identifier combination."
    )
    sireIdentifiers: Optional[List[types.IcarAnimalIdentifierType]] = Field(
        None,
        description="Unique scheme/identifier combinations for the sire, including official ID and Herdbook.",
    )
    expectedCalvingDate: datetime = Field(
        ...,
        description="The RFC3339 UTC date the calving is expected to happen (see https://ijmacd.github.io/rfc3339-iso8601/ for format guidance).",
    )


class IcarReproStatusObservedEventResource(IcarAnimalEventCoreResource):
    """
    This event records an observed reproductive status without necessarily a pregnancy check, parturition, or other event.
    """

    observedStatus: Optional[enums.IcarAnimalReproductionStatusType] = Field(
        None, description="The reproductive status at the time of observation."
    )


class IcarReproSemenStrawResource(IcarResource):
    """
    Describes a semen straw
    """

    id: Optional[types.IcarIdentifierType] = Field(
        None, description="Official identifier for the straw (if any)."
    )
    batch: Optional[str] = Field(
        None, description="Identification of the batch of semen."
    )
    collectionCentre: Optional[str] = Field(
        None, description="Identifies the collection centre."
    )
    dateCollected: Optional[datetime] = Field(
        None,
        description="RFC3339 UTC date/time of collection (see https://ijmacd.github.io/rfc3339-iso8601/ for format guidance).",
    )
    sireIdentifiers: Optional[List[types.IcarAnimalIdentifierType]] = Field(
        None,
        description="One or more unique scheme/identifier combinations for the sire.",
    )
    sireOfficialName: Optional[str] = Field(
        None, description="Official herdbook name of the sire."
    )
    sireURI: Optional[str] = Field(
        None, description="URI to an AnimalCoreResource for the sire."
    )
    preservationType: Optional[enums.IcarReproSemenPreservationType] = Field(
        None, description="The method of preservation of the semen (liquid, frozen)."
    )
    isSexedSemen: Optional[bool] = Field(
        None, description="True if this is sexed semen."
    )
    sexedGender: Optional[enums.IcarAnimalGenderType] = Field(
        None, description="Specify Male or Female for sexed semen only."
    )
    sexedPercentage: Optional[int] = Field(
        None,
        description="Percentage of semen that are expected to be of the chosen sex (e.g. 75, 90, 95).",
    )


class IcarReproEmbryoResource(IcarResource):
    """
    Describes an implanted embryo.
    """

    id: Optional[types.IcarIdentifierType] = Field(
        None, description="Official identifier for the embryo (if any)."
    )
    collectionCentre: Optional[str] = Field(
        None, description="Identifies the collection centre."
    )
    dateCollected: Optional[datetime] = Field(
        None,
        description="The RFC3339 UTC date of collection (see https://ijmacd.github.io/rfc3339-iso8601/ for format guidance).",
    )
    donorIdentifiers: Optional[List[types.IcarAnimalIdentifierType]] = Field(
        None,
        description="One or more unique scheme/identifier combinations for the donor dam.",
    )
    donorURI: Optional[str] = Field(
        None, description="URI to an AnimalCoreResource for the donor dam."
    )
    sireIdentifiers: Optional[List[types.IcarAnimalIdentifierType]] = Field(
        None,
        description="One or more unique scheme/identifier combinations for the sire.",
    )
    sireOfficialName: Optional[str] = Field(
        None, description="Official herdbook name of the sire."
    )
    sireURI: Optional[str] = Field(
        None, description="URI to an AnimalCoreResource for the sire."
    )


class IcarProgenyDetailsResource(IcarResource):
    """
    Schema for representing progeny details
    """

    identifier: Optional[types.IcarAnimalIdentifierType] = Field(
        None, description="Unique animal scheme and identifier combination."
    )
    alternativeIdentifiers: Optional[List[types.IcarAnimalIdentifierType]] = Field(
        None,
        description="Alternative identifiers for the animal. Here, also temporary identifiers, e.g. transponders or animal numbers, can be listed.",
    )
    specie: enums.IcarAnimalSpecieType = Field(
        ..., description="Species of the animal."
    )
    gender: enums.IcarAnimalGenderType = Field(..., description="Gender of the animal.")
    managementTag: Optional[str] = Field(
        None,
        description="The identifier used by the farmer in day to day operations. In many cases this could be the animal number.",
    )
    name: Optional[str] = Field(
        None, description="Name given by the farmer for this animal."
    )
    officialName: Optional[str] = Field(None, description="Official herdbook name.")
    taggingDate: Optional[datetime] = Field(
        None,
        description="Progeny tagging date in RFC3339 UTC (see https://ijmacd.github.io/rfc3339-iso8601/ for format guidance).",
    )
    birthStatus: Optional[enums.IcarParturitionBirthStatusType] = Field(
        None, description="Birth status of the progeny."
    )
    birthSize: Optional[enums.IcarParturitionBirthSizeType] = Field(
        None, description="Size of the progeny."
    )
    birthWeight: Optional[types.IcarMassMeasureType] = Field(
        None, description="Weight of the progeny."
    )


class IcarAnimalSortingCommandResource(IcarResource):
    """
    Sorting data for a specific animal on a location.
    """

    animal: types.IcarAnimalIdentifierType = Field(
        ..., description="Unique animal scheme and identifier combination."
    )
    sites: List[str] = Field(
        ...,
        description="Array with unique site identifiers where this animal can be sorted to.",
    )
    validFrom: datetime = Field(
        ...,
        description="Specifies from when the sort command should be active. RFC3339 UTC date time (see https://ijmacd.github.io/rfc3339-iso8601/ for format guidance).",
    )
    validTo: Optional[datetime] = Field(
        None,
        description="Specifies until when the sort command should be active. Could be left empty, when the sorting should be ongoing (until replaced). RFC3339 UTC date time (see https://ijmacd.github.io/rfc3339-iso8601/ for format guidance).",
    )


class IcarSortingSiteResource(IcarResource):
    """
    Site available on a location.
    """

    id: str = Field(..., description="Unique identifier in the system for this site.")
    name: str = Field(
        ..., description="Name of the site as it is known on the location."
    )
    capacity: Optional[float] = Field(
        0, description="The maximum capacity of this site."
    )


class IcarFeedResource(IcarResource):
    """
    Feeds available on a location.
    """

    id: str = Field(
        ..., description="Unique identifier in the source system for this resource."
    )
    category: Optional[enums.IcarFeedCategoryType] = Field(
        None, description="The scheme and the id of the category of the feed."
    )
    type: Optional[types.IcarFeedIdentifierType] = Field(
        None,
        description="The scheme and the id of the type of the feed. ICAR recommends the use of the list of the scheme org.fao",
    )
    name: Optional[str] = Field(
        None, description="Name of the feed as it is known on the location."
    )
    properties: Optional[List[types.IcarFeedPropertyType]] = None
    active: Optional[bool] = Field(
        None,
        description="indicates whether the feed is or was available on the location.",
    )


class IcarRationResource(IcarResource):
    """
    Rations defined on a location.
    """

    id: str = Field(
        ..., description="Unique identifier in the source system for this resource."
    )
    name: Optional[str] = Field(
        None, description="Name of the feed as it is known on the location."
    )
    feeds: Optional[List[types.IcarFeedsInRationType]] = None
    active: Optional[bool] = Field(
        None,
        description="indicates whether the ration is or was available on the location.",
    )


class IcarFeedIntakeEventResource(IcarAnimalEventCoreResource):
    """
    Event for recording a feed intake
    """

    feedingStartingDateTime: datetime = Field(
        ...,
        description="The RFC3339 UTC moment the feeding started (see https://ijmacd.github.io/rfc3339-iso8601/ for format guidance).",
    )
    feedVisitDuration: types.IcarFeedDurationType
    consumedFeed: Optional[List[types.IcarConsumedFeedType]] = None
    consumedRation: Optional[types.IcarConsumedRationType] = Field(
        None, description="The eventual ration that has been consumed"
    )
    device: Optional[types.IcarDeviceReferenceType] = Field(
        None, description="Optional information about the device used for the feeding."
    )


class IcarFeedRecommendationResource(IcarResource):
    """
    An overview of the recommended feeding of animals
    """

    id: str = Field(
        ...,
        description="Unique identifier in the source system for this recommendation.",
    )
    animal: types.IcarAnimalIdentifierType = Field(
        ..., description="Unique animal scheme and identifier combination."
    )
    recommendationDateTime_: Optional[datetime] = Field(
        None,
        alias="recommendationDateTime ",
        description="The RFC3339 UTC timestamp of the recommendation (see https://ijmacd.github.io/rfc3339-iso8601/ for format guidance).",
    )
    startDateTime: Optional[datetime] = Field(
        None,
        description="The RFC3339 UTC date of the beginning of the recommendation (see https://ijmacd.github.io/rfc3339-iso8601/ for format guidance).",
    )
    endDateTime: Optional[datetime] = Field(
        None,
        description="The RFC3339 UTC end date of the recommendation (see https://ijmacd.github.io/rfc3339-iso8601/ for format guidance).",
    )
    recommendedFeed: Optional[List[types.IcarRecommendedFeedType]] = None
    recommendedRation: Optional[List[types.IcarRecommendedRationType]] = None


class IcarFeedStorageResource(IcarDeviceResource):
    """
    Describes the feed storage device on a certain location.
    """

    feedId: Optional[str] = Field(
        None, description="Unique identifier of the feed that is stored in this device."
    )
    capacity: Optional[types.IcarFeedQuantityType] = Field(
        None, description="The amount of feed that can be stored in this device."
    )
    quantityAvailable: Optional[types.IcarFeedQuantityType] = Field(
        None,
        description="The amount of feed that is currently stored in this device and is available for feeding.",
    )
    id: str = Field(
        ...,
        description="Unique identifier on location level in the source system for this device.",
    )


class IcarFeedTransactionResource(IcarInventoryTransactionType):
    """
    An inventory transaction resource for a feed product.
    """

    product: types.IcarFeedReferenceType = Field(
        ..., description="The feed product in this transaction."
    )


class IcarGroupFeedingEventResource(IcarGroupEventCoreResource):
    """
    Event for recording group or mob feeding. Allowances represent averages so this cannot be used to populate individual animal events.
    """

    feedingEndDateTime: Optional[datetime] = Field(
        None,
        description="The RFC3339 UTC moment from which animals could no longer consume the feed (eventDateTime represents the start of feed availability).",
    )
    feedPerAnimal: Optional[List[types.IcarConsumedFeedType]] = None
    feedTotal: Optional[List[types.IcarConsumedFeedType]] = Field(
        None,
        description="Gives the feed offered to and consumed (total for all animals).",
    )
    rationPerAnimal: Optional[List[types.IcarConsumedRationType]] = None
    rationTotal: Optional[List[types.IcarConsumedRationType]] = Field(
        None,
        description="Gives the feed offered to and consumed (total for all animals).",
    )
    device: Optional[types.IcarDeviceReferenceType] = Field(
        None,
        description="Optional information about a device used for the feeding, if relevant.",
    )


class IcarDiagnosisEvent(RootModel[IcarDiagnosisEventResource]):
    root: IcarDiagnosisEventResource


class IcarTreatmentEvent(RootModel[IcarTreatmentEventResource]):
    root: IcarTreatmentEventResource


class IcarGroupTreatmentEvent(RootModel[IcarGroupTreatmentEventResource]):
    root: IcarGroupTreatmentEventResource


class IcarTreatmentProgramEvent(RootModel[IcarTreatmentProgramEventResource]):
    root: IcarTreatmentProgramEventResource


class IcarHealthStatusObservedEvent(RootModel[IcarHealthStatusObservedEventResource]):
    root: IcarHealthStatusObservedEventResource


class IcarMedicineTransactionResource(IcarInventoryTransactionType):
    """
    An inventory transaction resource for a medicine product.
    """

    product: types.IcarMedicineReferenceType = Field(
        ..., description="The medicine product in this transaction."
    )


class IcarAttentionEventResource(IcarAnimalEventCoreResource):
    """
    Defines an alert for an animal that may require attention.
    """

    alertEndDateTime: Optional[datetime] = Field(
        None,
        description="RFC3339 date time that represents the end time of an alert (start time is the eventDateTime) if it has ended.",
    )
    category: enums.IcarAttentionCategoryType = Field(
        ..., description="A category that allows filtering of alerts by subject."
    )
    causes: List[enums.IcarAttentionCauseType] = Field(
        ...,
        description="The specific causes of the alert. This is an array and at least one cause must be specified.",
    )
    priority: Optional[enums.IcarAttentionPriorityType] = Field(
        None, description="The relative priority of the alert."
    )
    severity: Optional[enums.IcarDiagnosisSeverityType] = Field(
        None,
        description="A structured set of severity values that align with those used in disease diagnosis.",
    )
    deviceAttentionScore: Optional[float] = Field(
        None,
        description="Provides a manufacturer- and device-specific score related to the alert.",
    )
    device: Optional[types.IcarDeviceReferenceType] = Field(
        None, description="Identifies the device that is raising the alert."
    )


class IcarGroupPositionObservationEventResource(
    IcarGroupEventCoreResource, types.IcarPositionObservationType
):
    """
    This event records that a group of animals was observed in a specific position or location (either a named location or a geographic coordinate).
    """


class IcarPositionObservationEventResource(
    IcarAnimalEventCoreResource, types.IcarPositionObservationType
):
    """
    This event records that an animal was observed in a specific position or location (either a named location or a geographic coordinate).
    """


class IcarObservationSummaryResource(IcarResource):
    """
    This resource (not an event) is delivered on request to summarise observations for an animal over a time period.
    """

    animal: types.IcarAnimalIdentifierType = Field(
        ..., description="Unique animal scheme and identifier combination."
    )
    statistics: Optional[List[types.IcarObservationStatisticsType]] = Field(
        None,
        description="The summary statistics for this animal. Likely to be summarised on demand based on query parameters.",
    )


class IcarMilkingVisitEventResource(IcarAnimalEventCoreResource):
    """
    Event for recording milking visit
    """

    milkingStartingDateTime: datetime = Field(
        ...,
        description="The RFC3339 UTC date time of the start of milking (see https://ijmacd.github.io/rfc3339-iso8601/ for format guidance).",
    )
    milkingDuration: Optional[types.IcarMilkDurationType] = None
    milkingVisitDuration: Optional[types.IcarMilkDurationType] = None
    milkingType: Optional[enums.IcarMilkingTypeCode] = Field(
        None,
        description="This code allows organisations to distinguish between manual and automated milking.",
    )
    milkingMilkWeight: types.IcarMilkingMilkWeightType = Field(
        ...,
        description="A certified milking weight that complies with the ICAR guidelines.",
    )
    milkingComplete: Optional[bool] = Field(
        None, description="indication whether this milking was completed normally."
    )
    milkingParlourUnit: Optional[str] = Field(
        None, description="The milking parlour unit where the milking took place."
    )
    milkingBoxNumber: Optional[str] = Field(
        None, description="The milking box number where the milking took place."
    )
    milkingDeviceId: Optional[str] = Field(
        None, description="The ID of the device where the milking took place."
    )
    measureDeviceId: Optional[str] = Field(
        None,
        description="The ID of the device where the measurement of the milking took place",
    )
    milkingShiftLocalStartDate: Optional[datetime] = Field(
        None,
        description="The ISO8601 date in local time zone to which this milking shift belongs. A time component is not expected or required.",
    )
    milkingShiftNumber: Optional[int] = Field(
        None,
        description="For milkings supervised by humans, this number represents the shift within a local date in which this milking visit occurred.",
    )
    quarterMilkings: Optional[List[types.IcarQuarterMilkingType]] = Field(
        None,
        description="A set of milking results for up to four quarters in dairy cows, or two teats for sheep or goats.",
    )
    animalMilkingSample: Optional[List[types.IcarAnimalMilkingSampleType]] = Field(
        None,
        description="An array of zero or more sample/bottle details if the animal is milk tested at this milking.",
    )
    milkCharacteristics: Optional[List[types.IcarMilkCharacteristicsType]] = Field(
        None,
        description="An array of milk characteristics other than certified milk weight. See icarMilkCharacteristicsType for documentation.",
    )
    milkingRemarks: Optional[List[enums.IcarMilkingRemarksType]] = None


class IcarTestDayResultEventResource(IcarAnimalEventCoreResource):
    """
    Event for representing test day result
    """

    milkWeight24Hours: Optional[types.IcarMilkingMilkWeightType] = None
    testDayCode: Optional[enums.IcarTestDayCodeType] = None
    milkCharacteristics: Optional[List[types.IcarMilkCharacteristicsType]] = None
    predictedProductionOnTestDay: Optional[types.IcarMilkingPredictionType] = None


class IcarWeightEventResource(IcarAnimalEventCoreResource):
    """
    The Weight event records a live weight observation of an animal.
    """

    weight: Optional[types.IcarMassMeasureType] = Field(
        None, description="The weight measurement, including units and resolution."
    )
    device: Optional[types.IcarDeviceReferenceType] = Field(
        None,
        description="Optional information about the device used for the measurement.",
    )
    timeOffFeed: Optional[float] = Field(
        None,
        description="Hours of curfew or withholding feed prior to weighing to standardise gut fill.",
    )


class IcarGroupWeightEventResource(IcarGroupEventCoreResource):
    """
    The Group Weight event records liveweight observations for a group of animals
    """

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
    animalWeights: Optional[List[types.IcarIndividualWeightType]] = Field(
        None,
        description="Array of animal id and weight pairs for animals in the event.",
    )
    statistics: Optional[List[types.IcarStatisticsType]] = Field(
        None,
        description="Array of weight statistics, namely average, sum, min, max, count, stdev",
    )
    device: Optional[types.IcarDeviceReferenceType] = Field(
        None,
        description="Optional information about the device used for the measurement.",
    )
    timeOffFeed: Optional[float] = Field(
        None,
        description="Hours of curfew or withholding feed prior to weighing to standardise gut fill.",
    )


class IcarTypeClassificationEventResource(IcarAnimalEventCoreResource):
    """
    Event for recording a type calssification consisting of a set of conformation scores
    """

    conformationScores: Optional[List[types.IcarConformationScoreType]] = None


class IcarConformationScoreEventResource(
    IcarAnimalEventCoreResource, types.IcarConformationScoreType
):
    """
    Event for recording conformation score
    """


class IcarAnimalCoreResource(IcarResource):
    """
    Core schema for representing animal
    """

    identifier: types.IcarAnimalIdentifierType = Field(
        ..., description="Unique animal scheme and identifier combination."
    )
    alternativeIdentifiers: Optional[List[types.IcarAnimalIdentifierType]] = Field(
        None,
        description="Alternative identifiers for the animal. Here, also temporary identifiers, e.g. transponders or animal numbers, can be listed.",
    )
    specie: enums.IcarAnimalSpecieType = Field(
        ..., description="Species of the animal."
    )
    gender: enums.IcarAnimalGenderType = Field(..., description="Gender of the animal.")
    birthDate: Optional[datetime] = Field(
        None,
        description="RFC3339 UTC date/time of birth (see https://ijmacd.github.io/rfc3339-iso8601/ for how to use).",
    )
    primaryBreed: Optional[types.IcarBreedIdentifierType] = Field(
        None, description="ICAR Breed code for the animal."
    )
    breedFractions: Optional[types.IcarBreedFractionsType] = Field(
        None, description="Breed fractions for the animal."
    )
    coatColor: Optional[str] = Field(
        None,
        description="Colour of the animal's coat, using the conventions for that breed.",
    )
    coatColorIdentifier: Optional[types.IcarCoatColorIdentifierType] = Field(
        None,
        description="Colour of the animal's coat using a national or breed-defined scheme and identifier combination.",
    )
    managementTag: Optional[str] = Field(
        None,
        description="The identifier used by the farmer in day to day operations. In many cases this could be the animal number.",
    )
    name: Optional[str] = Field(
        None, description="Name given by the farmer for this animal."
    )
    officialName: Optional[str] = Field(None, description="Official herdbook name.")
    productionPurpose: Optional[enums.IcarProductionPurposeType] = Field(
        None, description="Primary production purpose for which animals are bred."
    )
    status: Optional[enums.IcarAnimalStatusType] = Field(
        None,
        description="On-farm status of the animal (such as alive, dead, off-farm).",
    )
    reproductionStatus: Optional[enums.IcarAnimalReproductionStatusType] = Field(
        None, description="Reproduction status of the animal."
    )
    lactationStatus: Optional[enums.IcarAnimalLactationStatusType] = Field(
        None, description="Lactation status of the animal."
    )
    parentage: Optional[List[types.IcarParentageType]] = Field(
        None,
        description="Parents of the animal.  The array can handle multiple generations by specifying the parent of a parent.",
    )
    healthStatus: Optional[enums.IcarAnimalHealthStatusType] = Field(
        None,
        description="Health status of the animal (such as Healthy, Suspicious, Ill, InTreatment, ToBeCulled).",
    )


class IcarMovementBirthEventResource(IcarAnimalEventCoreResource):
    """
    Event for recording animal birth
    """

    registrationReason: Optional[enums.IcarRegistrationReasonType] = Field(
        None, description="Identifies whether this is a birth or a registration event"
    )
    animalDetail: Optional[IcarAnimalCoreResource] = Field(
        None,
        description="Core animal details.  Can be used if the animal has not already been defined on the holding.",
    )


class IcarGroupMovementBirthEventResource(IcarGroupEventCoreResource):
    """
    Extends icarGroupEventCoreResource to provide a group animal registration event (named Birth for consistency only).
    """

    registrationReason: enums.IcarRegistrationReasonType = Field(
        ..., description="Identifies whether this is a birth or registration event"
    )


class IcarMovementDeathEventResource(IcarAnimalEventCoreResource):
    """
    Event for recording animal death on farm.
    """

    deathReason: Optional[enums.IcarDeathReasonType] = Field(
        None,
        description="Coded reasons for death including disease, parturition complications, consumption by humans or animals.",
    )
    explanation: Optional[str] = Field(
        None, description="Free text explanation of the reason for death."
    )
    disposalMethod: Optional[enums.IcarDeathDisposalMethodType] = Field(
        None,
        description="Coded disposal methods including approved service, consumption by humans or animals, etc.",
    )
    disposalOperator: Optional[str] = Field(
        None,
        description="Disposal operator official name (should really be schema.org/organization).",
    )
    disposalReference: Optional[str] = Field(
        None, description="Reference (receipt, docket, or ID) for disposal."
    )
    consignment: Optional[types.IcarConsignmentType] = Field(
        None, description="Identifies the consignment of the animal from the holding."
    )
    deathMethod: Optional[enums.IcarDeathMethodType] = Field(
        None,
        description="Defines the method of death, including an accident, natural causes, or euthanised.",
    )
    extendedReasons: Optional[List[types.IcarReasonIdentifierType]] = Field(
        None, description="Extended reason codes why this animal has died."
    )


class IcarGroupMovementDeathEventResource(IcarGroupEventCoreResource):
    """
    Extends icarGroupEventCoreResource to provide a group death event.
    """

    deathreason: Optional[enums.IcarDeathReasonType] = Field(
        None,
        description="Coded reason for death - this is the CAUSE, compared to the MEANS.",
    )
    explanation: Optional[str] = Field(
        None, description="Free text explanation of the reason for death."
    )
    disposalMethod: Optional[enums.IcarDeathDisposalMethodType] = Field(
        None,
        description="Coded disposal methods including approved service, consumption by humans or animals, etc.",
    )
    disposalOperator: Optional[str] = Field(
        None,
        description="Disposal operator official name (should really be schema.org/organization).",
    )
    disposalReference: Optional[str] = Field(
        None, description="Reference (receipt, docket, or ID) for disposal."
    )
    consignment: Optional[types.IcarConsignmentType] = Field(
        None,
        description="Where disposal is by transport, a consignment record may be required.",
    )
    deathMethod: enums.IcarDeathMethodType = Field(
        ...,
        description="Defines the MEANS of death, including an accident, natural causes, or euthanised.",
    )


class IcarMovementArrivalEventResource(IcarAnimalEventCoreResource):
    """
    Event for recording animal arrival
    """

    arrivalReason: Optional[enums.IcarArrivalReasonType] = Field(
        None, description="Reason the animal arrived on the holding."
    )
    animalDetail: Optional[IcarAnimalCoreResource] = Field(
        None,
        description="Core animal details. Can be used if the animal has not already been defined on the holding.",
    )
    animalState: Optional[types.IcarAnimalStateType] = Field(
        None, description="State information about an animal."
    )
    consignment: Optional[types.IcarConsignmentType] = Field(
        None, description="Identifies the consignment of the animal to the holding."
    )


class IcarGroupMovementArrivalEventResource(IcarGroupEventCoreResource):
    """
    Extends icarGroupEventCoreResource to provide a group movement arrival event.
    """

    arrivalReason: enums.IcarArrivalReasonType = Field(
        ..., description="Reason the group of animals arrived on the holding."
    )
    consignment: Optional[types.IcarConsignmentType] = Field(
        None,
        description="Identifies the consignment of the group of animals to the holding.",
    )


class IcarMovementDepartureEventResource(IcarAnimalEventCoreResource):
    """
    Event for recording live animal departure.
    """

    departureKind: Optional[enums.IcarDepartureKindType] = Field(
        None,
        description="Identifies the kind of departure of the animal from the holding.",
    )
    departureReason: Optional[enums.IcarDepartureReasonType] = Field(
        None,
        description="Identifies the reason for the departure of the animal from the holding.",
    )
    consignment: Optional[types.IcarConsignmentType] = Field(
        None, description="Identifies the consignment of the animal from the holding."
    )
    extendedReasons: Optional[List[types.IcarReasonIdentifierType]] = Field(
        None, description="Extended reason codes why this animal has departed."
    )


class IcarGroupMovementDepartureEventResource(IcarGroupEventCoreResource):
    """
    Extends icarGroupEventCoreResource to provide a group movement departure event.
    """

    departureKind: enums.IcarDepartureKindType = Field(
        ...,
        description="Coded description of the type of departure (e.g. sale, agistment, other).",
    )
    departureReason: Optional[enums.IcarDepartureReasonType] = Field(
        None,
        description="Coded description of the reason why the animals are departing.",
    )
    consignment: Optional[types.IcarConsignmentType] = Field(
        None,
        description="Consignment information about origin, destination, and transport.",
    )


class IcarReproPregnancyCheckEventResource(IcarAnimalEventCoreResource):
    """
    Pregnancy diagnosis or check event.
    """

    method: Optional[enums.IcarReproPregnancyMethodType] = Field(
        None, description="Method by which diagnosis was carried out."
    )
    result: Optional[enums.IcarReproPregnancyResultType] = Field(
        None, description="Result - unknown, empty, pregnant."
    )
    foetalAge: Optional[int] = Field(
        None,
        description="Assessed age of the foetus or length of the pregnancy (in days).",
    )
    foetusCount: Optional[int] = Field(
        None, description="If specified, contains the number of foetuses observed."
    )
    foetusCountMale: Optional[int] = Field(
        None, description="If specified, contains number of foetuses observed as male."
    )
    foetusCountFemale: Optional[int] = Field(
        None,
        description="If specified, contains number of foetuses observed as female.",
    )
    exceptions: Optional[List[str]] = Field(
        None, description="Additional local observations - such as ABNORMAL CALF"
    )


class VisualDetection(BaseModel):
    """
    Specific info when the heat was visually detected.
    """

    heatSigns: Optional[List[enums.IcarReproHeatSignType]] = None
    heatIntensity: Optional[enums.IcarReproHeatIntensityType] = None


class IcarReproHeatEventResource(IcarAnimalEventCoreResource):
    """
    Event for recording heats.
    """

    heatDetectionMethod: Optional[enums.IcarReproHeatDetectionMethodType] = None
    certainty: Optional[enums.IcarReproHeatCertaintyType] = None
    commencementDateTime: Optional[datetime] = Field(
        None,
        description="RFC3339 UTC date/time when the heat will start (see https://ijmacd.github.io/rfc3339-iso8601/ for format guidance).",
    )
    expirationDateTime: Optional[datetime] = Field(
        None,
        description="RFC3339 UTC date/time when the heat will end (see https://ijmacd.github.io/rfc3339-iso8601/ for format guidance).",
    )
    visualDetection: Optional[VisualDetection] = Field(
        None, description="Specific info when the heat was visually detected."
    )
    optimumInseminationWindow: Optional[List[types.IcarReproHeatWindowType]] = Field(
        None, description="Details of the optimum breeding windows"
    )
    deviceHeatProbability: Optional[float] = Field(
        None,
        description="The manufacturer specific indication for the certainty of the heat",
    )
    heatReportScrSenseTime: Optional[HeatReportScrSenseTime] = Field(
        None,
        description="Specific info when the heat was detected by SenseTime from SCR",
    )
    heatReportNedapCowControl: Optional[HeatReportNedapCowControl] = Field(
        None,
        description="Specific info when the heat was detected by CowControl from NEDAP",
    )
    device: Optional[types.IcarDeviceReferenceType] = Field(
        None,
        description="Optional information about the device used for the measurement.",
    )


class IcarReproInseminationEventResource(IcarAnimalEventCoreResource):
    """
    Event for recording natural or artificial insemination, including embryo transfer.
    """

    rank: Optional[int] = Field(
        None,
        description="The rank of intervention of each AI carried out within the same reproductive cycle.",
    )
    inseminationType: enums.IcarReproInseminationType
    sireIdentifiers: Optional[List[types.IcarAnimalIdentifierType]] = Field(
        None,
        description="Unique scheme/identifier combinations for the sire, including official ID and Herdbook.",
    )
    sireOfficialName: Optional[str] = Field(
        None, description="Official herdbook name of the sire."
    )
    sireURI: Optional[str] = Field(
        None, description="URI to an AnimalCoreResource for the sire."
    )
    straw: Optional[IcarReproSemenStrawResource] = Field(
        None, description="Details of the straw, which may also include sire details."
    )
    eventEndDateTime: Optional[datetime] = Field(
        None,
        description="To be used in case of running with a bull to end the period. RFC3339 UTC format (see https://ijmacd.github.io/rfc3339-iso8601/ for format guidance).",
    )
    semenFromFarmStocks: Optional[bool] = Field(
        None,
        description="True if the semen is from the farmer's own stocks (false if supplied by technician).",
    )
    farmContainer: Optional[str] = Field(
        None, description="Number or ID of the container from which the dose was taken."
    )
    embryo: Optional[IcarReproEmbryoResource] = Field(
        None, description="Details of the embryo."
    )
    doItYourself: Optional[bool] = Field(
        None,
        description="Only where inseminationType is `insemination`: true if farmer applied, false or not specified if by AI company.",
    )


class IcarReproParturitionEventResource(IcarAnimalEventCoreResource):
    """
    Event for recording parturition (calving, lambing, kidding, fawning).
    """

    isEmbryoImplant: Optional[bool] = Field(
        None, description="True if the progeny is the result of an embryo implant."
    )
    damParity: Optional[int] = Field(
        None, description="The calving, litter, or other parturition number for the dam"
    )
    liveProgeny: Optional[int] = Field(
        None,
        description="The number of live offspring from the parturition. Important if progeny are not identified.",
    )
    totalProgeny: Optional[int] = Field(
        None,
        description="The total number of offspring from the parturition, including those born dead.",
    )
    calvingEase: Optional[enums.IcarReproCalvingEaseType] = Field(
        None, description="Calving ease (enum corresponds to traditional 1-5 values)."
    )
    progenyDetails: Optional[List[IcarProgenyDetailsResource]] = Field(
        None,
        description="List of progeny details. May not be fully identified, but recommend that gender and status are supplied at least.",
    )
    progeny: Optional[List[IcarAnimalCoreResource]] = Field(
        None,
        description="List of progeny. May not be fully identified, but recommend that gender and status are supplied at least.",
    )


class IcarReproMatingRecommendationResource(IcarAnimalEventCoreResource):
    """
    Mating recommendation for an animal
    """

    sireRecommendations: Optional[List[types.IcarSireRecommendationType]] = None


class IcarReproEmbryoFlushingEventResource(IcarEventCoreResource):
    """
    Event for recording embyro flushing
    """

    flushingMethod: enums.IcarReproEmbryoFlushingMethodType
    embryoCount: Optional[int] = Field(
        None, description="The number of embryos extracted in the flushing."
    )
    collectionCentre: Optional[str] = Field(
        None, description="The location where the embryo was flushed."
    )
