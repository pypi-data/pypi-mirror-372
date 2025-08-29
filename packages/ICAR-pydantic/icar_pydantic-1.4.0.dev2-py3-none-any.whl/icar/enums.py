from __future__ import annotations

from enum import Enum


class IcarBatchResultSeverityType(Enum):
    """
    Severity code to distinguish warnings and errors.
    """

    Information = "Information"
    Warning = "Warning"
    Error = "Error"


class IcarFeedCategoryType(Enum):
    """
    Enumeration for feed categories. Each category can have more detail in a type specification.
    """

    Concentrate = "Concentrate"
    Roughage = "Roughage"
    Additives = "Additives"
    Other = "Other"


class UncefactMassUnitsType(Enum):
    """
    Mass units for weight from UN/CEFACT trade facilitation recommendation 20.
     Kilogram, Gram, Pound, Metric Tonne, Microgram, Miligram, Ounce, Pound net.
    """

    KGM = "KGM"
    GRM = "GRM"
    LBR = "LBR"
    TNE = "TNE"
    MC = "MC"
    MGM = "MGM"
    ONZ = "ONZ"
    PN = "PN"


class IcarMethodType(Enum):
    """
    Enumeration for the method with which a value was determined.
    """

    Analyzed = "Analyzed"
    Derived = "Derived"


class UnitCode(Enum):
    """
    UN/CEFACT Common Code for Units of Measurement.
    """

    SEC = "SEC"
    MIN = "MIN"


class IcarMessageType(Enum):
    """
    Enumeration of the ICAR messages. These can be used to identify supported capabilities or functions.
    """

    MilkingVisits = "MilkingVisits"
    TestDayResults = "TestDayResults"
    Births = "Births"
    Deaths = "Deaths"
    Arrivals = "Arrivals"
    Departures = "Departures"
    Animals = "Animals"
    PregnancyChecks = "PregnancyChecks"
    Heats = "Heats"
    DryingOffs = "DryingOffs"
    Inseminations = "Inseminations"
    Abortions = "Abortions"
    Parturitions = "Parturitions"
    MatingRecommendations = "MatingRecommendations"
    Devices = "Devices"
    Weights = "Weights"
    Locations = "Locations"
    AnimalSetJoins = "AnimalSetJoins"
    AnimalSetLeaves = "AnimalSetLeaves"
    ProgenyDetails = "ProgenyDetails"
    BreedingValues = "BreedingValues"
    FeedIntakes = "FeedIntakes"
    FeedReports = "FeedReports"
    FeedRecommendations = "FeedRecommendations"
    Rations = "Rations"
    FeedStorages = "FeedStorages"
    Gestations = "Gestations"
    DoNotBreedInstructions = "DoNotBreedInstructions"
    ReproductionStatusObservations = "ReproductionStatusObservations"
    Lactations = "Lactations"
    LactationStatusObservations = "LactationStatusObservations"
    Withdrawals = "Withdrawals"
    DailyMilkingAverages = "DailyMilkingAverages"
    Diagnoses = "Diagnoses"
    Treatments = "Treatments"
    TreatmentPrograms = "TreatmentPrograms"
    HealthStatusObservations = "HealthStatusObservations"
    ConformationScores = "ConformationScores"
    TypeClassifications = "TypeClassifications"
    Statistics = "Statistics"
    Schemes = "Schemes"
    Embryos = "Embryos"
    SemenStraws = "SemenStraws"
    Flushings = "Flushings"
    GroupTreatments = "GroupTreatments"
    GroupBirths = "GroupBirths"
    GroupArrivals = "GroupArrivals"
    GroupDepartures = "GroupDepartures"
    GroupDeaths = "GroupDeaths"
    GroupWeights = "GroupWeights"
    Other = "Other"


