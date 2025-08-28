import io

from sapiopylib.rest.User import SapioUser
from sapiopylib.rest.pojo.webhook.WebhookContext import SapioWebhookContext
from sapiopylib.rest.utils.recordmodel.RecordModelWrapper import WrappedType

from sapiopycommons.general.aliases import AliasUtil, SapioRecord
from sapiopycommons.general.exceptions import SapioException
from sapiopycommons.recordmodel.record_handler import RecordHandler


# FR-46064 - Initial port of PyWebhookUtils to sapiopycommons.
class AttachmentUtil:
    @staticmethod
    def get_attachment_bytes(context: SapioWebhookContext, attachment: SapioRecord) -> bytes:
        """
        Get the data bytes for the given attachment record. Makes a webservice call to retrieve the data.

        :param context: The current webhook context.
        :param attachment: The attachment record.
        :return: The bytes for the attachment's file data.
        """
        attachment = AliasUtil.to_data_record(attachment)
        with io.BytesIO() as data_sink:
            def consume_data(chunk: bytes):
                data_sink.write(chunk)
            context.data_record_manager.get_attachment_data(attachment, consume_data)
            data_sink.flush()
            data_sink.seek(0)
            file_bytes = data_sink.read()
        return file_bytes

    @staticmethod
    def set_attachment_bytes(context: SapioWebhookContext, attachment: SapioRecord,
                             file_name: str, file_bytes: bytes) -> None:
        """
        Set the attachment data for a given attachment record. Makes a webservice call to set the data.

        :param context: The current webhook context.
        :param attachment: The attachment record. Must be an existing data record that is an attachment type.
        :param file_name: The name of the attachment.
        :param file_bytes: The bytes of the attachment data.
        """
        if attachment.record_id < 0:
            raise SapioException("Provided record cannot have its attachment data set, as it does not exist in the "
                                 "system yet.")
        attachment = AliasUtil.to_data_record(attachment)
        with io.BytesIO(file_bytes) as stream:
            context.data_record_manager.set_attachment_data(attachment, file_name, stream)

    @staticmethod
    def create_attachment(context: SapioWebhookContext | SapioUser, file_name: str, file_bytes: bytes,
                          wrapper_type: type[WrappedType]) -> WrappedType:
        """
        Create an attachment data type and initialize its attachment bytes at the same time.
        Makes a webservice call to create the attachment record and a second to set its bytes.

        :param context: The current webhook context or a user object to send requests from.
        :param file_name: The name of the attachment.
        :param file_bytes: THe bytes of the attachment data.
        :param wrapper_type: The attachment type to create.
        :return: A record model for the newly created attachment.
        """
        attachment: WrappedType = RecordHandler(context).create_models(wrapper_type, 1)[0]
        AttachmentUtil.set_attachment_bytes(context, attachment, file_name, file_bytes)
        return attachment
