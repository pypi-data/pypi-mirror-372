from __future__ import annotations

from typing import List, Optional

from pydantic import AnyUrl, BaseModel, Field, RootModel

from . import resources


class IcarErrorCollection(BaseModel):
    """
    A collection of RFC7807 compliant problem responses for JSON APIs.
    """

    errors: Optional[List[resources.IcarResponseMessageResource]] = None


class View(BaseModel):
    """
    Information about the current view or page of the collection
    """

    totalItems: Optional[int] = Field(
        None, description="Provides the number of items in the collection, if known."
    )
    totalPages: Optional[int] = Field(
        None, description="Provides the number of pages in the collection, if known."
    )
    pageSize: Optional[int] = Field(
        None,
        description="If non-zero, specifies the default number of items returned per page.",
    )
    currentPage: Optional[int] = Field(
        None,
        description="Optionally identifies the current page for display purposes, if returned.",
    )
    first: Optional[AnyUrl] = Field(
        None,
        description="Link to the first page of the collection. Link relation: first.",
    )
    next: Optional[AnyUrl] = Field(
        None,
        description="Link to the next page of the collection, if any. Link relation: next.",
    )
    prev: Optional[AnyUrl] = Field(
        None,
        description="Link to the previous page of the collection, if any. Link relation: prev.",
    )
    last: Optional[AnyUrl] = Field(
        None,
        description="Link to the last page of the collection, if any. Link relation: last.",
    )


class IcarResourceCollection(BaseModel):
    """
    Base class for a collection of items such as animals, devices, or events. Use allOf to add an items array of the right type.
    """

    view: Optional[View] = Field(
        None, description="Information about the current view or page of the collection"
    )


class IcarAnimalSetCollection(IcarResourceCollection):
    """
    Represents a collection of animal sets. Based on icarResourceCollection to provide paging etc.
    """

    member: Optional[List[resources.IcarAnimalSetResource]] = Field(
        None,
        description="As per JSON-LD Hydra syntax, member provides the array of objects, in this case animal sets.",
    )


class IcarAnimalSetArray(RootModel[List[resources.IcarAnimalSetResource]]):
    root: List[resources.IcarAnimalSetResource]


class IcarAnimalSetJoinEventCollection(IcarResourceCollection):
    """
    Represents a collection of animal set join events. Based on icarResourceCollection to provide paging etc.
    """

    member: Optional[List[resources.IcarAnimalSetJoinEventResource]] = Field(
        None,
        description="As per JSON-LD Hydra syntax, member provides the array of objects, in this case animal set join events.",
    )


class IcarAnimalSetJoinEventArray(
    RootModel[List[resources.IcarAnimalSetJoinEventResource]]
):
    root: List[resources.IcarAnimalSetJoinEventResource]


class IcarAnimalSetLeaveEventCollection(IcarResourceCollection):
    """
    Represents a collection of animal set leave events. Based on icarResourceCollection to provide paging etc.
    """

    member: Optional[List[resources.IcarAnimalSetLeaveEventResource]] = Field(
        None,
        description="As per JSON-LD Hydra syntax, member provides the array of objects, in this case animal set leave events.",
    )


class IcarAnimalSetLeaveEventArray(
    RootModel[List[resources.IcarAnimalSetLeaveEventResource]]
):
    root: List[resources.IcarAnimalSetLeaveEventResource]


class IcarDeviceCollection(IcarResourceCollection):
    """
    Represents a collection of devices. Based on icarResourceCollection to provide paging etc.
    """

    member: Optional[List[resources.IcarDeviceResource]] = Field(
        None,
        description="As per JSON-LD Hydra syntax, member provides the array of objects, in this case weight events.",
    )


class IcarDeviceArray(RootModel[List[resources.IcarDeviceResource]]):
    root: List[resources.IcarDeviceResource]


class IcarInventoryTransactionCollection(IcarResourceCollection):
    """
    Represents a collection of inventory transactions. Based on icarResourceCollection to provide paging etc.
    """

    member: Optional[List[resources.IcarInventoryTransactionResource]] = Field(
        None,
        description="As per JSON-LD Hydra syntax, member provides the array of objects, in this case inventory transactions.",
    )