class IcarInventoryTransactionKindType(Enum):
    """
    Defines the kinds of inventory transaction, which can represent items received, disposed of (including sale or destruction), used, counted in a stocktake or calculated on hand.
    """

    Receipt = "Receipt"
    Disposal = "Disposal"
    OnHand = "OnHand"
    Produce = "Produce"
    StockTake = "StockTake"
    Use = "Use"


class IcarProductFamilyType(Enum):
    """
    Defines the families of products
    """

    Animal_Feeds = "Animal Feeds"
    Animal_Reproductive_Products = "Animal Reproductive Products"
    Veterinary_Supplies = "Veterinary Supplies"
    Seed_and_Plant_Material = "Seed and Plant Material"
    Fertilisers_and_Nutrients = "Fertilisers and Nutrients"
    Pest_Control_Products = "Pest Control Products"
    Other_Animal_Products = "Other Animal Products"
    Milking_Supplies = "Milking Supplies"
    Fencing_Supplies = "Fencing Supplies"
    Water_System_Supplies = "Water System Supplies"
    Fuel = "Fuel"
    Other = "Other"


class IcarGroupEventMethodType(Enum):
    """
    Defines how the set of animals in a group event is defined.
    """

    ExistingAnimalSet = "ExistingAnimalSet"
    EmbeddedAnimalSet = "EmbeddedAnimalSet"
    InventoryClassification = "InventoryClassification"
    EmbeddedAnimalSetAndInventoryClassification = (
        "EmbeddedAnimalSetAndInventoryClassification"
    )


class IcarAnimalSpecieType(Enum):
    """
    Enumeration for species of animal using English names. Previous ADE definitions used a mixture of English and Genus names.
    """

    Buffalo = "Buffalo"
    Cattle = "Cattle"
    Deer = "Deer"
    Elk = "Elk"
    Goat = "Goat"
    Horse = "Horse"
    Pig = "Pig"
    Sheep = "Sheep"


class IcarAnimalGenderType(Enum):
    """
    Enumeration for sex of animal using species-independent English names. Includes neuter/cryptorchid variations.
    """

    Female = "Female"
    FemaleNeuter = "FemaleNeuter"
    Male = "Male"
    MaleCryptorchid = "MaleCryptorchid"
    MaleNeuter = "MaleNeuter"
    Unknown = "Unknown"


class IcarAnimalReproductionStatusType(Enum):
    """
    Enumeration for different possible reproduction status of an animal.
    """

    Open = "Open"
    Inseminated = "Inseminated"
    Pregnant = "Pregnant"
    NotPregnant = "NotPregnant"
    Birthed = "Birthed"
    DoNotBreed = "DoNotBreed"
    PregnantMultipleFoetus = "PregnantMultipleFoetus"


class IcarAnimalLactationStatusType(Enum):
    """
    Enumeration for different possible lactation status of an animal.
    """

    Dry = "Dry"
    Lead = "Lead"
    Fresh = "Fresh"
    Early = "Early"
    Lactating = "Lactating"


class IcarProductionPurposeType(Enum):
    """
    Defines the primary product that for which this animal is bred or kept.\nIf animals are kept for breeding or live trade (sale), specify the end purpose of that breeding/trade.\n
     - Meat corresponds to UNSPC 50111500 Minimally processed meat and poultry products\n - Milk corresponds to UNSPC 50203200 Raw milk products from live animals\n - Wool corresponds to UNSPC 11131506 Unprocessed wool
    """

    Meat = "Meat"
    Milk = "Milk"
    Wool = "Wool"


class IcarSetPurposeType(Enum):
    """
    Describes the purpose of a set of animals.
    """

    Enclosure = "Enclosure"
    Feeding = "Feeding"
    Finishing = "Finishing"
    Growing = "Growing"
    Health = "Health"
    Lactation = "Lactation"
    Movement = "Movement"
    Rearing = "Rearing"
    Reproduction = "Reproduction"
    Session = "Session"
    Other = "Other"


