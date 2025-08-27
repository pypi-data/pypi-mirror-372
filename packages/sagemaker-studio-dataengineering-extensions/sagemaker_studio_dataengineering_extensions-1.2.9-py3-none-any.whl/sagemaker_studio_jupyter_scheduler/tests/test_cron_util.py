from sagemaker_studio_jupyter_scheduler.util.cron_util import (
    EventBridgeCronExpressionAdapter,
    GNUCronExpressionAdapter,
    CronExpression,
)


def test_cron_expression_5_parts__happy_path():
    # Given
    raw_cron = "30 20 * 6 MON-FRI"

    # When
    cron_expression = CronExpression(raw_cron)

    # Then
    assert cron_expression.minutes == "30"
    assert cron_expression.hours == "20"
    assert cron_expression.day_of_month == "*"
    assert cron_expression.month == "6"
    assert cron_expression.day_of_week == "MON-FRI"


def test_cron_expression_6_parts__happy_path():
    # Given
    raw_cron = "30 20 * 6 MON-FRI 2025"

    # When
    cron_expression = CronExpression(raw_cron)

    # Then
    assert cron_expression.minutes == "30"
    assert cron_expression.hours == "20"
    assert cron_expression.day_of_month == "*"
    assert cron_expression.month == "6"
    assert cron_expression.day_of_week == "MON-FRI"
    assert cron_expression.year == "*"


def test_gnu_cron_adapter__happy_path():
    # Given
    schedule_expression = "cron(30 20 * 6 MON-FRI 2025)"

    # When
    cron_expression = GNUCronExpressionAdapter(schedule_expression).cron_expression

    # Then
    assert cron_expression.minutes == "30"
    assert cron_expression.hours == "20"
    assert cron_expression.day_of_month == "*"
    assert cron_expression.month == "6"
    assert cron_expression.day_of_week == "MON-FRI"
    assert cron_expression.year == ""


def test_event_bridge_cron_adapter__conflicting_parts__overrides_day_of_month():
    event_bridge_adapter = EventBridgeCronExpressionAdapter("30 20 1-28 6 MON-FRI")
    assert str(event_bridge_adapter.cron_expression) == "30 20 ? 6 MON-FRI *"


def test_event_bridge_cron_adapter__day_of_week_index__overrides_gnu_monday():
    event_bridge_adapter = EventBridgeCronExpressionAdapter("30 20 ? 6 1")
    assert str(event_bridge_adapter.cron_expression) == "30 20 ? 6 2 *"


def test_event_bridge_cron_adapter__day_of_week_index__overrides_gnu_sunday_when_0():
    event_bridge_adapter = EventBridgeCronExpressionAdapter("30 20 ? 6 0")
    assert str(event_bridge_adapter.cron_expression) == "30 20 ? 6 1 *"


def test_event_bridge_cron_adapter__day_of_week_index__overrides_gnu_sunday_when_7():
    event_bridge_adapter = EventBridgeCronExpressionAdapter("30 20 ? 6 7")
    assert str(event_bridge_adapter.cron_expression) == "30 20 ? 6 1 *"


def test_event_bridge_cron_adapter__day_of_week_index__overrides_gnu_multiple_days():
    event_bridge_adapter = EventBridgeCronExpressionAdapter("30 20 ? 6 0-3,5")
    assert str(event_bridge_adapter.cron_expression) == "30 20 ? 6 1-4,6 *"


def test_event_bridge_cron_adapter__day_of_week_index__overrides_gnu_mon_fri():
    event_bridge_adapter = EventBridgeCronExpressionAdapter("30 20 ? 6 MON,5")
    assert str(event_bridge_adapter.cron_expression) == "30 20 ? 6 MON,6 *"


def test_gnu_cron_adapter__day_of_week_index__overrides_eb_monday():
    gnu_adapter = GNUCronExpressionAdapter("cron(30 20 ? 6 2 *)")
    assert str(gnu_adapter.cron_expression) == "30 20 ? 6 1"


def test_gnu_cron_adapter__day_of_week_index__overrides_eb_sunday():
    gnu_adapter = GNUCronExpressionAdapter("cron(30 20 ? 6 1 *)")
    assert str(gnu_adapter.cron_expression) == "30 20 ? 6 0"


def test_gnu_cron_adapter__day_of_week_index__overrides_eb_multiple_days():
    gnu_adapter = GNUCronExpressionAdapter("cron(30 20 ? 6 1-4,6 *)")
    assert str(gnu_adapter.cron_expression) == "30 20 ? 6 0-3,5"


def test_gnu_cron_adapter__day_of_week_index__overrides_eb_mon_fri():
    gnu_adapter = GNUCronExpressionAdapter("cron(30 20 ? 6 MON,6 *)")
    assert str(gnu_adapter.cron_expression) == "30 20 ? 6 MON,5"
