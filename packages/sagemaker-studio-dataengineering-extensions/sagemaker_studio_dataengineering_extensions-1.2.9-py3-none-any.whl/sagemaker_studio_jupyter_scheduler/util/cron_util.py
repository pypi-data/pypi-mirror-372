import re
from typing import Optional


DEFAULT_CRON_EXPRESSION = "0 0 * * MON-FRI"


class CronExpression:
    minutes: str
    hours: str
    day_of_month: str
    month: str
    day_of_week: str
    year: Optional[str]

    def __init__(self, raw_cron: str):
        cron_fields = raw_cron.split(" ")
        num_cron_fields = len(cron_fields)
        if num_cron_fields < 5 or num_cron_fields > 6:
            raise RuntimeError(
                f"Cron expression has {num_cron_fields} fields, but expected 5-6"
            )

        self.minutes = cron_fields[0]
        self.hours = cron_fields[1]
        self.day_of_month = cron_fields[2]
        self.month = cron_fields[3]
        self.day_of_week = cron_fields[4]
        # GNU cron does not support 'year' field, but it is required by EventBridge
        self.year = "*" if num_cron_fields > 5 else ""

    def __str__(self):
        return f"{self.minutes} " \
               f"{self.hours} " \
               f"{self.day_of_month} " \
               f"{self.month} " \
               f"{self.day_of_week} " \
               f"{self.year}".rstrip()


class EventBridgeCronExpressionAdapter:
    cron_expression: CronExpression

    def __init__(self, raw_cron: str):
        self.cron_expression = CronExpression(raw_cron)
        self.fix_days(self.cron_expression)
        self.translate_to_event_bridge_cron()

    @staticmethod
    def fix_days(cron_expression: CronExpression):
        """
        Event Bridge has the following limitation:
        > You can't specify the Day-of-month and Day-of-week fields in the same cron expression.
        > If you specify a value or a * (asterisk) in one of the fields, you must use a ? (question mark) in the other.

        https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-create-rule-schedule.html#eb-cron-expressions
        """
        if cron_expression.day_of_month == "?" or cron_expression.day_of_week == "?":
            return

        # First try to change either * to ?
        if cron_expression.day_of_month == "*":
            cron_expression.day_of_month = "?"
            return

        if cron_expression.day_of_week == "*":
            cron_expression.day_of_week = "?"
            return

        # Neither field is *, so have to just favor one of the fields.
        # Arbitrarily favoring day_of_week.
        cron_expression.day_of_month = "?"

    def translate_to_event_bridge_cron(self):
        """
        The cron expression syntax for GNU syntax (on Studio UI) and EventBridge are different
        > 'day_of_week' field for GNU follows MON-SUN(1-7, where 0 and 7 are both sunday)
        > 'day_of_week' field for EventBridge follows SUN-SAT(1-7)
        > 'year' field is not supported by GNU syntax, but it is required in EventBridge syntax
        """
        # Translates the day_of_week field of cron expression from GNU syntax to EventBridge syntax
        if re.search(r'\d', self.cron_expression.day_of_week):
            self.cron_expression.day_of_week = re.sub(
                r'\d',
                self.replace_day_index_event_bridge,
                self.cron_expression.day_of_week
            )

        # Event Bridge cron expressions require an extra field for year, which we just set to *.
        self.cron_expression.year = "*"

    @staticmethod
    def replace_day_index_event_bridge(index_match: Optional[re.Match]) -> str:
        """
        Replace the day_of_week numeric values corresponding to EventBridge syntax
        """
        day_index = int(index_match.group())
        return str(day_index + 1) if day_index < 7 else str(1)


class GNUCronExpressionAdapter:
    cron_expression: CronExpression

    def __init__(self, schedule_expression: str):
        self.schedule_expression = schedule_expression
        self.translate_to_gnu_cron()

    def translate_to_gnu_cron(self):
        # Translates the day_of_week field of cron expression from EventBridge syntax to GNU syntax
        raw_cron = re.search("cron\\((.+)\\)", self.schedule_expression).group(1)

        self.cron_expression = CronExpression(raw_cron)

        if re.search(r'\d', self.cron_expression.day_of_week):
            self.cron_expression.day_of_week = re.sub(
                r'\d',
                self.replace_day_index_gnu,
                self.cron_expression.day_of_week
            )

        # GNU cron syntax does not support 'year' field, so we are setting it as an empty field
        self.cron_expression.year = ""

    @staticmethod
    def replace_day_index_gnu(index_match: Optional[re.Match]) -> str:
        """
        Replace the day_of_week numeric values corresponding to GNU syntax
        """
        return str(int(index_match.group()) - 1)