class IcarDiagnosisStageType(Enum):
    """
    Enumeration for stage of disease diagnosis.
    """

    Early = "Early"
    Acute = "Acute"
    SubAcute = "SubAcute"
    Chronic = "Chronic"
    AcuteOnChronic = "AcuteOnChronic"
    EndStage = "EndStage"
    Other = "Other"


class IcarDiagnosisSeverityType(Enum):
    """
    Enumeration for clinical severity of disease diagnosis.
    """

    Light = "Light"
    Moderate = "Moderate"
    Severe = "Severe"


class IcarPositionOnAnimalType(Enum):
    """
    Enumeration for the position on the animal where the diagnosis or treatment occurred.
    """

    LegsFrontLeft = "LegsFrontLeft"
    LegsFrontRight = "LegsFrontRight"
    LegsRearLeft = "LegsRearLeft"
    LegsRearRight = "LegsRearRight"
    UdderFrontLeft = "UdderFrontLeft"
    UdderFrontRight = "UdderFrontRight"
    UdderRearLeft = "UdderRearLeft"
    UdderRearRight = "UdderRearRight"
    OvariesLeft = "OvariesLeft"
    OvariesRight = "OvariesRight"
    OvariesUnknown = "OvariesUnknown"
    Neck = "Neck"
    Head = "Head"
    Mouth = "Mouth"
    Back = "Back"
    Testes = "Testes"
    Other = "Other"


class IcarWithdrawalProductType(Enum):
    """
    Categorises the types of products to which withdrawal periods may apply. These categories are generalised from NOAH/ACVM/FDA/Codex Alimentus.
    """

    Meat = "Meat"
    Milk = "Milk"
    Eggs = "Eggs"
    Honey = "Honey"
    Velvet = "Velvet"
    Fibre = "Fibre"
    Other = "Other"


class UncefactDoseUnitsType(Enum):
    """
    Subset of units that are helpful for medicine doses from UN/CEFACT trade facilitation recommendation 20.
    See https://unece.org/trade/uncefact/cl-recommendations#ui-id-17
    """

    MLT = "MLT"
    LTR = "LTR"
    MGM = "MGM"
    GRM = "GRM"
    XTU = "XTU"
    XVI = "XVI"
    XAR = "XAR"
    XCQ = "XCQ"
    GJ = "GJ"
    GL = "GL"
    GRN = "GRN"
    L19 = "L19"
    NA = "NA"
    SYR = "SYR"
    WW = "WW"
    TU = "TU"
    EA = "EA"


class PlanOrActual(Enum):
    """
    Indicator showing if the attributes in the course Summary are actual information for the treatments or the plan
    """

    Plan = "Plan"
    Actual = "Actual"


class IcarAnimalHealthStatusType(Enum):
    """
    Defines the health-status of the animal.
    """

    Healthy = "Healthy"
    Suspicious = "Suspicious"
    Ill = "Ill"
    InTreatment = "InTreatment"
    ToBeCulled = "ToBeCulled"


class IcarAttentionCategoryType(Enum):
    """
    Defines a category of device messages that may allow filtering of alerts.
    """

    Behaviour = "Behaviour"
    Environment = "Environment"
    Health = "Health"
    Reproduction = "Reproduction"
    DeviceIssue = "DeviceIssue"
    Weight = "Weight"
    Other = "Other"


