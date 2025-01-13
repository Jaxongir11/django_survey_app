import random
import string
from collections import namedtuple
from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.utils.text import slugify
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from accounts.models import Profile
from djf_surveys.utils import create_star


TYPE_FIELD = namedtuple(
    'TYPE_FIELD', 'text number radio select multi_select text_area url email date rating'
)._make(range(10))


TYPE_FIELD_CHOICES = [
    (TYPE_FIELD.text, _("Text")),
    (TYPE_FIELD.number, _("Number")),
    (TYPE_FIELD.radio, _("Radio")),
    (TYPE_FIELD.select, _("Select")),
    (TYPE_FIELD.multi_select, _("Multi Select")),
    (TYPE_FIELD.text_area, _("Text Area")),
    (TYPE_FIELD.url, _("URL")),
    (TYPE_FIELD.email, _("Email")),
    (TYPE_FIELD.date, _("Date")),
    (TYPE_FIELD.rating, _("Rating"))
]


def generate_unique_slug(klass, field, id, identifier='slug'):
    """
    Generate unique slug.
    """
    origin_slug = slugify(field)
    unique_slug = origin_slug
    numb = 1
    mapping = {
        identifier: unique_slug,
    }
    obj = klass.objects.filter(**mapping).first()
    while obj:
        if obj.id == id:
            break
        rnd_string = random.choices(string.ascii_lowercase, k=(len(unique_slug)))
        unique_slug = '%s-%s-%d' % (origin_slug, ''.join(rnd_string[:10]), numb)
        mapping[identifier] = unique_slug
        numb += 1
        obj = klass.objects.filter(**mapping).first()
    return unique_slug


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Direction(models.Model):
    name = models.CharField(_("nomi"), max_length=255)

    class Meta:
        verbose_name = _("direction")
        verbose_name_plural = _("O'quv kurslari")
        ordering = ['name']

    def __str__(self):
        return self.name


