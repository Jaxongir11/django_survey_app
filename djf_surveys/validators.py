from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class RatingValidator(object):
    def __init__(self, max):
        self.max = max

    def __call__(self, value):
        try:
            rating = int(value)
        except (TypeError, ValueError):
            raise ValidationError(
                _('%ss son emas.' % value)
            )

        if rating > self.max:
            raise ValidationError(
                _('Qiymat ruxsat etilgan reytinglarning eng ko‘p miqdoridan oshib ketmasligi lozim.')
            )

        if rating < 1:
            raise ValidationError(
                _('Qiymat 1 dan kam bo‘lmasligi kerak.')
            )


