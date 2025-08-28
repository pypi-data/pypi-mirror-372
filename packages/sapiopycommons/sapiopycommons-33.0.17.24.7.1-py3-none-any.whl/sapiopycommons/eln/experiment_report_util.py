from sapiopylib.rest.User import SapioUser
from sapiopylib.rest.pojo.CustomReport import (
    CompositeReportTerm,
    CompositeTermOperation,
    CustomReportCriteria,
    ExplicitJoinDefinition,
    FieldCompareReportTerm,
    RawReportTerm,
    RawTermOperation,
    ReportColumn,
)
from sapiopylib.rest.pojo.datatype.FieldDefinition import FieldType
from sapiopylib.rest.pojo.webhook.WebhookContext import SapioWebhookContext
from sapiopylib.rest.utils.recordmodel.RecordModelWrapper import WrappedType

from sapiopycommons.general.aliases import SapioRecord
from sapiopycommons.general.custom_report_util import CustomReportUtil
from sapiopycommons.recordmodel.record_handler import RecordHandler

_NOTEBOOK_ID = "EXPERIMENTID"
_RECORD_ID = "RECORDID"


# FR-46908 - Provide a utility class that holds experiment related custom reports e.g. getting all the experiments
# that given records were used in or getting all records of a datatype used in given experiments.
class ExperimentReportUtil:
    @staticmethod
    def map_records_to_experiment_ids(
        context: SapioWebhookContext | SapioUser,
        records: list[SapioRecord],
    ) -> dict[SapioRecord, list[int]]:
        """
        Return a dictionary mapping each record to a list of ids of experiments that they were used in.
        If a record wasn't used in any experiments then it will be mapped to an empty list.

        :param context: The current webhook context or a user object to send requests from.
        :param records: a list of records of the same data type.
        :return: a dictionary mapping each record to a list of ids of each experiment it was used in.
        """
        if not records:
            return {}

        user: SapioUser = context if isinstance(context, SapioUser) else context.user

        data_type_name = records[0].data_type_name

        record_ids = [record.record_id for record in records]

        rows = ExperimentReportUtil.__get_record_experiment_relation_rows(
            user, data_type_name, record_ids=record_ids
        )

        id_to_record: dict[int, SapioRecord] = RecordHandler.map_by_id(records)

        record_to_exps: dict[SapioRecord, set[int]] = {
            record: set() for record in records
        }

        for row in rows:
            record_id: int = row[_RECORD_ID]
            exp_id: int = row[_NOTEBOOK_ID]

            record = id_to_record[record_id]

            record_to_exps[record].add(exp_id)

        return {record: list(exps) for record, exps in record_to_exps.items()}

    @staticmethod
    def map_experiments_to_records_of_type(
        context: SapioWebhookContext | SapioUser,
        exp_ids: list[int],
        wrapper_type: type[WrappedType],
    ) -> dict[int, list[WrappedType]]:
        """
        Return a dictionary mapping each experiment id to a list of records of the given type that were used in each experiment.
        If an experiment didn't use any records of the given type then it will be mapped to an empty list.

        :param context: The current webhook context or a user object to send requests from.
        :param exp_ids: a list of experiment ids. These are specifically the Notebook Experiment ids which can be found in the title of the experiment.
        :param wrapper_type: The record model wrapper to use, corresponds to which data type we will query for.
        :return: a dictionary mapping each experiment id to a list of records of the given type that were used in that experiment.
        """
        if not exp_ids:
            return {}

        user = context if isinstance(context, SapioUser) else context.user

        record_handler = RecordHandler(user)

        data_type_name: str = wrapper_type.get_wrapper_data_type_name()

        rows = ExperimentReportUtil.__get_record_experiment_relation_rows(
            user, data_type_name, exp_ids=exp_ids
        )

        record_ids: set[int] = {row[_RECORD_ID] for row in rows}

        records = record_handler.query_models_by_id(wrapper_type, record_ids)

        id_to_record: dict[int, WrappedType] = RecordHandler.map_by_id(records)

        exp_to_records: dict[int, set[SapioRecord]] = {exp: set() for exp in exp_ids}

        for row in rows:
            record_id: int = row[_RECORD_ID]
            exp_id: int = row[_NOTEBOOK_ID]

            record = id_to_record[record_id]

            exp_to_records[exp_id].add(record)

        return {exp: list(records) for exp, records in exp_to_records.items()}

    @staticmethod
    def __get_record_experiment_relation_rows(
        user: SapioUser,
        data_type_name: str,
        record_ids: list[int] | None = None,
        exp_ids: list[int] | None = None,
    ) -> list[dict[str, int]]:
        """
        Return a list of dicts mapping \"RECORDID\" to the record id and \"EXPERIMENTID\" to the experiment id.
        At least one of record_ids and exp_ids should be provided.
        """
        assert (record_ids or exp_ids)

        if record_ids:
            rec_ids = [str(record_id) for record_id in record_ids]

            ids_str = "{" + ", ".join(rec_ids) + "}"

            records_term = RawReportTerm(
                data_type_name, "RECORDID", RawTermOperation.EQUAL_TO_OPERATOR, ids_str
            )

        else:
            # Get all records of the given type
            records_term = RawReportTerm(
                data_type_name,
                "RECORDID",
                RawTermOperation.GREATER_THAN_OR_EQUAL_OPERATOR,
                "0",
            )

        if exp_ids:
            exp_ids = [str(exp_id) for exp_id in exp_ids]

            ids_str = "{" + ", ".join(exp_ids) + "}"

            exp_term = RawReportTerm(
                "NOTEBOOKEXPERIMENT",
                "EXPERIMENTID",
                RawTermOperation.EQUAL_TO_OPERATOR,
                ids_str,
            )

        else:
            # Get all experiments
            exp_term = RawReportTerm(
                "NOTEBOOKEXPERIMENT",
                "EXPERIMENTID",
                RawTermOperation.GREATER_THAN_OR_EQUAL_OPERATOR,
                "0",
            )

        root_term = CompositeReportTerm(
            records_term, CompositeTermOperation.AND_OPERATOR, exp_term
        )

        # The columns the resulting dataframe will have
        column_list = [
            ReportColumn(data_type_name, "RECORDID", FieldType.LONG),
            ReportColumn("NOTEBOOKEXPERIMENT", "EXPERIMENTID", FieldType.LONG),
        ]

        # Join records on the experiment entry records that correspond to them.
        records_entry_join = FieldCompareReportTerm(
            data_type_name,
            "RECORDID",
            RawTermOperation.EQUAL_TO_OPERATOR,
            "EXPERIMENTENTRYRECORD",
            "RECORDID",
        )

        # Join entry records on the experiment entries they are in.
        experiment_entry_enb_entry_join = FieldCompareReportTerm(
            "EXPERIMENTENTRYRECORD",
            "ENTRYID",
            RawTermOperation.EQUAL_TO_OPERATOR,
            "ENBENTRY",
            "ENTRYID",
        )

        # Join entries on the experiments they are in.
        enb_entry_experiment_join = FieldCompareReportTerm(
            "ENBENTRY",
            "EXPERIMENTID",
            RawTermOperation.EQUAL_TO_OPERATOR,
            "NOTEBOOKEXPERIMENT",
            "EXPERIMENTID",
        )

        report_criteria = CustomReportCriteria(
            column_list,
            root_term,
            join_list=[
                ExplicitJoinDefinition("EXPERIMENTENTRYRECORD", records_entry_join),
                ExplicitJoinDefinition("ENBENTRY", experiment_entry_enb_entry_join),
                ExplicitJoinDefinition("NOTEBOOKEXPERIMENT", enb_entry_experiment_join),
            ],
        )

        return CustomReportUtil.run_custom_report(user, report_criteria)
