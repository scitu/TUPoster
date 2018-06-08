import json
import requests
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in
from django.contrib.auth.models import AbstractUser
from django.db import transaction

from app.exceptions import OverScoreException, NeedRefereePermissinException,\
    VotingUnavailableException, NeedSciPermissionException, VoteLimitationException


class MyUser(AbstractUser):
    STUDENT = '1'
    STAFF = '2'
    INSTRUCTOR = '3'
    ROLE_CHOICES = [
        (STUDENT, 'student'),
        (STAFF, 'staff'),
        (INSTRUCTOR, 'instructor'),
    ]

    is_sci_member = models.BooleanField(default=False)
    role = models.CharField(max_length=2, choices=ROLE_CHOICES, default=STUDENT)
User = get_user_model()


class Event(models.Model):
    title = models.CharField(max_length=128)
    place = models.TextField(null=True, blank=True)
    datetime = models.DateTimeField(null=True, blank=True)
    max_vote = models.PositiveSmallIntegerField(default=2)
    voteable = models.BooleanField(default=True)

    def get_available_question(self):
        return self.question_set.filter(is_use=True)

    def __str__(self):
        return self.title


class RefereeMapping(models.Model):
    DEPARTMENT_CHOICE = [('0', 'คณิตศาสตร์และสถิติ'), ('1', 'วิทยาการคอมพิวเตอร์'), ('2', 'เทคโนโลยีเพื่อการพัฒนายั่งยืน'),
                          ('3', 'เทคโนโลยีการเกษตร'), ('4', 'เคมี'), ('5', 'ฟิสิกส์'), ('6', 'วิทยาศาสตร์และเทคโนโลยีการอาหาร'),
                          ('7', 'วิทยาศาสตร์สิ่งแวดล้อม'), ('8', 'เทคโนโลยีชีวภาพ'), ('9', 'เทคโนโลยีวัสดุและสิ่งทอ'),
                          ('10', 'โครงการหลักสูตรนานาชาติ')]

    natid = models.CharField(max_length=13, unique=True)
    name = models.CharField(max_length=128)
    department = models.CharField(max_length=64, null=True, blank=True)
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.PROTECT)

    def __str__(self):
        return "{} {}".format(self.natid, self.name)

class Question(models.Model):
    event = models.ForeignKey(Event, on_delete=models.PROTECT)
    message = models.TextField()
    max_score = models.PositiveSmallIntegerField(default=5)
    is_use = models.BooleanField(default=True)


    def __str__(self):
        return self.message


class Poster(models.Model):
    TYPE_CHOICE = [('0', 'Technology'), ('1', 'Environmental and Sustainability'), ('2', 'Physical Sciences'),
                    ('3', 'Life Sciences'), ('4', 'Digital and Data Analysis'), ('5', 'Physical Science'),
                    ('6', ' Physical Sciences'), ('7', 'Theory'), ('8', 'Environment and Sutainability'),
                    ('9', 'Life Science'), ('10', 'Physical science')]

    DEPARTMENT_CHOICE = [('0', 'เทคโนโลยีดิจิทัลแนวสร้างสรรค์'), ('1', 'การออกแบบเชิงนวัตกรรมดิจิทัล'), ('2', 'วิทยาศาสตร์และเทคโนโลยีสิ่งทอ'),
        ('3', 'ฟิสิกส์'), ('4', 'โครงการ วมว.'), ('5', 'เคมี'), ('6', 'วิทยาศาสตร์และเทคโนโลยีการอาหาร'), ('7', 'วิทยาศาสตร์สิ่งแวดล้อม'),
        ('8', 'วัสดุศาสตร์'), ('9', 'เทคโนโลยีเพื่อการพัฒนายั่งยืน'), ('10', 'ฟิสิกส์อิเล็กทรอนิกส์'), ('11', 'เทคโนโลยีชีวภาพ'), ('12', 'คณิตศาสตร์และสถิติ'),
        ('13', 'คณิตศาสตร์การจัดการ'), ('14', 'เทคโนโลยีการเกษตร'), ('15', 'วิทยาศาสตร์อุตสาหการและการจัดการ'), ('16', 'วิทยาการคอมพิวเตอร์')]

    event = models.ForeignKey(Event, on_delete=models.PROTECT)
    poster_id = models.CharField(max_length=32)
    title = models.TextField()
    hilight = models.TextField(null=True, blank=True)
    student_1 = models.CharField(max_length=128, null=True, blank=True)
    student_2 = models.CharField(max_length=128, null=True, blank=True)
    student_3 = models.CharField(max_length=128, null=True, blank=True)
    student_4 = models.CharField(max_length=128, null=True, blank=True)
    advisor = models.CharField(max_length=128, null=True, blank=True)
    co_advisor = models.CharField(max_length=128, null=True, blank=True)

    department = models.CharField(max_length=128, null=True,
                            blank=True)
    type = models.CharField(max_length=128, null=True,
                            blank=True)
    referees = models.ManyToManyField(RefereeMapping, related_name="ref_poster")

    def __str__(self):
        return "{} {}".format(self.poster_id, self.title)

class Score(models.Model):
    question = models.ForeignKey(Question, on_delete=models.PROTECT)
    referee = models.ForeignKey(RefereeMapping, on_delete=models.PROTECT)
    poster = models.ForeignKey(Poster, on_delete=models.PROTECT)
    value = models.IntegerField()

    class Meta:
        unique_together = ('question', 'referee', 'poster')

    def save(self, *args, **kwargs):
        if not self.poster.event.voteable:
            raise VotingUnavailableException(
                'Voting are unavailable at this time.')
        if not self.referee in self.poster.referees.all():
            raise NeedRefereePermissinException(
                'Need permission to score this poster.')
        if self.value > self.question.max_score:
            raise OverScoreException('Over max score.')
        super(Score, self).save(*args, **kwargs)

    def __str__(self):
        return "{} {}".format(self.question, self.value)


class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    poster = models.ForeignKey(Poster, on_delete=models.PROTECT)
    is_use = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'poster')

    def is_sci_user(self):
        return self.user.is_sci_member

    def save(self, *args, **kwargs):
        if not self.poster.event.voteable:
            raise VotingUnavailableException(
                'Voting are unavailable at this time.')
        if self.is_use:
            if not self.is_sci_user():
                raise NeedSciPermissionException('Only Sci student.')
            if self.user.vote_set.filter(is_use=True).count() >= self.poster.event.max_vote:
                raise VoteLimitationException('Limit vote exceed.')
        super(Vote, self).save(*args, **kwargs)
    def __str__(self):
        return "{} {}".format(self.user, self.poster)


#
# Signal Observe
#
def logged_in_handle(sender, user, request, **kwargs):
    #
    # Check if TU login
    prov = user.social_auth.filter(provider='tu')
    if prov.exists():
        data = prov[0].extra_data
        headers = {"Authorization": "Bearer {}".format(data['access_token'])}
        res = requests.get('https://api.tu.ac.th/api/me/', headers=headers).json()

        refs = RefereeMapping.objects.filter(natid=res['description'])
        if refs.exists():
            ref = refs[0]
            ref.user = user
            ref.save()

        is_sci = False
        if res['company'] == 'คณะวิทยาศาสตร์และเทคโนโลยี':
            is_sci = True
        elif res['username'].isdigit() and res['username'][2:4] == '09':
            is_sci = True
        user.is_sci_member = is_sci
        if res['role']:
            user.role = res['role']
        user.save()

user_logged_in.connect(logged_in_handle)