class IcarAttentionCauseType(Enum):
    """
    Defines causes of alerts from devices.
    """

    Activity = "Activity"
    AnimalTemperature = "AnimalTemperature"
    AnimalTemperatureDecrease = "AnimalTemperatureDecrease"
    AnimalTemperatureIncrease = "AnimalTemperatureIncrease"
    BodyCondition = "BodyCondition"
    EatingLess = "EatingLess"
    EnvironmentTemperature = "EnvironmentTemperature"
    Disturbance = "Disturbance"
    Health = "Health"
    HeartRate = "HeartRate"
    Inactivity = "Inactivity"
    Ketosis = "Ketosis"
    Lameness = "Lameness"
    Location = "Location"
    LowerRumination = "LowerRumination"
    LyingTooLong = "LyingTooLong"
    LyingTooShort = "LyingTooShort"
    Mastitis = "Mastitis"
    MobilityScore = "MobilityScore"
    NoMovement = "NoMovement"
    Parturition = "Parturition"
    PostParturitionRisk = "PostParturitionRisk"
    ProlongedParturition = "ProlongedParturition"
    RespirationRate = "RespirationRate"
    Standing = "Standing"
    StandingUp = "StandingUp"
    Walking = "Walking"
    Heat = "Heat"
    LowBattery = "LowBattery"
    Offline = "Offline"
    UnderWeight = "UnderWeight"
    OverWeight = "OverWeight"
    AtTargetWeight = "AtTargetWeight"
    Other = "Other"
    Undefined = "Undefined"


class IcarAttentionPriorityType(Enum):
    """
    Defines the relative priority of alerts.
    """

    Informational = "Informational"
    Normal = "Normal"
    Urgent = "Urgent"
    Critical = "Critical"


class IcarStatisticsPurposeType(Enum):
    """
    The kind or purpose of the statistics provided (can be expanded).
    """

    TestDay = "TestDay"
    Feeding = "Feeding"
    Reproduction = "Reproduction"
    BreedingValues = "BreedingValues"
    TypeClassification = "TypeClassification"
    Registration = "Registration"


class IcarGroupType(Enum):
    """
    The type of group for which statistics are provided (can be expanded).
    """

    Herd = "Herd"
    LactationNumber = "LactationNumber"
    DaysInMilk = "DaysInMilk"
    AnimalSet = "AnimalSet"


class IcarAggregationType(Enum):
    """
    The type of aggregation. In addition to obvious statistical terms, Range is the difference between min and max, and index is a computed index value.
    """

    Average = "Average"
    Sum = "Sum"
    StDev = "StDev"
    Min = "Min"
    Max = "Max"
    Count = "Count"
    Range = "Range"
    Index = "Index"


class IcarDurationType(Enum):
    """
    ISO8601 durations used in aggregations:
     (1 day - typically from midnight, 1 hour, 24 hour period, 96 hour period, 1 week, 1 month)
    """

    P1D = "P1D"
    PT1H = "PT1H"
    PT24H = "PT24H"
    PT96H = "PT96H"
    P1W = "P1W"
    P1M = "P1M"


class IcarMilkingTypeCode(Enum):
    """
    The type of milking (manual or automated)
    """

    Manual = "Manual"
    Automated = "Automated"


class UnitCode2(Enum):
    """
    UN/CEFACT Common Code for Units of Measurement.
    """

    KGM = "KGM"


class IcarBottleIdentifierType(Enum):
    """
    The type of bottle identifiertype according to ICAR_BottleIdentifierCode
    """

    BRC = "BRC"
    RFD = "RFD"


class IcarValidSampleFillingIndicatorType(Enum):
    """
    Validity of sample based on milk volume: 0=success (>80% expected milk), 1=incomplete (< 20% expected milk), 2=completed (with between 20-80% expected milk).
    """

    field_0 = "0"
    field_1 = "1"
    field_2 = "2"


class IcarQuarterId(Enum):
    """
    the unique id of the quarter milking
    """

    LF = "LF"
    RF = "RF"
    LR = "LR"
    RR = "RR"


class IcarMilkingRemarksType(Enum):
    """
    Enumeration for different possible milking-remarks.
    """

    AnimalSick = "AnimalSick"
    MilkingIncomplete = "MilkingIncomplete"
    TeatSeparated = "TeatSeparated"
    MilkedSeparately = "MilkedSeparately"
    SamplingFailed = "SamplingFailed"


