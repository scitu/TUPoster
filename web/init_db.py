import os
import shutil
import json
from collections import defaultdict
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.files import File
from django.core.files.base import ContentFile
from django.core.files.images import ImageFile

from app.models import Event, Question

User = get_user_model()

print()
print('='*40)
_secret_path = os.path.join('secret', 'setup.json')

print("Read secret variable")
try:
    with open(_secret_path, 'r') as fp:
        print(fp)
        secret_var = json.load(fp)
except IOError as err:
    secret_var = {
        'admin_email': '',
        'admin_username': 'admin',
        'admin_password': 'qwer1234'
    }
    print('********************************************')
    print('!!! Secret File Not Found, use default value')
    print('********************************************')
    for k, v in secret_var.items():
        print('\t{}: {}'.format(k, v))
secret_var = defaultdict(str, secret_var)

print()
print("- Create Admin user")
try:
    admin = User.objects.create_superuser(
        username=secret_var['admin_username'],
        password=secret_var['admin_password'],
        email=secret_var['admin_email']
    )
except:
    print(err)

print()
print('- create academic group -')
academic_group = Group.objects.create(name='academic')
p1 = Permission.objects.get(codename='add_event')
p2 = Permission.objects.get(codename='change_event')
p3 = Permission.objects.get(codename='add_poster')
p4 = Permission.objects.get(codename='change_poster')
p5 = Permission.objects.get(codename='add_question')
p6 = Permission.objects.get(codename='change_question')
academic_group.permissions.add(p1, p2, p3, p4, p5, p6)

#
# Initial event
#
event = Event.objects.create(
    title="Sci 2018",
    place="TU Rangsit",
    max_vote=1,
    datetime="2018-05-12 10:00:00",
)

q1 = Question.objects.create(
    event=event,
    message="ความสวยงาม ความเหมาะสม อ่านง่าย สื่อความหมายชัดเจน และตรงตามรูปแบบที่กำหนด",
    max_score=10
)
q2 = Question.objects.create(
    event=event,
    message="โจทย์วิจัยชัดเจน วิธีการเหมาะสม และการเสนอผลการทดลองถูกต้อง โอกาสการนำไปใช้ประโยชน์",
    max_score=20
)

q3 = Question.objects.create(
    event=event,
    message="การนำเสนอ (ชัดเจน และถูกต้อง)\nการตอบคำถาม (ตรงประเด็น และชัดเจน)",
    max_score=20
)

print()
print('-- init complete --')
print()