class IcarInventoryTransactionArray(
    RootModel[List[resources.IcarInventoryTransactionResource]]
):
    root: List[resources.IcarInventoryTransactionResource]


class IcarRemarkEventCollection(IcarResourceCollection):
    """
    Represents a collection of remark (or note) events. Based on icarResourceCollection to provide paging etc.
    """

    member: Optional[List[resources.IcarRemarkEventResource]] = Field(
        None,
        description="As per JSON-LD Hydra syntax, member provides the array of objects, in this case remark events.",
    )


class IcarRemarkEventArray(RootModel[List[resources.IcarRemarkEventResource]]):
    root: List[resources.IcarRemarkEventResource]


class IcarTestDayCollection(IcarResourceCollection):
    """
    Represents a collection of test days. Based on icarResourceCollection to provide paging etc.
    """

    member: Optional[List[resources.IcarTestDayResource]] = Field(
        None,
        description="As per JSON-LD Hydra syntax, member provides the array of objects, in this case test days.",
    )


class IcarTestDayArray(RootModel[List[resources.IcarTestDayResource]]):
    root: List[resources.IcarTestDayResource]


class IcarLactationStatusObservedEventCollection(IcarResourceCollection):
    """
    Represents a collection of animal lactation status observation events. Based on icarResourceCollection to provide paging etc.
    """

    member: Optional[List[resources.IcarLactationStatusObservedEventResource]] = Field(
        None,
        description="As per JSON-LD Hydra syntax, member provides the array of objects, in this case lactation status events.",
    )


class IcarLactationStatusObservedEventArray(
    RootModel[List[resources.IcarLactationStatusObservedEventResource]]
):
    root: List[resources.IcarLactationStatusObservedEventResource]


class IcarMilkingDryOffEventCollection(IcarResourceCollection):
    """
    Represents a collection of animal drying off events. Based on icarResourceCollection to provide paging etc.
    """

    member: Optional[List[resources.IcarMilkingDryOffEventResource]] = Field(
        None,
        description="As per JSON-LD Hydra syntax, member provides the array of objects, in this case weight events.",
    )


class IcarMilkingDryOffEventArray(
    RootModel[List[resources.IcarMilkingDryOffEventResource]]
):
    root: List[resources.IcarMilkingDryOffEventResource]


class IcarReproAbortionEventCollection(IcarResourceCollection):
    """
    Represents a collection of animal abortion events. Based on icarResourceCollection to provide paging etc.
    """

    member: Optional[List[resources.IcarReproAbortionEventResource]] = Field(
        None,
        description="As per JSON-LD Hydra syntax, member provides the array of objects, in this case abortion events.",
    )


class IcarReproAbortionEventArray(
    RootModel[List[resources.IcarReproAbortionEventResource]]
):
    root: List[resources.IcarReproAbortionEventResource]


class IcarReproDoNotBreedEventCollection(IcarResourceCollection):
    """
    Represents a collection of do not breed events. Based on icarResourceCollection to provide paging etc.
    """

    member: Optional[List[resources.IcarReproDoNotBreedEventResource]] = Field(
        None,
        description="As per JSON-LD Hydra syntax, member provides the array of objects, in this case do not breed events.",
    )


class IcarReproDoNotBreedEventArray(
    RootModel[List[resources.IcarReproDoNotBreedEventResource]]
):
    root: List[resources.IcarReproDoNotBreedEventResource]


class IcarGestationCollection(IcarResourceCollection):
    """
    Represents a collection of gestations. Based on icarResourceCollection to provide paging etc.
    """

    member: Optional[List[resources.IcarGestationResource]] = Field(
        None,
        description="As per JSON-LD Hydra syntax, member provides the array of objects, in this case gestations.",
    )


class IcarGestationArray(RootModel[List[resources.IcarGestationResource]]):
    root: List[resources.IcarGestationResource]


