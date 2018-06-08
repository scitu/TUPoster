
# coding: utf-8

# In[1]:


import os, django
django.setup()


# In[2]:


import pandas as pd
from app.models import RefereeMapping


# In[3]:


poster = pd.read_excel('./data/รายชื่อกรรมการตัดสินโครงงาน7พค61.xlsx')


# In[4]:


def normal_name(x):
    if not isinstance(x, str):
        return None
    lst = ['น.ส.', 'นางสาว', 'นาง', 'นาย', 'Mr.', 'Mrs.', 'Ms.', 'อ.', 'ผ.', 'ผศ.', 'รศ.', 'ศ.', 'นพ.', 'ดร.',
           'ผู้ช่วยศาสตราจารย์', 'อาจารย์' ]
    for word in lst:
        x = x.replace(word, '')
    x = x.replace('  ', ' ')
    return x.strip()


# In[5]:


column = ['order', 'name', 'position', 'department', 'campus', 'type',
          'jobid', 'level', 'natid', 'education', 'education_full',
          'major', 'grad_university', 'remark']


# In[6]:


names = pd.read_excel('./data/name.xlsx', sheet_name="ฟ.3 สายวิชาการ (รายชื่อ)", names=column)[8:239]


# In[7]:


def get_null_mask(df):
    lst = []
    for i, r in df.iterrows():
        if 'อัตราว่าง' in r['name']:
            lst.append(False)
        else:
            lst.append(True)
    return lst
mask = get_null_mask(names)
names = names[mask]
names['name'] = names['name'].apply(normal_name)


# In[8]:


names


# In[9]:


names.department.unique()


# In[10]:

bulk = list()
for idx, row in names.iterrows():
    try:
        um = RefereeMapping(name=row['name'], natid=row['natid'], department=row['department'])
        um.save()
    except Exception as err:
        print(err)
        print(um)
        print(row)
        print()
#     bulk.append(um)
# RefereeMapping.objects.bulk_create(bulk)

