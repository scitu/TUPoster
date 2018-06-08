import json
from app.models import RefereeMapping, Poster

with open('./data/dummy_data.json', 'r') as fp:
    data = json.load(fp)
dref = RefereeMapping.objects.create(**data[0])
rposter = Poster.objects.get(pk=1)
print(rposter)
print(rposter.referees.all().count())
rposter.referees.add(dref)
print(rposter.referees.all().count())
rposter.save()