class IcarReproStatusObservedEventCollection(IcarResourceCollection):
    """
    Represents a collection of animal reproductive status observation events. Based on icarResourceCollection to provide paging etc.
    """

    member: Optional[List[resources.IcarReproStatusObservedEventResource]] = Field(
        None,
        description="As per JSON-LD Hydra syntax, member provides the array of objects, in this case reproductive status events.",
    )


class IcarReproStatusObservedEventArray(
    RootModel[List[resources.IcarReproStatusObservedEventResource]]
):
    root: List[resources.IcarReproStatusObservedEventResource]


class BatchResults(RootModel[List[resources.IcarBatchResult]]):
    root: List[resources.IcarBatchResult]


class IcarFeedCollection(IcarResourceCollection):
    """
    Represents a collection of feeds. Based on icarResourceCollection to provide paging etc.
    """

    member: Optional[List[resources.IcarFeedResource]] = Field(
        None,
        description="As per JSON-LD Hydra syntax, member provides the array of objects, in this case feeds.",
    )


class IcarFeedArray(RootModel[List[resources.IcarFeedResource]]):
    root: List[resources.IcarFeedResource]


class IcarRationCollection(IcarResourceCollection):
    """
    Represents a collection of rations. Based on icarResourceCollection to provide paging etc.
    """

    member: Optional[List[resources.IcarRationResource]] = Field(
        None,
        description="As per JSON-LD Hydra syntax, member provides the array of objects, in this case rations.",
    )


class IcarRationArray(RootModel[List[resources.IcarRationResource]]):
    root: List[resources.IcarRationResource]


class IcarFeedIntakeEventCollection(IcarResourceCollection):
    """
    Represents a collection of feed intakes. Based on icarResourceCollection to provide paging etc.
    """

    member: Optional[List[resources.IcarFeedIntakeEventResource]] = Field(
        None,
        description="As per JSON-LD Hydra syntax, member provides the array of objects, in this case feed intakes.",
    )


class IcarFeedIntakeEventArray(RootModel[List[resources.IcarFeedIntakeEventResource]]):
    root: List[resources.IcarFeedIntakeEventResource]


class IcarFeedRecommendationCollection(IcarResourceCollection):
    """
    Represents a collection of feed recommendations. Based on icarResourceCollection to provide paging etc.
    """

    member: Optional[List[resources.IcarFeedRecommendationResource]] = Field(
        None,
        description="As per JSON-LD Hydra syntax, member provides the array of objects, in this case feed recommendations.",
    )


class IcarFeedRecommendationArray(
    RootModel[List[resources.IcarFeedRecommendationResource]]
):
    root: List[resources.IcarFeedRecommendationResource]


class IcarFeedStorageCollection(IcarResourceCollection):
    """
    Represents a collection of feed storage devices. Based on icarResourceCollection to provide paging etc.
    """

    member: Optional[List[resources.IcarFeedStorageResource]] = Field(
        None,
        description="As per JSON-LD Hydra syntax, member provides the array of objects, in this case feed storage devices.",
    )


class IcarFeedStorageArray(RootModel[List[resources.IcarFeedStorageResource]]):
    root: List[resources.IcarFeedStorageResource]


class IcarFeedReportCollection(IcarResourceCollection):
    """
    Represents a collection of feed reports. Based on icarResourceCollection to provide paging etc.
    """

    member: Optional[List[resources.IcarFeedReportResource]] = Field(
        None,
        description="As per JSON-LD Hydra syntax, member provides the array of objects, in this case feed reports.",
    )


class IcarFeedTransactionCollection(IcarResourceCollection):
    """
    Represents a collection of feed inventory transactions. Based on icarResourceCollection to provide paging etc.
    """

    member: Optional[List[resources.IcarFeedTransactionResource]] = Field(
        None,
        description="As per JSON-LD Hydra syntax, member provides the array of objects, in this case inventory transactions.",
    )


class IcarFeedTransactionArray(RootModel[List[resources.IcarFeedTransactionResource]]):
    root: List[resources.IcarFeedTransactionResource]


