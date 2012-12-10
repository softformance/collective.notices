
import pytz

from collective.z3cform.datetimewidget.converter import DatetimeDataConverter as BaseConverter

from DateTime import DateTime


class DatetimeDataConverter(BaseConverter):

    def toFieldValue(self, value):
        value = super(DatetimeDataConverter, self).toFieldValue(value)
        if value is not self.field.missing_value:
            if not getattr(value, 'tzinfo', None):
                value = value.replace(tzinfo=pytz.timezone(DateTime().timezone()))
        return value
