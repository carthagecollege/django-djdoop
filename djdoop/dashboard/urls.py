from django.conf.urls import patterns, url
from django.views.generic import TemplateView

urlpatterns = patterns('djdoop.dashboard.views',
    url(
        r'^success/$',
        TemplateView.as_view(
            template_name='dashboard/success.html'
        ),
        name='admin_success'
    ),
    # ajax communication to paint the panels
    url(
        r'^panels/$',
        'panels', name="dashboard_panels"
    ),
    # ajax communication for x-editable jquery plugin
    # pronounced 'sheditable' :-)
    url(
        r'^xeditable/$',
        'xeditable', name="dashboard_xeditable"
    ),
    # ajax returns students because using home view is a
    # pain in the ass with security involved & spinner
    url(
        r'^get-students/$',
        'get_students', name="get_students"
    ),
    # search
    url(
        r'^student/$',
        'student_detail', name="student_search"
    ),
    # profiled pair detail
    url(
        r'^profiled_pair/(?P<cid>\d+)/$',
        'profiled_pair_detail', name="profiled_pair_detail"
    ),
    # student detail print
    url(
        r'^student/(?P<cid>\d+)/print/$',
        'student_detail',
        {"template":"dashboard/student_detail_print.html"},
        name="student_detail_print"
    ),
    # home
    url(
        r'^$', 'home', name="dashboard_home"
    ),
)