class IcarGroupFeedingEventCollection(IcarResourceCollection):
    """
    Represents a collection of feed intakes. Based on icarResourceCollection to provide paging etc.
    """

    member: Optional[List[resources.IcarGroupFeedingEventResource]] = Field(
        None,
        description="As per JSON-LD Hydra syntax, member provides the array of objects, in this case group feeding events.",
    )


class IcarGroupFeedingEventArray(
    RootModel[List[resources.IcarGroupFeedingEventResource]]
):
    root: List[resources.IcarGroupFeedingEventResource]


class IcarDiagnosisEventCollection(IcarResourceCollection):
    """
    Represents a collection of animal health diagnosis events. Based on icarResourceCollection to provide paging etc.
    """

    member: Optional[List[resources.IcarDiagnosisEventResource]] = Field(
        None,
        description="As per JSON-LD Hydra syntax, member provides the array of objects, in this case diagnosis events.",
    )


class IcarDiagnosisEventArray(RootModel[List[resources.IcarDiagnosisEventResource]]):
    root: List[resources.IcarDiagnosisEventResource]


class IcarTreatmentEventCollection(IcarResourceCollection):
    """
    Represents a collection of animal health treatment events. Based on icarResourceCollection to provide paging etc.
    """

    member: Optional[List[resources.IcarTreatmentEventResource]] = Field(
        None,
        description="As per JSON-LD Hydra syntax, member provides the array of objects, in this case treatment events.",
    )


class IcarTreatmentEventArray(RootModel[List[resources.IcarTreatmentEventResource]]):
    root: List[resources.IcarTreatmentEventResource]


class IcarGroupTreatmentEventCollection(IcarResourceCollection):
    """
    Represents a collection of group health treatment events. Based on icarResourceCollection to provide paging etc.
    """

    member: Optional[List[resources.IcarGroupTreatmentEventResource]] = Field(
        None, description="Provides the array of objects, in this case weighing events."
    )


class IcarGroupTreatmentEventArray(
    RootModel[List[resources.IcarGroupTreatmentEventResource]]
):
    root: List[resources.IcarGroupTreatmentEventResource]


class IcarTreatmentProgramEventCollection(IcarResourceCollection):
    """
    Represents a collection of animal health treatment program events. Based on icarResourceCollection to provide paging etc.
    """

    member: Optional[List[resources.IcarTreatmentProgramEventResource]] = Field(
        None,
        description="As per JSON-LD Hydra syntax, member provides the array of objects, in this case treatment program events.",
    )


class IcarTreatmentProgramEventArray(
    RootModel[List[resources.IcarTreatmentProgramEventResource]]
):
    root: List[resources.IcarTreatmentProgramEventResource]


class IcarHealthStatusObservedEventCollection(IcarResourceCollection):
    """
    Represents a collection of animal health status observation events. Based on icarResourceCollection to provide paging etc.
    """

    member: Optional[List[resources.IcarHealthStatusObservedEventResource]] = Field(
        None,
        description="As per JSON-LD Hydra syntax, member provides the array of objects, in this case lactation status events.",
    )


class IcarHealthStatusObservedArray(
    RootModel[List[resources.IcarHealthStatusObservedEventResource]]
):
    root: List[resources.IcarHealthStatusObservedEventResource]


class IcarMedicineTransactionCollection(IcarResourceCollection):
    """
    Represents a collection of medicine inventory transactions. Based on icarResourceCollection to provide paging etc.
    """

    member: Optional[List[resources.IcarMedicineTransactionResource]] = Field(
        None,
        description="As per JSON-LD Hydra syntax, member provides the array of objects, in this case inventory transactions.",
    )


class IcarMedicineTransactionArray(
    RootModel[List[resources.IcarMedicineTransactionResource]]
):
    root: List[resources.IcarMedicineTransactionResource]


class IcarAttentionEventCollection(IcarResourceCollection):
    """
    Represents a collection of attention events generated by devices. Based on icarResourceCollection to provide paging etc.
    """

    member: Optional[List[resources.IcarAttentionEventResource]] = Field(
        None,
        description="As per JSON-LD Hydra syntax, member provides the array of objects, in this case attention events.",
    )


