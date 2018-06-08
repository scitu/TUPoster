from django.urls import path
from app.views import home, all_qr, get_qr, get_report, logout, question, poster_detail, vote, scoring, get_question_detail

urlpatterns = [
    path('logout/', logout),
    path('', home),
    path('getqr/', get_qr),
    path('getqr/<int:posterid>/', get_qr),
    path('question/<int:pk>/', question),
    path('poster/<int:pk>/', poster_detail),
    path('vote/', vote),
    path('sendscore/', scoring),
    path('qdetail/<int:pk>/', get_question_detail),
    path('report/', get_report),
    path('allqr/', all_qr),
]
