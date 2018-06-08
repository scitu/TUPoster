from django.contrib import admin
from app.models import RefereeMapping, Event, Poster, Vote, Question, Score, MyUser


class EventAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Event._meta.fields]


class QuestionAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Question._meta.fields]


class MyUserAdmin(admin.ModelAdmin):
    list_display = [f.name for f in MyUser._meta.fields]


class PosterAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Poster._meta.fields]
    list_filter = ['department', 'type']


class VoteAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Vote._meta.fields]


class ScoreAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Score._meta.fields]
    list_filter = ['question']


class RefereeMappingAdmin(admin.ModelAdmin):
    list_display = [f.name for f in RefereeMapping._meta.fields]
    list_filter = ['department']


admin.site.register(MyUser, MyUserAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Poster, PosterAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Vote, VoteAdmin)
admin.site.register(Score, ScoreAdmin)
admin.site.register(RefereeMapping, RefereeMappingAdmin)