class IcarAttentionEventArray(RootModel[List[resources.IcarAttentionEventResource]]):
    root: List[resources.IcarAttentionEventResource]


class IcarStatisticsCollection(IcarResourceCollection):
    """
    Represents a collection of statistics. Based on icarResourceCollection to provide paging etc.
    """

    member: Optional[List[resources.IcarStatisticsResource]] = Field(
        None,
        description="As per JSON-LD Hydra syntax, member provides the array of objects, in this case statistics.",
    )


class IcarGroupPositionObservationEventCollection(IcarResourceCollection):
    """
    Represents a collection of group position observation events.
    """

    member: Optional[List[resources.IcarGroupPositionObservationEventResource]] = Field(
        None,
        description="As per JSON-LD Hydra syntax, member provides the array of objects, in this case group position observation events.",
    )


class IcarGroupPositionObservationEventArray(
    RootModel[List[resources.IcarGroupPositionObservationEventResource]]
):
    root: List[resources.IcarGroupPositionObservationEventResource]


class IcarPositionObservationEventCollection(IcarResourceCollection):
    """
    Represents a collection of animal position observation events.
    """

    member: Optional[List[resources.IcarPositionObservationEventResource]] = Field(
        None,
        description="As per JSON-LD Hydra syntax, member provides the array of objects, in this case position observation events.",
    )


class IcarPositionObservationEventArray(
    RootModel[List[resources.IcarPositionObservationEventResource]]
):
    root: List[resources.IcarPositionObservationEventResource]


class IcarObservationSummaryCollection(IcarResourceCollection):
    """
    Represents a collection of observation summary statistics. Based on icarResourceCollection to provide paging etc.
    """

    member: Optional[List[resources.IcarObservationSummaryResource]] = Field(
        None,
        description="As per JSON-LD Hydra syntax, member provides the array of objects, in this case observation summary statistics.",
    )


class IcarObservationSummaryResourceArray(
    RootModel[List[resources.IcarObservationSummaryResource]]
):
    root: List[resources.IcarObservationSummaryResource]


class IcarMilkingVisitEventCollection(IcarResourceCollection):
    """
    Represents a collection of animal milking visit events. Based on icarResourceCollection to provide paging etc.
    """

    member: Optional[List[resources.IcarMilkingVisitEventResource]] = Field(
        None,
        description="As per JSON-LD Hydra syntax, member provides the array of objects, in this case milking visit events.",
    )


class IcarMilkingVisitEventArray(
    RootModel[List[resources.IcarMilkingVisitEventResource]]
):
    root: List[resources.IcarMilkingVisitEventResource]


class IcarTestDayResultEventCollection(IcarResourceCollection):
    """
    Represents a collection of test day result events. Based on icarResourceCollection to provide paging etc.
    """

    member: Optional[List[resources.IcarTestDayResultEventResource]] = Field(
        None,
        description="As per JSON-LD Hydra syntax, member provides the array of objects, in this case test day result events.",
    )


class IcarTestDayResultEventArray(
    RootModel[List[resources.IcarTestDayResultEventResource]]
):
    root: List[resources.IcarTestDayResultEventResource]


class IcarDailyMilkingAveragesCollection(IcarResourceCollection):
    """
    Represents a collection of daily milking averages per animal. Based on icarResourceCollection to provide paging etc.
    """

    member: Optional[List[resources.IcarDailyMilkingAveragesResource]] = Field(
        None,
        description="As per JSON-LD Hydra syntax, member provides the array of objects, in this case test day result events.",
    )


class IcarMilkPredictionsCollection(IcarResourceCollection):
    """
    Represents a collection of milk predictions per animal. Based on icarResourceCollection to provide paging etc.
    """

    member: Optional[List[resources.IcarMilkPredictionResource]] = Field(
        None,
        description="As per JSON-LD Hydra syntax, member provides the array of objects, in this case milk prediction events.",
    )


