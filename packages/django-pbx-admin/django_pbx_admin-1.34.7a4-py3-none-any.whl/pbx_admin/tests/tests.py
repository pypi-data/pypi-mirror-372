import datetime

from django.core.exceptions import ValidationError
from django.test import SimpleTestCase, TestCase

from parameterized import parameterized

from pbx_admin.form_fields import DateTimeRangePickerField
from pbx_admin.templatetags.admin_tags import humanize_number
from pbx_admin.views.mixins import PaginationMixin
from pbx_admin.widgets import DateTimeRangePickerWidget


class AdminListViewTests(TestCase):
    def test_adjacent_pages(self):
        self.assertEqual(
            PaginationMixin._get_adjacent_pages(7, range(1, 12), 2), ([5, 6], [8, 9])
        )
        self.assertEqual(
            PaginationMixin._get_adjacent_pages(3, range(1, 7), 2), ([1, 2], [4, 5])
        )


class DateTimeRangePickerFieldTest(SimpleTestCase):
    def setUp(self) -> None:
        self.test_field = DateTimeRangePickerField()

    def test_valid_widget(self) -> None:
        self.assertIsInstance(self.test_field.widget, DateTimeRangePickerWidget)

    def test_valid_time_range(self) -> None:
        date_range = [
            datetime.datetime.now(),
            datetime.datetime.now() + datetime.timedelta(days=10),
        ]

        test_case = self.test_field.clean(date_range)

        self.assertEqual(date_range, test_case)

    def test_invalid_time_range(self) -> None:
        invalid_date_range = [
            datetime.datetime.now(),
            datetime.datetime.now() - datetime.timedelta(days=10),
        ]

        with self.assertRaisesMessage(ValidationError, "Invalid date range"):
            self.test_field.clean(invalid_date_range)


class TemplateTagsTests(TestCase):
    @parameterized.expand(
        (
            (0, "0"),
            (999, "999"),
            (1_000, "1K"),
            (99_999, "99K"),
            (100_000, "100K"),
            (324_324, "324K"),
            (1_000_000, "1M"),
            (1_888_000, "1.8M"),
        )
    )
    def test_humanize_number(self, num, expected):
        self.assertEqual(humanize_number(num), expected)
