
# coding: utf-8

# In[1]:


import pandas as pd
from django.db import transaction

from app.models import Poster, Event, RefereeMapping


# In[2]:


def normal_name(x):
    if not isinstance(x, str):
        return None
    lst = ['น.ส.', 'นางสาว', 'นาง', 'นาย', 'Mr.', 'Mrs.', 'Ms.', 'อ.', 'ผ.', 'ผศ.', 'รศ.', 'ศ.', 'นพ.', 'ดร.',
           'ผู้ช่วยศาสตราจารย์', 'อาจารย์', 'ผศ']
    for word in lst:
        x = x.replace(word, '')
    x = x.replace('  ', ' ')
    x = x.replace('   ', ' ')
    x = x.replace('พล  จันทร์', 'พล จันทร์')
    return x.strip()


# In[3]:


columns = ['poster_id', 'order', 'title', 'prefix_1', 'name_1',
           'prefix_2', 'name_2', 'prefix_3', 'name_3',  'prefix_4', 'name_4',
           'advisor', 'co-advisor', 'department', 'type', 'hilight', 'ref1', 'ref2', 'ref3']


# In[4]:


posters = pd.read_excel(
    './data/สรุปกรรมการโครงงาน-final.xlsx', names = columns, sheet_name = "รวมโครงงาน8พค61")


# In[5]:


posters.ref1 = posters.ref1.apply(normal_name)
posters.ref2 = posters.ref2.apply(normal_name)
posters.ref3 = posters.ref3.apply(normal_name)


# In[6]:


# for i, r in posters.iterrows():
#     print(r.ref1)
#     print(r.ref2)
#     print(r.ref3)
#     print()


# In[7]:


posters = posters.fillna('')


# In[8]:


posters


# In[9]:


posters.type.unique()


# In[10]:


posters.department.unique()


# In[11]:


event_obj = Event.objects.get(pk=1)
bulk = list()

unknown = set()
for i, r in posters.iterrows():
    event = event_obj
    poster_id = r.poster_id
    title = r.title
    hilight = r.hilight
    advisor = r.advisor
    co_advisor = r["co-advisor"]
    department = r.department
    types = r.type
    student_1 = None
    if r.name_1:
        student_1 = str(r.prefix_1) + str(r.name_1)
    student_2 = None
    if r.name_2:
        student_2 = str(r.prefix_2) + str(r.name_2)
    student_3 = None
    if r.name_3:
        student_3 = str(r.prefix_3) + str(r.name_3)
    student_4 = None
    if r.name_4:
        student_4 = str(r.prefix_4) + str(r.name_4)

    params = {
        'event': event,
        'poster_id': poster_id,
        'title': title,
        'hilight': hilight,
        'student_1': student_1,
        'student_2': student_2,
        'student_3': student_3,
        'student_4': student_4,
        'advisor': advisor,
        'co_advisor': co_advisor,
        'department': department,
        'type': types,
    }
    bulk.append(Poster(**params))
Poster.objects.bulk_create(bulk)

# In[12]:

print('-- unkonw ref --')
print(unknown)
print('----------------')
print()


# In[13]:

# with transaction.atomic():
#     for i, r in posters.iterrows():
#         try:
#             poster = Poster.objects.get(poster_id=r.poster_id, title=r.title)
#         except Exception as err:
#             #
#             # Duplicated code
#             #
#             # SP_tech606096
#             print('Duplicated: ', r.poster_id)
#             continue
#         refs = list()
#         for i in range(1, 4):
#             x = getattr(r, 'ref{}'.format(i))
#             if x:
#                 try:
#                     ref = RefereeMapping.objects.get(name=x)
#                     refs.append(ref)
#                 except:
#                     unknown.add(x)
#         poster.referees.add(*refs)
#         poster.save()

# In[13]:
ref_set = RefereeMapping.objects.all()
posters = Poster.objects.all()
with transaction.atomic():
    for poster in posters:
        poster.referees.add(*ref_set)
        poster.save