class IcarLactationCollection(IcarResourceCollection):
    """
    Represents a collection of lactations. Based on icarResourceCollection to provide paging etc.
    """

    member: Optional[List[resources.IcarLactationResource]] = Field(
        None,
        description="As per JSON-LD Hydra syntax, member provides the array of objects, in this case lactations.",
    )


class IcarWithdrawalEventCollection(IcarResourceCollection):
    """
    Represents a collection of withdrawals. Based on icarResourceCollection to provide paging etc.
    """

    member: Optional[List[resources.IcarWithdrawalEventResource]] = Field(
        None,
        description="As per JSON-LD Hydra syntax, member provides the array of objects, in this case lactation status events.",
    )


class IcarWeightEventCollection(IcarResourceCollection):
    """
    Represents a collection of animal weight events. Based on icarResourceCollection to provide paging etc.
    """

    member: Optional[List[resources.IcarWeightEventResource]] = Field(
        None,
        description="As per JSON-LD Hydra syntax, member provides the array of objects, in this case weight events.",
    )


class IcarWeightEventArray(RootModel[List[resources.IcarWeightEventResource]]):
    root: List[resources.IcarWeightEventResource]


class IcarGroupWeightEventCollection(IcarResourceCollection):
    """
    Represents a collection of group weighing events. Based on icarResourceCollection to provide paging etc.
    """

    member: Optional[List[resources.IcarGroupWeightEventResource]] = Field(
        None, description="Provides the array of objects, in this case weighing events."
    )


class IcarGroupWeightEventArray(
    RootModel[List[resources.IcarGroupWeightEventResource]]
):
    root: List[resources.IcarGroupWeightEventResource]


class IcarBreedingValueCollection(IcarResourceCollection):
    """
    Represents a collection of breeding values. Based on icarResourceCollection to provide paging etc.
    """

    member: Optional[List[resources.IcarBreedingValueResource]] = Field(
        None,
        description="As per JSON-LD Hydra syntax, member provides the array of objects, in this case breeding values.",
    )


class IcarTypeClassificationEventCollection(IcarResourceCollection):
    """
    Represents a collection of type classifications. Based on icarResourceCollection to provide paging etc.
    """

    member: Optional[List[resources.IcarTypeClassificationEventResource]] = Field(
        None,
        description="As per JSON-LD Hydra syntax, member provides the array of objects, in this case type classification events.",
    )


class IcarConformationScoreEventCollection(IcarResourceCollection):
    """
    Represents a collection of animal conformation scores. Based on icarResourceCollection to provide paging etc.
    """

    member: Optional[List[resources.IcarConformationScoreEventResource]] = Field(
        None,
        description="As per JSON-LD Hydra syntax, member provides the array of objects, in this case conformation score events.",
    )


class IcarConformationScoreEventArray(
    RootModel[List[resources.IcarConformationScoreEventResource]]
):
    root: List[resources.IcarConformationScoreEventResource]


class IcarLocationCollection(IcarResourceCollection):
    """
    Represents a collection of locations. Based on icarResourceCollection to provide paging etc.
    """

    member: Optional[List[resources.IcarLocationResource]] = Field(
        None,
        description="As per JSON-LD Hydra syntax, member provides the array of objects, in this case locations.",
    )


class IcarAnimalCoreResourceArray(RootModel[List[resources.IcarAnimalCoreResource]]):
    root: List[resources.IcarAnimalCoreResource]


class IcarMovementBirthEventArray(
    RootModel[List[resources.IcarMovementBirthEventResource]]
):
    root: List[resources.IcarMovementBirthEventResource]


class IcarGroupMovementBirthEventArray(
    RootModel[List[resources.IcarGroupMovementBirthEventResource]]
):
    root: List[resources.IcarGroupMovementBirthEventResource]


class IcarMovementDeathEventArray(
    RootModel[List[resources.IcarMovementDeathEventResource]]
):
    root: List[resources.IcarMovementDeathEventResource]


class IcarGroupMovementDeathEventArray(
    RootModel[List[resources.IcarGroupMovementDeathEventResource]]
):
    root: List[resources.IcarGroupMovementDeathEventResource]