class IcarTestDayCodeType(Enum):
    """
    The test day code, indicating a status of the cow on the test day.
    """

    Dry = "Dry"
    SamplingImpossible = "SamplingImpossible"
    Sick = "Sick"


class UnitCode3(Enum):
    """
    UN/CEFACT Common Code for Units of Measurement.
    """

    KGM = "KGM"
    LBR = "LBR"


class IcarLactationType(Enum):
    """
    Enumeration for lactation type.
    """

    Normal = "Normal"
    field_100Days = "100Days"
    field_200Days = "200Days"
    field_305Days = "305Days"
    field_365Days = "365Days"


class IcarMilkRecordingProtocolType(Enum):
    """
    Enumeration for the milk recording protocol.
    """

    A_OfficialMRORepresentative = "A-OfficialMRORepresentative"
    B_HerdOwnerOrNominee = "B-HerdOwnerOrNominee"
    C_Both = "C-Both"


class IcarMilkRecordingSchemeType(Enum):
    """
    Enumeration for the milk recording scheme
    """

    AllMilkingsAtTestday = "AllMilkingsAtTestday"
    AllMilkingsInPeriod = "AllMilkingsInPeriod"
    OneMilkingAtTestday = "OneMilkingAtTestday"


class IcarMilkingsPerDayType(Enum):
    """
    Enumeration for the milkings per day.
    """

    field_1 = "1"
    field_2 = "2"
    field_3 = "3"
    field_4 = "4"
    Robot = "Robot"


class IcarMilkSamplingSchemeType(Enum):
    """
    Enumeration for the different milk sampling schemes.
    """

    ProportionalSizeSamplingOfAllMilkings = "ProportionalSizeSamplingOfAllMilkings"
    ConstantSizeSamplingOfAllMilkings = "ConstantSizeSamplingOfAllMilkings"
    AlternateSampling = "AlternateSampling"
    CorrectedSampling = "CorrectedSampling"
    OneMilkingSampleInAMS = "OneMilkingSampleInAMS"
    MulitpleMilkingSampleInAMS = "MulitpleMilkingSampleInAMS"


class IcarMilkSamplingMomentType(Enum):
    """
    Enumeration for different possible milk sampling moments.
    """

    Composite = "Composite"
    Morning = "Morning"
    Evening = "Evening"


class IcarMilkingType(Enum):
    """
    Enumeration for different possible types of milking.
    """

    OfficialMilkResultSuppliedByMRO = "OfficialMilkResultSuppliedByMRO"
    MeasureByICARApprovedEquipment = "MeasureByICARApprovedEquipment"
    MeasureByNotApprovedEquipment = "MeasureByNotApprovedEquipment"


class IcarWeightMethodType(Enum):
    """
    Method by which the weight is observed.
     Includes loadcell (loadbars), girth (tape), assessed (visually), walk-over weighing,
    prediction, imaging (camera/IR), front end weight correlated to whole body, group average (pen/sample weigh).
    """

    LoadCell = "LoadCell"
    Girth = "Girth"
    Assessed = "Assessed"
    WalkOver = "WalkOver"
    Predicted = "Predicted"
    Imaged = "Imaged"
    FrontEndCorrelated = "FrontEndCorrelated"
    GroupAverage = "GroupAverage"


class IcarBreedingValueCalculationType(Enum):
    """
    Enumeration for identifying the mathematical calculation method used to calculate breeding values.
    """

    BreedingValue = "BreedingValue"
    ParentAverageBreedingValue = "ParentAverageBreedingValue"
    GenomicBreedingValue = "GenomicBreedingValue"
    ConvertedBreedingValue = "ConvertedBreedingValue"
    Other = "Other"


class IcarConformationTraitGroupType(Enum):
    """
    Enumeration for the type of trait.
    """

    Composite = "Composite"
    Linear = "Linear"


