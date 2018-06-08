import traceback
import pandas as pd
from django.db import transaction
from app.models import RefereeMapping, Question, Score, Event, Poster

df = pd.read_excel('./data/score_template.xlsx')
event = Event.objects.get(pk=1)
is_pass = True
with transaction.atomic():
    for i, r in df.iterrows():
        try:
            referee = RefereeMapping.objects.get(natid=r['natid'])
            poster = Poster.objects.get(poster_id=r['poster'])
        except Exception as err:
            is_pass = False
            print('--- Invalid ---')
            print(i, r)
            traceback.print_exc()

        try:
            q1_message = 'ความสวยงาม ความเหมาะสม อ่านง่าย สื่อความหมายชัดเจน และตรงตามรูปแบบที่กำหนด'
            q1 = Question.objects.get(message=q1_message)
            s1 = r['(1) ความสวยงาม']
            s1_inst = Score.objects.update_or_create(poster=poster, referee=referee,
                            question=q1, defaults={'value': s1})
        except Exception as err:
            is_pass = False
            print('--- Invalid Q1---')
            print(i, r)
            traceback.print_exc()

        try:
            q2_message = 'โจทย์วิจัยชัดเจน วิธีการเหมาะสม และการเสนอผลการทดลองถูกต้อง โอกาสการนำไปใช้ประโยชน์'
            q2 = Question.objects.get(message=q2_message)
            s2 = r['(2) โจทย์วิจัยชัดเจน']
            s2_inst = Score.objects.update_or_create(poster=poster, referee=referee,
                            question=q2, defaults={'value': s2})
        except Exception as err:
            is_pass = False
            print('--- Invalid Q2---')
            print(i, r)
            traceback.print_exc()

        try:
            q3_message = 'การนำเสนอ (ชัดเจน และถูกต้อง)\nการตอบคำถาม (ตรงประเด็น และชัดเจน)'
            q3 = Question.objects.get(message=q3_message)
            s3 = r['(3) การนำเสนอ']
            s3_inst = Score.objects.update_or_create(poster=poster, referee=referee,
                            question=q3, defaults={'value': s3})
        except Exception as err:
            is_pass = False
            print('--- Invalid Q3---')
            print(i, r)
            traceback.print_exc()

print('is pass: ', is_pass)