class Survey(BaseModel):
    name = models.CharField(_("nomi"), max_length=200)
    description = models.TextField(_("ta’rif"), default='')
    slug = models.SlugField(_("slug"), max_length=225, default='')
    editable = models.BooleanField(_("tahrirlanadigan"), default=True,
                                   help_text=_("Agar belgi qo‘yilmasa, foydalanuvchi yozuvni tahrirlay olmaydi."))
    deletable = models.BooleanField(_("o‘chirib tashlasa bo‘ladigan"), default=True,
                                    help_text=_("Agar belgi qo‘yilmasa, foydalanuvchi yozuvni o'chira olmaydi."))
    duplicate_entry = models.BooleanField(_("bitta foydalanuvchi bir necha marta yuborish mumkin"), default=False,
                                          help_text=_("Agar belgi qo‘yilsa, foydalanuvchi qayta topshirishi mumkin."))
    private_response = models.BooleanField(_("xususiy javob"), default=False,
                                           help_text=_("Agar belgi qo‘yilsa, faqat administrator va egasi kira oladi."))
    can_anonymous_user = models.BooleanField(_("anonim yuborish"), default=False,
                                             help_text=_("Agar belgi qo‘yilsa, autentifikatsiyasiz foydalanuvchi yuboradi."))
    notification_to = models.TextField(_("Bildirishnoma"), blank=True, null=True,
                                       help_text=_("Xabardor qilish uchun elektron pochta manzilingizni kiriting"))
    success_page_content = models.TextField(
        _("Muvaffaqiyatli yakunlash sahifasi mazmuni"), blank=True, null=True,
        help_text=_("Muvaffaqiyatli sahifasi shu yerda o‘zgartirishingiz mumkin. HTML sintaksisi qo‘llab-quvvatlanadi")
    )

    class Meta:
        verbose_name = _("survey")
        verbose_name_plural = _("So'rovnomalar")
        ordering = ['created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.slug:
            self.slug = generate_unique_slug(Survey, self.slug, self.id)
        else:
            self.slug = generate_unique_slug(Survey, self.name, self.id)
        super().save(*args, **kwargs)


class Question(BaseModel):
    type_field = models.PositiveSmallIntegerField(_("kiritish maydonining turi"), choices=TYPE_FIELD_CHOICES)

    key = models.CharField(
        _("kalit"), max_length=225, unique=True, null=True, blank=True,
        help_text=_("Noyob kalit savol matnidan avtomatik yaratiladi. Yaratishni istasangiz, bo‘sh joyni to‘ldiring.")
    )
    survey = models.ForeignKey(Survey, related_name='questions', on_delete=models.CASCADE, verbose_name=_("survey"))
    label = models.CharField(_("Yorliq"), max_length=500, help_text=_("Savolingizni shu yerga kiriting."))
    choices = models.TextField(
        _("variantlar"),
        blank=True, null=True,
        help_text=_(
            "Agar maydon turi radio, tanlanadigan yoki ko‘p variantli bo‘lsa, ajratilgan variantlarni to‘ldiring"
            "vergullar bilan. Masalan: Erkak, Ayol")
    )
    help_text = models.CharField(
        _("yordam matni"),
        max_length=200, blank=True, null=True,
        help_text=_("Bu yerda yordam matnini kiritishingiz mumkin.")
    )
    required = models.BooleanField(_("talab qilinadi"), default=True,
                                   help_text=_("Agar belgi qo‘yilsa, foydalanuvchi ushbu savolga javob berishi kerak."))
    ordering = models.PositiveIntegerField(_("variantlar"), default=0,
                                           help_text=_("So‘rovnomalar doirasida savollar tartibini belgilaydi."))

    class Meta:
        verbose_name = _("question")
        verbose_name_plural = _("Savollar")
        ordering = ["ordering"]

    def __str__(self):
        return f"{self.label}-survey-{self.survey.id}"

    def save(self, *args, **kwargs):
        if self.key:
            self.key = generate_unique_slug(Question, self.key, self.id, "key")
        else:
            self.key = generate_unique_slug(Question, self.label, self.id, "key")

        super(Question, self).save(*args, **kwargs)


class UserAnswer(BaseModel):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, verbose_name=_("survey"))
    user = models.ForeignKey(get_user_model(), blank=True, null=True, on_delete=models.CASCADE, verbose_name=_("user"))
    direction = models.ForeignKey(Direction, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = _("user answer")
        verbose_name_plural = _("Foydalanuvchi javoblari")
        ordering = ["-updated_at"]

    def __str__(self):
        return str(self.id)

    def get_user_photo(self):
        profile = getattr(self.user, 'profile', None)
        if profile and profile.image:
            return profile.image.url
        return settings.MEDIA_URL + 'user_image/default.png'


class Answer(BaseModel):
    question = models.ForeignKey(Question, related_name="answers", on_delete=models.CASCADE, null=True, verbose_name=_("question"))
    value = models.TextField(_("value"), help_text=_("Foydalanuvchi tomonidan berilgan javobning qiymati."))
    user_answer = models.ForeignKey(UserAnswer, on_delete=models.CASCADE, verbose_name=_("user answer"))

    class Meta:
        verbose_name = _("answer")
        verbose_name_plural = _("Javoblar")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.question}: {self.value}"

    @property
    def get_value(self):
        if self.question.type_field == TYPE_FIELD.rating:
            if not self.question.choices:  # use 5 as default for backward compatibility
                self.question.choices = 5
            return create_star(active_star=int(self.value) if self.value else 0, num_stars=int(self.question.choices))
        elif self.question.type_field == TYPE_FIELD.url:
            return mark_safe(f'<a href="{self.value}" target="_blank">{self.value}</a>')
        elif self.question.type_field == TYPE_FIELD.radio or self.question.type_field == TYPE_FIELD.select or \
                self.question.type_field == TYPE_FIELD.multi_select:
            return self.value.strip().replace("_", " ").capitalize()
        else:
            return self.value

    @property
    def get_value_for_csv(self):
        if self.question.type_field == TYPE_FIELD.radio or self.question.type_field == TYPE_FIELD.select or \
                self.question.type_field == TYPE_FIELD.multi_select:
            return self.value.strip().replace("_", " ").capitalize()
        else:
            return self.value.strip()