class IcarConformationTraitType(Enum):
    """
    The type of conformation trait according to ICAR guidelines
    """

    Angularity = "Angularity"
    BackLength = "BackLength"
    BackWidth = "BackWidth"
    BodyConditionScore = "BodyConditionScore"
    BodyDepth = "BodyDepth"
    BodyLength = "BodyLength"
    BoneStructure = "BoneStructure"
    CentralLigament = "CentralLigament"
    ChestDepth = "ChestDepth"
    ChestWidth = "ChestWidth"
    ClawAngle = "ClawAngle"
    DairyStrength = "DairyStrength"
    FeetLegs = "FeetLegs"
    FinalScore = "FinalScore"
    FlankDepth = "FlankDepth"
    FootAngle = "FootAngle"
    ForePasternsSideView = "ForePasternsSideView"
    ForeUdderAttachment = "ForeUdderAttachment"
    ForeUdderLength = "ForeUdderLength"
    Frame = "Frame"
    FrontFeetOrientation = "FrontFeetOrientation"
    FrontLegsFrontView = "FrontLegsFrontView"
    FrontTeatPlacement = "FrontTeatPlacement"
    HeightAtRump = "HeightAtRump"
    HeightAtWithers = "HeightAtWithers"
    HindPasternsSideView = "HindPasternsSideView"
    HockDevelopment = "HockDevelopment"
    LengthOfRump = "LengthOfRump"
    Locomotion = "Locomotion"
    LoinStrength = "LoinStrength"
    Muscularity = "Muscularity"
    MuscularityComposite = "MuscularityComposite"
    MuscularityShoulderSideView = "MuscularityShoulderSideView"
    MuscularityShoulderTopView = "MuscularityShoulderTopView"
    MuzzleWidth = "MuzzleWidth"
    RearLegsRearView = "RearLegsRearView"
    RearLegsSet = "RearLegsSet"
    RearLegsSideView = "RearLegsSideView"
    RearTeatPlacement = "RearTeatPlacement"
    RearUdderHeight = "RearUdderHeight"
    RearUdderWidth = "RearUdderWidth"
    RoundingOfRibs = "RoundingOfRibs"
    RumpAngle = "RumpAngle"
    RumpLength = "RumpLength"
    RumpWidth = "RumpWidth"
    SkinThickness = "SkinThickness"
    Stature = "Stature"
    TailSet = "TailSet"
    TeatDirection = "TeatDirection"
    TeatForm = "TeatForm"
    TeatLength = "TeatLength"
    TeatPlacementRearView = "TeatPlacementRearView"
    TeatPlacementSideView = "TeatPlacementSideView"
    TeatThickness = "TeatThickness"
    ThicknessOfBone = "ThicknessOfBone"
    ThicknessOfTeat = "ThicknessOfTeat"
    ThicknessOfLoin = "ThicknessOfLoin"
    ThighLength = "ThighLength"
    ThighRoundingSideView = "ThighRoundingSideView"
    ThighWidthRearView = "ThighWidthRearView"
    ThurlWidth = "ThurlWidth"
    TopLine = "TopLine"
    Type = "Type"
    Udder = "Udder"
    UdderBalance = "UdderBalance"
    UdderDepth = "UdderDepth"
    WidthAtHips = "WidthAtHips"
    WidthAtPins = "WidthAtPins"


class IcarConformationScoringMethodType(Enum):
    """
    The method of conformation scoring
    """

    Manual = "Manual"
    Automated = "Automated"


class IcarAnimalStatusType(Enum):
    """
    Defines the status of the animal either absolutely and/or with reference to the location on which it is recorded\nOff-farm signifies that the animal is no longer recorded at the location.
    """

    Alive = "Alive"
    Dead = "Dead"
    OffFarm = "OffFarm"
    Unknown = "Unknown"


class IcarAnimalRelationType(Enum):
    """
    Enumeration for parent relationships - genetic is the default, recipient and adoptive (foster) are alternatives.
    """

    Genetic = "Genetic"
    Recipient = "Recipient"
    Adoptive = "Adoptive"


