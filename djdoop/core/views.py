from django.conf import settings
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, Http404

from djzbar.utils.informix import do_sql as do_esql
#from djzbar.utils.decorators import portal_login_required
from djtools.utils.date import calculate_age
from djtools.fields import TODAY

import logging
logger = logging.getLogger(__name__)

def is_member(user,group):
    """
    simple method to check if a user belongs to a group
    """
    return user.groups.filter(name=group)

def get_data(table,cid,fields=None,date=None):
    """
    table   = name of database table
    fields  = list of database fields to return
    key     = dict with unique identifier and value
    """
    status = False
    sql = "SELECT "
    if fields:
        sql += ','.join(fields)
    else:
        sql += "*"
    sql += " FROM %s WHERE college_id=%s" % (table,cid)
    if date:
        sql += " AND created_at?"
    result = do_esql(sql)
    return result

def put_data(dic,table,cid=None,noquo=[]):
    """
    dic:    dictionary of data
    table:  the name of the table in the database
    cid:    create or update
    noquo:  a list of field names that do not require quotes
    """
    if cid:
        prefix = 'UPDATE %s SET ' % table
        for key,val in dic.items():
            # strip quotes
            if key not in noquo:
                try:
                    val = val.replace('"', '')
                except:
                    pass
            # informix expects 1 or 0
            if val == True:
                val = 1
            if val == False:
                val = 0
            prefix += '%s=' % key
            if noquo and key in noquo:
                prefix += '%s,' % val
            else:
                prefix += '"%s",' % val
        sql = '%s WHERE college_id=%s' % (prefix[:-1],cid)
    else:
        prefix = 'INSERT INTO %s' % table
        fields = '('
        values = 'VALUES ('
        for key,val in dic.items():
            # strip quotes
            if key not in noquo:
                try:
                    val = val.replace('"', '')
                except:
                    pass
            # informix expects 1 or 0
            if val == True:
                val = 1
            if val == False:
                val = 0
            fields +='%s,' % key
            if noquo and key in noquo:
                values +='%s,' % val
            else:
                values +='"%s",' % val
        fields = '%s)' % fields[:-1]
        values = '%s)' % values[:-1]
        sql = '%s %s %s' % (prefix,fields,values)
    do_esql(sql,key=settings.INFORMIX_DEBUG)

def update_manager(field,cid):
    """
    simple method to update the manager table
    which we use throughout the app
    """
    put_data(
        {field:1,"college_id":cid},
        "cc_student_medical_manager",
        cid=cid,
        noquo=[field,"college_id"]
    )

@csrf_exempt
def set_type(request):
    field = request.POST.get("field")
    cid = request.POST.get("college_id")
    if not cid:
        cid = request.user.id
    table="cc_student_medical_manager"
    # check for student manager record
    student = None
    obj = get_data(table,cid)
    if obj:
        student = obj.fetchone()
    update = None
    if student:
        update = cid

    # sports field is a list
    if field == "sports":
        switch = ','.join(request.POST.getlist("switch[]"))
    else:
        switch = request.POST.get("switch")

    dic = {field:switch,"college_id":cid}
    noquo=["athlete","college_id","cc_student_immunization"]
    put_data( dic, table, cid = update, noquo=noquo )

    return HttpResponse(switch, mimetype="text/plain; charset=utf-8")

#@portal_login_required

def responsive_switch(request,action):
    if action=="go":
        request.session['desktop_mode']=True
    elif action=="leave":
        request.session['desktop_mode']=False
    return HttpResponseRedirect(request.META.get("HTTP_REFERER", ""))
