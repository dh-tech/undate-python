from undate.converters.calendars import SeleucidDateConverter
from undate.date import Date, DatePrecision
from undate.undate import Calendar, Undate


class TestSeleucidDateConverter:
    def test_parse(self):
        # day
        # Elul = month 6; 11 September, 1000 Gregorian
        date_str = "29 Elul 1311"
        date = SeleucidDateConverter().parse(date_str)
        assert date == Undate(1311, 6, 29, calendar="Seleucid")
        assert date.calendar == Calendar.SELEUCID
        assert date.precision == DatePrecision.DAY
        assert date.label == f"{date_str} {SeleucidDateConverter.calendar_name}"

        date_str = "Tishri 1458"  # month 7
        date = SeleucidDateConverter().parse(date_str)
        assert date == Undate(1458, 7, calendar="Seleucid")
        assert date.calendar == Calendar.SELEUCID
        assert date.precision == DatePrecision.MONTH
        assert date.label == f"{date_str} {SeleucidDateConverter.calendar_name}"

        # year
        date_str = "1458"
        date = SeleucidDateConverter().parse(date_str)
        assert date == Undate(1458, calendar="Seleucid")
        assert date.calendar == Calendar.SELEUCID
        assert date.precision == DatePrecision.YEAR
        assert date.label == f"{date_str} {SeleucidDateConverter.calendar_name}"

    def test_gregorian_earliest_latest(self):
        # earliest/latest should be converted to Gregorian for comparison

        # full date
        # Elul = month 6 (7 September, 1000 Gregorian)
        date_str = "29 Elul 1311"
        date = SeleucidDateConverter().parse(date_str)
        assert date.earliest == Date(1000, 9, 7)
        assert date.latest == Date(1000, 9, 7)
        assert date.label == f"{date_str} {SeleucidDateConverter.calendar_name}"

        date_str = "23 Adar I 1475"
        date = SeleucidDateConverter().parse(date_str)
        assert date.earliest == Date(1164, 2, 25)
        assert date.latest == Date(1164, 2, 25)
        assert date.label == f"{date_str} {SeleucidDateConverter.calendar_name}"

        # month/year
        date_str = "Tishri 1458"
        date = SeleucidDateConverter().parse(date_str)
        assert date.earliest == Date(1146, 9, 16)
        assert date.latest == Date(1146, 10, 15)
        assert date.label == f"{date_str} {SeleucidDateConverter.calendar_name}"

    def test_days_in_year(self):
        converter = SeleucidDateConverter()
        assert converter.days_in_year(2350) == 354
        assert converter.days_in_year(2349) == 385
        assert converter.days_in_year(2351) == 355


# TODO: update validation error to say seleucid instead of hebrew

#     seleucid_year = 1458
#     converted_date = convert_seleucid_date(f"Tishri {seleucid_year}")
#     converted_date_am = convert_hebrew_date(
#         f"Tishrei {seleucid_year + Calendar.SELEUCID_OFFSET}"
#     )
#     # the converted date range for Tishri Sel. should be the same as that for Tishri AM - 3449 years.
#     assert converted_date[0] == converted_date_am[0]
#     assert converted_date[1] == converted_date_am[1]

#     # leap day (Feb 29, 2020) should convert properlyd
#     converted_date = convert_seleucid_date("4 Adar 2331")
#     assert converted_date[1] == date(2020, 2, 29)


# # 26 Tammuz 4816: 17 July, 1056; Tammuz = month 4
# date = Undate(4816, 4, 26, calendar="Seleucid")
# assert date.earliest == Date(1056, 7, 17)
# assert date.latest == Date(1056, 7, 17)
# # 13 Tishrei 5416 Anno Mundi (1655-10-14)
# date = Undate(5416, 7, 13, calendar="Seleucid")  # Tishrei = month 7
# assert date.earliest == Date(1655, 10, 14)
# assert date.latest == Date(1655, 10, 14)


# from pgp tests


#     # month/year
#     seleucid_year = 1458
#     converted_date = convert_seleucid_date(f"Tishri {seleucid_year}")
#     converted_date_am = convert_hebrew_date(
#         f"Tishrei {seleucid_year + Calendar.SELEUCID_OFFSET}"
#     )
#     # the converted date range for Tishri Sel. should be the same as that for Tishri AM - 3449 years.
#     assert converted_date[0] == converted_date_am[0]
#     assert converted_date[1] == converted_date_am[1]

#     # leap day (Feb 29, 2020) should convert properly
#     converted_date = convert_seleucid_date("4 Adar 2331")
#     assert converted_date[1] == date(2020, 2, 29)

#     # leap year (4826 AM = 1377 Seleucid) should convert properly
#     seleucid_year = 1377
#     converted_date = convert_seleucid_date(f"21 Adar II {seleucid_year}")
#     converted_date_am = convert_hebrew_date(
#         f"21 Adar II {seleucid_year + Calendar.SELEUCID_OFFSET}"
#     )
#     assert converted_date[0] == converted_date_am[0]
#     assert converted_date[1] == converted_date_am[1]
#     # and it should be converted to 1066-03-21 CE
#     assert converted_date[1] == date(1066, 3, 21)