class IcarMovementArrivalEventArray(
    RootModel[List[resources.IcarMovementArrivalEventResource]]
):
    root: List[resources.IcarMovementArrivalEventResource]


class IcarGroupMovementArrivalEventArray(
    RootModel[List[resources.IcarGroupMovementArrivalEventResource]]
):
    root: List[resources.IcarGroupMovementArrivalEventResource]


class IcarMovementDepartureEventArray(
    RootModel[List[resources.IcarMovementDepartureEventResource]]
):
    root: List[resources.IcarMovementDepartureEventResource]


class IcarGroupMovementDepartureEventArray(
    RootModel[List[resources.IcarGroupMovementDepartureEventResource]]
):
    root: List[resources.IcarGroupMovementDepartureEventResource]


class IcarReproPregnancyCheckEventCollection(IcarResourceCollection):
    """
    Represents a collection of animal pregnancy checks events. Based on icarResourceCollection to provide paging etc.
    """

    member: Optional[List[resources.IcarReproPregnancyCheckEventResource]] = Field(
        None,
        description="As per JSON-LD Hydra syntax, member provides the array of objects, in this case pregnancy check events.",
    )


class IcarReproPregnancyCheckEventArray(
    RootModel[List[resources.IcarReproPregnancyCheckEventResource]]
):
    root: List[resources.IcarReproPregnancyCheckEventResource]


class IcarReproHeatEventCollection(IcarResourceCollection):
    """
    Represents a collection of animal heat events. Based on icarResourceCollection to provide paging etc.
    """

    member: Optional[List[resources.IcarReproHeatEventResource]] = Field(
        None,
        description="As per JSON-LD Hydra syntax, member provides the array of objects, in this case heat events.",
    )


class IcarReproHeatEventArray(RootModel[List[resources.IcarReproHeatEventResource]]):
    root: List[resources.IcarReproHeatEventResource]


class IcarReproInseminationEventCollection(IcarResourceCollection):
    """
    Represents a collection of animal insemination events. Based on icarResourceCollection to provide paging etc.
    """

    member: Optional[List[resources.IcarReproInseminationEventResource]] = Field(
        None,
        description="As per JSON-LD Hydra syntax, member provides the array of objects, in this case insemination events.",
    )


class IcarReproInseminationEventArray(
    RootModel[List[resources.IcarReproInseminationEventResource]]
):
    root: List[resources.IcarReproInseminationEventResource]


class IcarReproParturitionEventCollection(IcarResourceCollection):
    """
    Represents a collection of animal parturition events. Based on icarResourceCollection to provide paging etc.
    """

    member: Optional[List[resources.IcarReproParturitionEventResource]] = Field(
        None,
        description="As per JSON-LD Hydra syntax, member provides the array of objects, in this case parturition events.",
    )


class IcarReproParturitionEventArray(
    RootModel[List[resources.IcarReproParturitionEventResource]]
):
    root: List[resources.IcarReproParturitionEventResource]


class IcarReproMatingRecommendationCollection(IcarResourceCollection):
    """
    Represents a collection of animal mating recommendation events. Based on icarResourceCollection to provide paging etc.
    """

    member: Optional[List[resources.IcarReproMatingRecommendationResource]] = Field(
        None,
        description="As per JSON-LD Hydra syntax, member provides the array of objects, in this case mating recommendation events.",
    )


class IcarReproMatingRecommendationArray(
    RootModel[List[resources.IcarReproMatingRecommendationResource]]
):
    root: List[resources.IcarReproMatingRecommendationResource]


class IcarReproEmbryoFlushingEventCollection(IcarResourceCollection):
    """
    Represents a collection of animal embryo flushing events. Based on icarResourceCollection to provide paging etc.
    """

    member: Optional[List[resources.IcarReproEmbryoFlushingEventResource]] = Field(
        None,
        description="As per JSON-LD Hydra syntax, member provides the array of objects, in this case embryo flushing events.",
    )


