from collections.abc import Iterable
from typing import Any

from sapiopylib.rest.pojo.DataRecord import DataRecord
from sapiopylib.rest.pojo.eln.ElnExperiment import ElnExperiment
from sapiopylib.rest.utils.Protocols import ElnExperimentProtocol
from sapiopylib.rest.utils.recordmodel.PyRecordModel import PyRecordModel
from sapiopylib.rest.utils.recordmodel.RecordModelWrapper import WrappedRecordModel, WrappedType

RecordModel = PyRecordModel | WrappedRecordModel | WrappedType
"""Different forms that a record model could take."""
SapioRecord = DataRecord | RecordModel
"""A record could be provided as either a DataRecord, PyRecordModel, or WrappedRecordModel (WrappedType)."""
RecordIdentifier = SapioRecord | int
"""A RecordIdentifier is either a record type or an integer for the record's record ID."""
ExperimentIdentifier = ElnExperimentProtocol | ElnExperiment | int
"""An ExperimentIdentifier is either an experiment protocol, experiment, or an integer for te experiment's notebook
ID."""
FieldMap = dict[str, Any]
"""A field map is simply a dict of data field names to values. The purpose of aliasing this is to help distinguish
any random dict in a webhook from one which is explicitly used for record fields."""


# FR-46064 - Initial port of PyWebhookUtils to sapiopycommons.
class AliasUtil:
    @staticmethod
    def to_data_record(record: SapioRecord) -> DataRecord:
        """
        Convert a single DataRecord, PyRecordModel, or WrappedRecordModel to just a DataRecord.

        :return: The DataRecord of the input SapioRecord.
        """
        return record if isinstance(record, DataRecord) else record.get_data_record()

    @staticmethod
    def to_data_records(records: Iterable[SapioRecord]) -> list[DataRecord]:
        """
        Convert a list of variables that could either be DataRecords, PyRecordModels,
        or WrappedRecordModels to just DataRecords.

        :return: A list of DataRecords for the input records.
        """
        return [(x if isinstance(x, DataRecord) else x.get_data_record()) for x in records]

    @staticmethod
    def to_record_ids(records: Iterable[RecordIdentifier]) -> list[int]:
        """
        Convert a list of variables that could either be integers, DataRecords, PyRecordModels,
        or WrappedRecordModels to just integers (taking the record ID from the records).

        :return: A list of record IDs for the input records.
        """
        return [(x if isinstance(x, int) else x.record_id) for x in records]

    @staticmethod
    def to_field_map_lists(records: Iterable[SapioRecord]) -> list[FieldMap]:
        """
        Convert a list of variables that could either be DataRecords, PyRecordModels,
        or WrappedRecordModels to a list of their field maps.

        :return: A list of field maps for the input records.
        """
        field_map_list: list[FieldMap] = []
        for record in records:
            if isinstance(record, DataRecord):
                field_map_list.append(record.get_fields())
            else:
                field_map_list.append(record.fields.copy_to_dict())
        return field_map_list

    @staticmethod
    def to_notebook_id(experiment: ExperimentIdentifier) -> int:
        """
        Convert an object that identifies an ELN experiment to its notebook ID.

        :return: The notebook ID for the experiment identifier.
        """
        if isinstance(experiment, int):
            return experiment
        if isinstance(experiment, ElnExperiment):
            return experiment.notebook_experiment_id
        return experiment.get_id()