class IcarRegistrationReasonType(Enum):
    """
    Enumeration for registration reason: Born, or Registered (induct existing animal).
    """

    Born = "Born"
    Registered = "Registered"


class IcarDeathReasonType(Enum):
    """
    Enumeration for death reason. Not specified in previous ADE data dictionary.
    """

    Missing = "Missing"
    Parturition = "Parturition"
    Disease = "Disease"
    Accident = "Accident"
    Consumption = "Consumption"
    Culled = "Culled"
    Other = "Other"
    Unknown = "Unknown"
    Age = "Age"
    Mastitis = "Mastitis"
    Production = "Production"
    LegOrClaw = "LegOrClaw"
    MilkingAbility = "MilkingAbility"
    Nutrition = "Nutrition"
    Fertility = "Fertility"


class IcarDeathDisposalMethodType(Enum):
    """
    Enumeration for disposal method. Not specified in previous ADE data dictionary, required by some schemes.
    """

    ApprovedService = "ApprovedService"
    Consumption = "Consumption"
    OnPremise = "OnPremise"
    Other = "Other"


class IcarDeathMethodType(Enum):
    """
    Enumeration for method of death.
     Note: Some organisations will use Euthanized and Culled as synonyms. Culling may be euthanasia for disease control purposes.
     Culling is also used to describe live animal departures (out of this scope).
    """

    Perished = "Perished"
    Slaughter = "Slaughter"
    Culled = "Culled"
    Theft = "Theft"
    Lost = "Lost"
    Accident = "Accident"
    Euthanized = "Euthanized"
    Other = "Other"


class IcarArrivalReasonType(Enum):
    """
    Enumeration for arrival reason. Not specified in previous ADE data dictionary.
    """

    Purchase = "Purchase"
    InternalTransfer = "InternalTransfer"
    Imported = "Imported"
    StudService = "StudService"
    StudServiceReturn = "StudServiceReturn"
    Slaughter = "Slaughter"
    Agistment = "Agistment"
    AgistmentReturn = "AgistmentReturn"
    Show = "Show"
    ShowReturn = "ShowReturn"
    Sale = "Sale"
    SaleReturn = "SaleReturn"
    Other = "Other"


class IcarDepartureKindType(Enum):
    """
    Enumeration for the kind of departure. Type of destination or transfer.
    """

    InternalTransfer = "InternalTransfer"
    Export = "Export"
    Slaughter = "Slaughter"
    Newborn = "Newborn"
    StudService = "StudService"
    StudServiceReturn = "StudServiceReturn"
    Agistment = "Agistment"
    AgistmentReturn = "AgistmentReturn"
    Show = "Show"
    ShowReturn = "ShowReturn"
    Sale = "Sale"
    SaleReturn = "SaleReturn"
    Other = "Other"


class IcarDepartureReasonType(Enum):
    """
    Enumeration for departure cause. Not specified in previous ADE data dictionary.
    """

    Age = "Age"
    Superfluous = "Superfluous"
    Slaughter = "Slaughter"
    Sale = "Sale"
    Newborn = "Newborn"
    LegOrClaw = "LegOrClaw"
    Nutrition = "Nutrition"
    Parturition = "Parturition"
    Mastitis = "Mastitis"
    Fertility = "Fertility"
    Health = "Health"
    Production = "Production"
    MilkingAbility = "MilkingAbility"
    BadType = "BadType"
    Behaviour = "Behaviour"
    Other = "Other"
    Unknown = "Unknown"


class IcarReproPregnancyMethodType(Enum):
    """
    The method of pregnancy determination.
    """

    Echography = "Echography"
    Palpation = "Palpation"
    Blood = "Blood"
    Milk = "Milk"
    Visual = "Visual"
    Other = "Other"