class Question2(BaseModel):
    # Faqat reyting savollari uchun type_field qiymatini o'rnatish
    type_field = models.PositiveSmallIntegerField(
        _("type of input field"), choices=[(TYPE_FIELD.rating, _("Rating"))], default=TYPE_FIELD.rating
    )
    key = models.CharField(
        _("kalit"), max_length=225, unique=True, null=True, blank=True,
        help_text=_("Noyob kalit savol matnidan avtomatik yaratiladi. Yaratishni istasangiz, bo‘sh joyni to‘ldiring.")
    )
    survey = models.ForeignKey(Survey, related_name='questions2', on_delete=models.CASCADE, verbose_name=_("survey"))
    label = models.CharField(_("yorliq"), max_length=500, help_text=_("Savolingizni shu yerga kiriting."))
    choices = models.TextField(
        _("variantlar"),
        blank=True, null=True,
        help_text=_("Reytingda yulduzlar sonini aniqlash uchun, masalan: 5")
    )
    help_text = models.CharField(
        _("yordam matni"),
        max_length=200, blank=True, null=True,
        help_text=_("Bu yerda yordam matnini kiritishingiz mumkin")
    )
    required = models.BooleanField(_("talab qilinadi"), default=True,
                                   help_text=_("Agar belgi qo‘yilsa, foydalanuvchi ushbu savolga javob berishi kerak."))
    ordering = models.PositiveIntegerField(_("variantlar"), default=0,
                                           help_text=_("So‘rovnomalar doirasida savollar tartibini belgilaydi."))

    class Meta:
        verbose_name = _("rating question")
        verbose_name_plural = _("Reyting savollari")
        ordering = ["ordering"]

    def __str__(self):
        return f"{self.label}-survey-{self.survey.id}"

    def save(self, *args, **kwargs):
        if self.key:
            self.key = generate_unique_slug(Question2, self.key, self.id, "key")
        else:
            self.key = generate_unique_slug(Question2, self.label, self.id, "key")
        super(Question2, self).save(*args, **kwargs)


class UserAnswer2(BaseModel):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, verbose_name=_("survey"))
    user = models.ForeignKey(
        get_user_model(),
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="rating_user",
        verbose_name=_("rating user")
    )

    direction = models.ForeignKey(Direction, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = _("user answer for Question2")
        verbose_name_plural = _("Foydalanuvchi reyting javoblari")
        ordering = ["-updated_at"]

    def __str__(self):
        return f"UserAnswer2-{self.id}: {self.user} rated multiple users"


class UserRating(BaseModel):
    user_answer = models.ForeignKey(UserAnswer2, on_delete=models.CASCADE, verbose_name=_("user answer2"))
    rated_user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, verbose_name=_("rated user"))

    class Meta:
        verbose_name = _("user rating")
        verbose_name_plural = _("O'qituvchilar reytingi")
        ordering = ["-created_at"]

    def __str__(self):
        return f"O'qituvchilar reytingini-{self.id}: {self.user_answer.user} baholadi {self.rated_user}ni"


class Answer2(BaseModel):
    question = models.ForeignKey(Question2, related_name="answers2", on_delete=models.CASCADE, verbose_name=_("question2"))
    value = models.PositiveIntegerField(_("value"), help_text=_("Reyting qiymati, masalan, 1 dan 5 gacha."))  # Reyting qiymat uchun moslashtirilgan
    user_rating = models.ForeignKey(UserRating, on_delete=models.CASCADE, verbose_name=_("user rating"))

    class Meta:
        verbose_name = _("answer for Question2")
        verbose_name_plural = _("Reyting javoblari")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.question}: {self.value} (Baholangan foydalanuvchi: {self.user_rating.rated_user})"

