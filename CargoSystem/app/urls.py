from django.conf.urls import url
from . import views
from .views import RegisterView

urlpatterns = [
    url(r'^login/$', views.login, name='login'),
    url(r'^register/$', RegisterView.as_view(), name='register_view'),
    url(r'^logout/$', views.logout_view, name='logout'),
    url(r'^cargo/(?P<pk>\d+)/$', views.cargo_detail, name='cargo_detail'),
    url(r'^cargo/$', views.cargo_list, name='cargo_list'),
    url(r'^cargo/$', views.cargos_list, name='cargos_list'),
    url(r'^cargo/center/$', views.cargo_center_list, name='cargo_center_list'),
]
