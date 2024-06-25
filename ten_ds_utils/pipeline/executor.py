from datetime import datetime
import logging
from typing import Callable

from ten_ds_utils.govuk_notify import govuk_notify_service
from ten_ds_utils.config.pipeline import PipelineConfig


class PipelineExecutor:
    def __init__(
        self,
        pipeline_name: str,
        contact_email: str,
        conf: PipelineConfig,
        ignore_local_errors: bool = False,
    ):
        self.initialize_log()
        self.pipeline_name = pipeline_name
        self.contact_email = contact_email
        self.conf = conf

        # functions break pipelinewhen running locally for debugging
        self.ignore_local_errors = ignore_local_errors

        if isinstance(self.contact_email, str):
            self.contact_email = [self.contact_email]

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_pipeline()

    def initialize_log(self):
        self.log = []

    def add_to_log(self, log_str: str):
        self.log += [log_str]

    def execute(self, func: Callable):
        def wrapper(*args, **kwargs):
            try:
                output = func(*args, **kwargs)
                return output

            except Exception as e:
                self.add_to_log(f"Error running function {func.__name__}")
                logging.info(f"\x1b[31;1mError in {func.__name__}: \x1b[0m{e}")

                if self.conf.is_local() and not self.ignore_local_errors:
                    raise e

        return wrapper

    def end_pipeline(self):
        if bool(self.log):
            logging.info("Pipeline executed - errors detected")
            error_text = "\n * ".join(self.log)
            email_text = f"""
            \n * {error_text}
            """
            self.report_errors(email_text)

        else:
            logging.info("\033[0;32mPipeline executed - no errors detected\x1b[0m")

    def print_errors(self, body):
        logging.warning(body)

    def email_errors(self, body, email_service=None):
        if not email_service:
            email_service = govuk_notify_service("govuk-notify-ten-ds-error")

        email_time = datetime.now().strftime("%H:%M:%S %d/%m/%Y")

        for email_address in self.contact_email:
            email_service.send_email_notification(
                template_id="dc82cbab-cb59-43a4-8cfa-b5beee2b0644",
                email_address=email_address,
                personalisation={
                    "pipeline_name": self.pipeline_name,
                    "time_of_error": email_time,
                    "env": self.conf.env(),
                    "body": body,
                },
            )

    def report_errors(self, body: str):
        if self.conf.is_local():
            self.print_errors(body)

        else:
            self.email_errors(body)