class IcarReproPregnancyResultType(Enum):
    """
    The result of pregnancy diagnosis (empty/pregnant).
    """

    Empty = "Empty"
    Pregnant = "Pregnant"
    Multiple = "Multiple"
    Unknown = "Unknown"


class IcarReproHeatDetectionMethodType(Enum):
    """
    The method of detecting the heat of an animal
    """

    Chemical = "Chemical"
    Visual = "Visual"
    Pedometer = "Pedometer"
    Collar = "Collar"
    EarTag = "EarTag"
    Bolus = "Bolus"
    Other = "Other"


class IcarReproHeatCertaintyType(Enum):
    """
    The certainty of a specific heat. 'Potential' is very early in the heat cycle, e.g. first 2 hours, followed by 'Suspect', until the animal is most likely 'InHeat'.
    """

    InHeat = "InHeat"
    Suspect = "Suspect"
    Potential = "Potential"


class IcarReproHeatSignType(Enum):
    """
    The signs of the heat (Slime,Clear slime,Interested in other animals,Stands under,Bawling,Blood)
    """

    Slime = "Slime"
    ClearSlime = "ClearSlime"
    InterestedInOtherAnimals = "InterestedInOtherAnimals"
    Bawling = "Bawling"
    Blood = "Blood"
    StandsUnder = "StandsUnder"


class IcarReproHeatIntensityType(Enum):
    """
    The intensity of the heat (Very weak,Weak,Normal,Strong,Very strong)
    """

    VeryWeak = "VeryWeak"
    Weak = "Weak"
    Normal = "Normal"
    Strong = "Strong"
    VeryStrong = "VeryStrong"


class IcarReproInseminationType(Enum):
    """
    The method of insemination (natural service, run with bull, insemination, implantation
    """

    NaturalService = "NaturalService"
    RunWithBull = "RunWithBull"
    Insemination = "Insemination"
    Implantation = "Implantation"


class IcarReproSemenPreservationType(Enum):
    """
    Method of semen preservation (liquid usually with extender, frozen)
    """

    Liquid = "Liquid"
    Frozen = "Frozen"


class IcarReproCalvingEaseType(Enum):
    """
    Enumeration for calving ease. In the order they are listed, these correspond to INTERBEEF codes 1 to 5
    """

    EasyUnassisted = "EasyUnassisted"
    EasyAssisted = "EasyAssisted"
    DifficultExtraAssistance = "DifficultExtraAssistance"
    DifficultVeterinaryCare = "DifficultVeterinaryCare"
    CaesareanOrSurgery = "CaesareanOrSurgery"


class IcarParturitionBirthStatusType(Enum):
    """
    Enumeration for the widely used progeny birth statuses.
    """

    Alive = "Alive"
    Stillborn = "Stillborn"
    Aborted = "Aborted"
    DiedBeforeTaggingDate = "DiedBeforeTaggingDate"
    DiedAfterTaggingDate = "DiedAfterTaggingDate"
    SlaughteredAtBirth = "SlaughteredAtBirth"
    EuthanisedAtBirth = "EuthanisedAtBirth"


class IcarParturitionBirthSizeType(Enum):
    """
    Enumeration for the widely used progeny birth sizes.
    """

    ExtraSmall = "ExtraSmall"
    Small = "Small"
    Average = "Average"
    Large = "Large"
    ExtraLarge = "ExtraLarge"


class IcarRecommendationType(Enum):
    """
    the type of recommendation (SireRecommended, RecommendationImpossible, BeefSire, NoBreedingSire
    """

    SireRecommended = "SireRecommended"
    RecommendationImpossible = "RecommendationImpossible"
    BeefSire = "BeefSire"
    NoBreedingSire = "NoBreedingSire"


class IcarReproEmbryoFlushingMethodType(Enum):
    """
    The method of embryo flushing.
    """

    OPU_IVF = "OPU-IVF"
    Superovulation = "Superovulation"
