
from django import template
from django.utils.safestring import mark_safe
from django.utils.html import escape

from urllib.parse import quote_plus

register = template.Library()

@register.filter
def order_by(qs, s):
    args = s.split(',')
    return qs.order_by(*args)

@register.filter
def span_math(s):
    i=0
    s = escape(s)
    while True:
        i = s.find('$',i)
        j = s.find('$',i+1)
        if i<0 or j<0:
            break
        pre = '<span class="math">'
        post = '</span>'
        s = s[0:i] + pre + s[i:j+1] + post + s[j+1:]
        i = j + len(pre) + len(post)
    return mark_safe(s)
    

@register.filter
def simpletags_line(s):
    if not s:
        return s
    o=''
    open_i=False
    open_b=False
    close_s=''
    i=0
    while i<len(s):
        if s[i]=='\\' and i+1<len(s) and s[i+1] in ['(','[']:
            if s[i+1]=='(':
                closetag='\)'
            else:
                closetag='\]'
            j=s.find(closetag,i+1)
            if j>=0:
                o+=s[i:j+2]
                i=j+2
                continue

        if s[i]=='$':
            closetag='$'
            j=s.find(closetag,i+1)
            if j>=0:
                r=s[i:j+1]
                for key,val in [('<','&lt;'),('>','&gt;'),('&','&amp;')]:
                    r.replace(key,val)
                o+=s[i:j+1]
                i=j+1
                continue
            
        if s[i]=='[':
            if i+1<len(s) and s[i+1]=='[':
                o+='['
                i+=2
                continue
            j=s.find(']',i+1)
            if j>=0:
                k=s.find('|',i+1,j)
                if k<0: k=i
                o+='<a href=\''+s[k+1:j]+'\'>'
                if k>i:
                    o+=s[i+1:k]+'</a>'
                else:
                    o+=s[k+1:j]+'</a>'
                i=j+1
                continue

        if s[i]==']':
            if i+1<len(s) and s[i+1]==']':
                o+=']'
                i+=2
                continue

        if s[i]=='/':
            if i+1<len(s) and s[i+1]=='/':
                o+='/'
                i+=1
            else:
                if open_i:
                    o+='</i>'
                    open_i=False
                else:
                    o+='<i>'
                    open_i=True
        elif s[i]=='*':
            if i+1<len(s) and s[i+1]=='*':
                o+='*'
                i+=1
            else:
                if open_b:
                    o+='</b>'
                    open_b=False
                else:
                    o+='<b>'
                    open_b=True
        elif s[i] in '^_':
            if i+1<len(s) and s[i+1]==s[i]:
                o+=s[i]
                i+=1
            else:
                o+=close_s
                if s[i]=='^':
                    o+='<sup>'
                    close_s='</sup>'
                else:
                    o+='<sub>'
                    close_s='</sub>'
        else:
            if s[i] in ' \n(-':
                o+=close_s
                close_s=''
            o+=s[i]
        i+=1
    o+=close_s
    if open_i:
        o+='</i>'
        open_i=False
    if open_b:
        o+='</b>'
        open_b=False
    return mark_safe(o)

@register.filter
def simpletags(s,opt=None):
    if not s: return s
    s=s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')    
    s=simpletags_line(s)
    s=s.replace("\r\n","\n")
    if opt=='nop':
        o=''
    else:
        o='<p>'
    open_ul=False
    open_li=False
    i=0
    while i<len(s):
        if s[i]=='|':
            if i+1<len(s) and s[i+1]==s[i]:
                o+=s[i]
                i+=1
            else:
                o+='<br>'
            pass
        elif s[i]=='\n':
            if i>0 and (s[i-1]=='\n') and (i<2 or s[i-2]!='\n'):
                if open_ul:
                    if open_li:
                        o+='</li>'
                        open_li=False
                    o+='</ul>\n<p>'
                    open_ul=False
                else:
                    o+='</p>\n<p>'
            else:
                o+=s[i]
        elif s[i]=='#' and (i==0 or s[i-1]=='\n'):
            if open_li:
                o+='</li>\n'
                open_li=False
            if not open_ul:
                o+='</p>\n<ul>'
                open_ul=True
            o+='<li>'
            open_li=True
        else:
            o+=s[i]
        i+=1
    if open_li:
        o+='</li>'
        open_li=False
    if open_ul:
        o+='</ul>'
        open_ul=False
    o+='</p>\n'
    return mark_safe(o)

MONTH_NAME = [ None, 'January', 'February', 'March',
                'April', 'May', 'June', 'July', 'August',
                'September', 'October', 'November', 'December',
                ]

NOME_MESE = [ None, 'gennaio', 'febbraio', 'marzo',
              'aprile', 'maggio', 'giugno', 'luglio', 'agosto',
              'settembre', 'ottobre', 'novembre', 'dicembre']

DAY_NAME = [ 'Monday','Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday' ]

@register.filter
def friendly(x,year=None):
#    print 'friendly',x
    try:
        if hasattr(x,'year'):
            if year and year == x.year:
                return '%d %s' %(x.day, MONTH_NAME[x.month])
            else:
                return '%d %s %d' % (x.day, MONTH_NAME[x.month], x.year)
        if hasattr(x,'hour'):
            return '%d:%.2d' % (x.hour,x.minute)
    except AttributeError:
        return x

@register.filter
def friendly_short(date):
    try:
        return '%s %d %s' % (DAY_NAME[date.weekday()][:3], date.day, MONTH_NAME[date.month][:3])
        return str(value)+'(%s)'%arg
    except AttributeError:
        return date

@register.filter
def friendly_ita(date):
    try:
        return '%d %s' % (date.day, NOME_MESE[date.month])
        return str(value)+'(%s)'%arg
    except AttributeError:
        return date

@register.filter
def month(date, year=None):
    if year and year == date.year:
        return MONTH_NAME[date.month]
    else:
        return MONTH_NAME[date.month]+' '+str(date.year)

@register.filter
def debug(x):
    return str(type(x))

class SetVar(template.Node):
    def __init__(self,var,value):
        self.var=var
        self.value=value
        print(("SetVar init(%s,%s)" % (self.var,self.value)))

    def render(self, context):
        print(("setting %s=%s" % (self.var,self.value)))
        context[self.var]=self.value
        return 'xxxx'

@register.tag
def set_menu(parser,token):
    try:
        tag_name, value = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires a single argument" % token.contents.split()[0])
    if not (value[0] == value[-1] and value[0] in ('"', "'")):
        raise template.TemplateSyntaxError("%r tag's argument should be in quotes" % tag_name)
    print("set_menu")
    return SetVar('MENU',value)

@register.tag
def set_submenu(parser,token):
    try:
        tag_name, value = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires a single argument" % token.contents.split()[0])
    if not (value[0] == value[-1] and value[0] in ('"', "'")):
        raise template.TemplateSyntaxError("%r tag's argument should be in quotes" % tag_name)
    return SetVar('SUBMENU',value)

@register.tag
def facebook_like(url):
    return '<!-- facebook_like not defined -->'