class IcarReproEmbryoFlushingEventArray(
    RootModel[List[resources.IcarReproEmbryoFlushingEventResource]]
):
    root: List[resources.IcarReproEmbryoFlushingEventResource]


class IcarAnimalSortingCommandCollection(IcarResourceCollection):
    """
    Represents a collection of animal-sorting-commands. Based on icarResourceCollection to provide paging etc.
    """

    member: Optional[List[resources.IcarAnimalSortingCommandResource]] = Field(
        None,
        description="As per JSON-LD Hydra syntax, member provides the array of objects, in this case animal sorting commands (icarAnimalSortingCommandResource).",
    )


class IcarSortingSiteCollection(IcarResourceCollection):
    """
    Represents a collection of sites. Based on icarResourceCollection to provide paging etc.
    """

    member: Optional[List[resources.IcarSortingSiteResource]] = Field(
        None,
        description="As per JSON-LD Hydra syntax, member provides the array of objects, in this case sorting-sites.",
    )


class IcarAnimalCoreCollection(IcarResourceCollection):
    """
    Represents a collection of animals. Based on icarResourceCollection to provide paging etc.
    """

    member: Optional[List[resources.IcarAnimalCoreResource]] = Field(
        None,
        description="As per JSON-LD Hydra syntax, member provides the array of objects, in this case animals.",
    )


class IcarMovementBirthEventCollection(IcarResourceCollection):
    """
    Represents a collection of animal birth events. Based on icarResourceCollection to provide paging etc.
    """

    member: Optional[List[resources.IcarMovementBirthEventResource]] = Field(
        None,
        description="As per JSON-LD Hydra syntax, member provides the array of objects, in this case birth events.",
    )


class IcarGroupMovementBirthEventCollection(IcarResourceCollection):
    """
    Represents a collection of group animal registration (birth) events. Based on icarResourceCollection to provide paging etc.
    """

    member: Optional[List[resources.IcarGroupMovementBirthEventResource]] = Field(
        None, description="Provides the array of objects, in this case birth events."
    )


class IcarMovementDeathEventCollection(IcarResourceCollection):
    """
    Represents a collection of animal death events. Based on icarResourceCollection to provide paging etc.
    """

    member: Optional[List[resources.IcarMovementDeathEventResource]] = Field(
        None,
        description="As per JSON-LD Hydra syntax, member provides the array of objects, in this case death events.",
    )


class IcarGroupMovementDeathEventCollection(IcarResourceCollection):
    """
    Represents a collection of group death events. Based on icarResourceCollection to provide paging etc.
    """

    member: Optional[List[resources.IcarGroupMovementDeathEventResource]] = Field(
        None, description="Provides the array of objects, in this case death events."
    )


class IcarMovementArrivalEventCollection(IcarResourceCollection):
    """
    Represents a collection of animal arrival events. Based on icarResourceCollection to provide paging etc.
    """

    member: Optional[List[resources.IcarMovementArrivalEventResource]] = Field(
        None,
        description="As per JSON-LD Hydra syntax, member provides the array of objects, in this case arrival events.",
    )


class IcarGroupMovementArrivalEventCollection(IcarResourceCollection):
    """
    Represents a collection of group arrival events. Based on icarResourceCollection to provide paging etc.
    """

    member: Optional[List[resources.IcarGroupMovementArrivalEventResource]] = Field(
        None, description="Provides the array of objects, in this case arrival events."
    )


class IcarMovementDepartureEventCollection(IcarResourceCollection):
    """
    Represents a collection of animal departure events. Based on icarResourceCollection to provide paging etc.
    """

    member: Optional[List[resources.IcarMovementDepartureEventResource]] = Field(
        None,
        description="As per JSON-LD Hydra syntax, member provides the array of objects, in this case departure events.",
    )


class IcarGroupMovementDepartureEventCollection(IcarResourceCollection):
    """
    Represents a collection of group departure events. Based on icarResourceCollection to provide paging etc.
    """

    member: Optional[List[resources.IcarGroupMovementDepartureEventResource]] = Field(
        None,
        description="Provides the array of objects, in this case departure events.",
    )
