import traceback
from abc import abstractmethod
from logging import Logger

from sapiopylib.rest.DataMgmtService import DataMgmtServer
from sapiopylib.rest.DataRecordManagerService import DataRecordManager
from sapiopylib.rest.WebhookService import AbstractWebhookHandler
from sapiopylib.rest.pojo.webhook.WebhookContext import SapioWebhookContext
from sapiopylib.rest.pojo.webhook.WebhookEnums import WebhookEndpointType
from sapiopylib.rest.pojo.webhook.WebhookResult import SapioWebhookResult
from sapiopylib.rest.utils.recordmodel.RecordModelManager import RecordModelManager, RecordModelInstanceManager, \
    RecordModelRelationshipManager
from sapiopylib.rest.utils.recordmodel.ancestry import RecordModelAncestorManager

from sapiopycommons.general.exceptions import SapioUserErrorException, SapioCriticalErrorException, \
    SapioUserCancelledException


# FR-46064 - Initial port of PyWebhookUtils to sapiopycommons.
class CommonsWebhookHandler(AbstractWebhookHandler):
    """
    A subclass of AbstractWebhookHandler that provides additional quality of life features, including exception
    handling for special sapiopycommons exceptions, logging, easy access invocation type methods, and the context and
    record managers accessible through self.
    """
    logger: Logger

    context: SapioWebhookContext

    dr_man: DataRecordManager
    rec_man: RecordModelManager
    inst_man: RecordModelInstanceManager
    rel_man: RecordModelRelationshipManager
    # FR-46329: Add the ancestor manager to CommonsWebhookHandler.
    an_man: RecordModelAncestorManager

    def run(self, context: SapioWebhookContext) -> SapioWebhookResult:
        self.context = context
        self.logger = context.user.logger

        self.dr_man = context.data_record_manager
        self.rec_man = RecordModelManager(context.user)
        self.inst_man = self.rec_man.instance_manager
        self.rel_man = self.rec_man.relationship_manager
        self.an_man = RecordModelAncestorManager(self.rec_man)

        # Wrap the execution of each webhook in a try/catch. If an exception occurs, handle any special sapiopycommons
        # exceptions. Otherwise, return a generic message stating that an error occurred.
        try:
            self.initialize(context)
            return self.execute(context)
        except SapioUserErrorException as e:
            return self.handle_user_error_exception(e)
        except SapioCriticalErrorException as e:
            return self.handle_critical_error_exception(e)
        except SapioUserCancelledException as e:
            return self.handle_user_cancelled_exception(e)
        except Exception as e:
            return self.handle_unexpected_exception(e)

    def initialize(self, context: SapioWebhookContext) -> None:
        """
        A function that can be optionally overridden by your webhooks to initialize additional instance variables,
        or set up whatever else you wish to set up before the execute function is ran. Default behavior does nothing.
        """
        pass

    @abstractmethod
    def execute(self, context: SapioWebhookContext) -> SapioWebhookResult:
        """
        The business logic of the webhook, implemented in all subclasses that are called as endpoints.
        """
        pass

    # CR-46153: Make CommonsWebhookHandler exception handling more easily overridable by splitting them out of
    # the run method and into their own functions.
    def handle_user_error_exception(self, e: SapioUserErrorException) -> SapioWebhookResult:
        """
        Handle a SapioUserErrorException. Default behavior returns the error message as display text in a webhook
        result.

        :param e: The exception that was raised.
        :return: A SapioWebhookResult reporting the exception to the user.
        """
        result: SapioWebhookResult | None = self.handle_any_exception(e)
        if result is not None:
            return result
        self.log_error(traceback.format_exc())
        return SapioWebhookResult(False, display_text=e.args[0])

    def handle_critical_error_exception(self, e: SapioCriticalErrorException) -> SapioWebhookResult:
        """
        Handle a SapioCriticalErrorException. Default behavior makes a display_error client callback.

        :param e: The exception that was raised.
        :return: A SapioWebhookResult reporting the exception to the user.
        """
        result: SapioWebhookResult | None = self.handle_any_exception(e)
        if result is not None:
            return result
        self.log_error(traceback.format_exc())
        if self.can_send_client_callback():
            DataMgmtServer.get_client_callback(self.context.user).display_error(e.args[0])
        return SapioWebhookResult(False)

    def handle_unexpected_exception(self, e: Exception) -> SapioWebhookResult:
        """
        Handle a generic exception which isn't a SapioUserErrorException or SapioCriticalErrorException. Default
        behavior returns a generic error message as display text informing the user to contact Sapio support.

        :param e: The exception that was raised.
        :return: A SapioWebhookResult reporting the exception to the user.
        """
        result: SapioWebhookResult | None = self.handle_any_exception(e)
        if result is not None:
            return result
        self.log_error(traceback.format_exc())
        return SapioWebhookResult(False, display_text="Unexpected error occurred during webhook execution. "
                                                      "Please contact Sapio support.")

    def handle_user_cancelled_exception(self, e: SapioUserCancelledException) -> SapioWebhookResult:
        """
        Handle a SapioUserCancelledException. Default behavior returns "User Cancelled" as display text in a webhook
        result.

        :param e: The exception that was raised.
        :return: A SapioWebhookResult with display text saying the user cancelled the request.
        """
        result: SapioWebhookResult | None = self.handle_any_exception(e)
        if result is not None:
            return result
        return SapioWebhookResult(False, display_text="User cancelled.")

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def handle_any_exception(self, e: Exception) -> SapioWebhookResult | None:
        """
        An exception handler which runs regardless of the type of exception that was raised. Can be used to "rollback"
        the client if an error occurs. Default behavior does nothing and returns None.

        :param e: The exception that was raised.
        :return: An optional SapioWebhookResult. May return a custom message to the client that wouldn't have been
            sent by one of the normal exception handlers, or may return None if no result needs returned.
        """
        return None

    def log_info(self, msg: str) -> None:
        """
        Write an info message to the log. Log destination is stdout. This message will be prepended with the user's
        username and the experiment ID of the experiment they are in, if any.
        """
        exp_id = None
        if self.context.eln_experiment is not None:
            exp_id = self.context.eln_experiment.notebook_experiment_id
        # CR-46333: Add the user's group to the logging message.
        user = self.context.user
        username = user.username
        group_name = user.session_additional_data.current_group_name
        self.logger.info(f"(User: {username}, Group: {group_name}, Experiment: {exp_id}):\n{msg}")

    def log_error(self, msg: str) -> None:
        """
        Write an error message to the log. Log destination is stderr. This message will be prepended with the user's
        username and the experiment ID of the experiment they are in, if any.
        """
        exp_id = None
        if self.context.eln_experiment is not None:
            exp_id = self.context.eln_experiment.notebook_experiment_id
        # CR-46333: Add the user's group to the logging message.
        user = self.context.user
        username = user.username
        group_name = user.session_additional_data.current_group_name
        # PR-46209: Use logger.error instead of logger.info when logging errors.
        self.logger.error(f"(User: {username}, Group: {group_name}, Experiment: {exp_id}):\n{msg}")

    def is_main_toolbar(self) -> bool:
        """
        :return: True if this endpoint was invoked as a main toolbar button.
        """
        return self.context.end_point_type == WebhookEndpointType.ACTIONMENU

    def is_form_toolbar(self) -> bool:
        """
        :return: True if this endpoint was invoked as a data record form toolbar button.
        """
        return self.context.end_point_type == WebhookEndpointType.FORMTOOLBAR

    def is_table_toolbar(self) -> bool:
        """
        :return: True if this endpoint was invoked as a data record table toolbar button.
        """
        return self.context.end_point_type == WebhookEndpointType.TABLETOOLBAR

    def is_temp_form_toolbar(self) -> bool:
        """
        :return: True if this endpoint was invoked as a temporary data record form toolbar button.
        """
        return self.context.end_point_type == WebhookEndpointType.TEMP_DATA_FORM_TOOLBAR

    def is_temp_table_toolbar(self) -> bool:
        """
        :return: True if this endpoint was invoked as a temporary data record table toolbar button.
        """
        return self.context.end_point_type == WebhookEndpointType.TEMP_DATA_TABLE_TOOLBAR

    def is_eln_rule(self) -> bool:
        """
        :return: True if this endpoint was invoked as an ELN rule action.
        """
        return self.context.end_point_type == WebhookEndpointType.VELOXELNRULEACTION

    def is_on_save_rule(self) -> bool:
        """
        :return: True if this endpoint was invoked as an on save rule action.
        """
        return self.context.end_point_type == WebhookEndpointType.VELOX_RULE_ACTION
        # TODO: This VELOXONSAVERULEACTION endpoint type exists, but I don't see it actually getting sent by on save
        #  rule action invocations, instead seeing the above VELOX_RULE_ACTION type. Probably worth investigation.
        # return self.context.end_point_type == WebhookEndpointType.VELOXONSAVERULEACTION

    def is_eln_main_toolbar(self) -> bool:
        """
        :return: True if this endpoint was invoked as an ELN main toolbar button.
        """
        return self.context.end_point_type == WebhookEndpointType.NOTEBOOKEXPERIMENTMAINTOOLBAR

    def is_eln_entry_toolbar(self) -> bool:
        """
        :return: True if this endpoint was invoked as an ELN entry toolbar button.
        """
        return self.context.end_point_type == WebhookEndpointType.EXPERIMENTENTRYTOOLBAR

    def is_selection_list(self) -> bool:
        """
        :return: True if this endpoint was invoked as a selection list populator.
        """
        return self.context.end_point_type == WebhookEndpointType.SELECTIONDATAFIELD

    def is_report_builder(self) -> bool:
        """
        :return: True if this endpoint was invoked as a report builder template data populator.
        """
        return self.context.end_point_type == WebhookEndpointType.REPORT_BUILDER_TEMPLATE_DATA_POPULATOR

    def is_scheduled_action(self) -> bool:
        """
        :return: True if this endpoint was invoked as a scheduled action.
        """
        return self.context.end_point_type == WebhookEndpointType.SCHEDULEDPLUGIN

    def is_action_button_field(self) -> bool:
        """
        :return: True if this endpoint was invoked as an action button field.
        """
        return self.context.end_point_type == WebhookEndpointType.ACTIONDATAFIELD

    def is_action_text_field(self) -> bool:
        """
        :return: True if this endpoint was invoked as an action text field.
        """
        return self.context.end_point_type == WebhookEndpointType.ACTION_TEXT_FIELD

    def is_custom(self) -> bool:
        """
        :return: True if this endpoint was invoked from a custom point, such as a custom queue.
        """
        return self.context.end_point_type == WebhookEndpointType.CUSTOM

    def is_calendar_event_click_handler(self) -> bool:
        """
        :return: True if this endpoint was invoked from a calendar event click handler.
        """
        return self.context.end_point_type == WebhookEndpointType.CALENDAR_EVENT_CLICK_HANDLER

    def is_eln_menu_grabber(self) -> bool:
        """
        :return: True if this endpoint was invoked as a notebook entry grabber.
        """
        return self.context.end_point_type == WebhookEndpointType.NOTEBOOKEXPERIMENTGRABBER

    def is_conversation_bot(self) -> bool:
        """
        :return: True if this endpoint was invoked as from a conversation bot.
        """
        return self.context.end_point_type == WebhookEndpointType.CONVERSATION_BOT

    def is_multi_data_type_table_toolbar(self) -> bool:
        """
        :return: True if this endpoint was invoked as a multi data type table toolbar button.
        """
        return self.context.end_point_type == WebhookEndpointType.REPORTTOOLBAR

    def can_send_client_callback(self) -> bool:
        """
        :return: Whether client callbacks and directives can be sent from this webhook's endpoint type.
        """
        return self.context.is_client_callback_available
