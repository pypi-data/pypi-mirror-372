from app_utils.testing import NoSocketsTestCase

from ..models import InactivityPingConfig, LeaveOfAbsence, Webhook
from .factories import (
    GroupFactory,
    InactivityPingConfigFactory,
    LeaveOfAbsenceFactory,
    UserMainRequestorFactory,
    WebhookFactory,
)


class TestLeaveOfAbsenceManager(NoSocketsTestCase):
    def test_should_ping_for_inactive_user(self):
        # given
        LeaveOfAbsenceFactory(is_approved=True)
        LeaveOfAbsenceFactory()
        # when
        self.assertEqual(LeaveOfAbsence.objects.unapproved_count(), 1)

    def test_should_annotate_status_correctly(self):
        # given
        pending = LeaveOfAbsenceFactory()
        approved = LeaveOfAbsenceFactory(is_approved=True)
        denied = LeaveOfAbsenceFactory(is_denied=True)
        # when
        result = {obj.pk: obj for obj in LeaveOfAbsence.objects.annotate_status()}
        # then
        self.assertEqual(result[pending.pk].status, LeaveOfAbsence.Status.PENDING)
        self.assertEqual(result[approved.pk].status, LeaveOfAbsence.Status.APPROVED)
        self.assertEqual(result[denied.pk].status, LeaveOfAbsence.Status.DENIED)


class TestInactivityPingConfigManager(NoSocketsTestCase):
    def test_should_filter_relevant_for_user(self):
        # given
        config_1 = InactivityPingConfigFactory()
        group_1 = GroupFactory()
        config_2 = InactivityPingConfigFactory(groups=[group_1])
        group_2 = GroupFactory()
        InactivityPingConfigFactory(groups=[group_2])

        user = UserMainRequestorFactory(groups=[group_1])
        # when
        result = InactivityPingConfig.objects.relevant_for_user(user)
        # then
        result_pks = set(result.values_list("pk", flat=True))
        self.assertSetEqual(result_pks, {config_1.pk, config_2.pk})


class TestWebhookManager(NoSocketsTestCase):
    def test_should_filter_relevant_for_user(self):
        # given
        group_1 = GroupFactory()
        config_1 = InactivityPingConfigFactory(groups=[group_1])
        webhook = WebhookFactory(ping_configs=[config_1])
        group_2 = GroupFactory()
        config_2 = InactivityPingConfigFactory(groups=[group_2])
        WebhookFactory(ping_configs=[config_2])
        user = UserMainRequestorFactory(groups=[group_1])
        # when
        result = Webhook.objects.relevant_for_user(user)
        # then
        result_pks = set(result.values_list("pk", flat=True))
        self.assertSetEqual(result_pks, {webhook.pk})
