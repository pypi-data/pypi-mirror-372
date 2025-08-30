import os
import pyExcelerator
import tempfile
import re
import datetime
import xml.sax.handler
from xml.parsers.expat import ExpatError
from django.template.loader import get_template

import django
from django.http import HttpResponse

def xml2obj(src):
    """
    A simple function to converts XML data into native Python object.
    """

#    logger.info('xml2obj(src), src=%s, type=%s' % (str(src),str(type(src))))

    non_id_char = re.compile('[^_0-9a-zA-Z]')
    def _name_mangle(name):
        return non_id_char.sub('_', name)

    class DataNode(object):
        def __init__(self):
            self._attrs = {}    # XML attributes and child elements
            self.data = None    # child text data
        def __len__(self):
            # treat single element as a list of 1
            return 1
        def __getitem__(self, key):
            if isinstance(key, str):
                return self._attrs.get(key,None)
            else:
                return [self][key]
        def __contains__(self, name):
            return name in self._attrs
        def __bool__(self):
            return bool(self._attrs or self.data)
        def __getattr__(self, name):
            if name.startswith('__'):
                # need to do this for Python special methods???
                raise AttributeError(name)
            return self._attrs.get(name,None)
        def _add_xml_attr(self, name, value):
            if name in self._attrs:
                # multiple attribute of the same name are represented by a list
                children = self._attrs[name]
                if not isinstance(children, list):
                    children = [children]
                    self._attrs[name] = children
                children.append(value)
            else:
                self._attrs[name] = value
        def __str__(self):
            return self.data or ''
        def __repr__(self):
            items = sorted(self._attrs.items())
            if self.data:
                items.append(('data', self.data))
            return '{%s}' % ', '.join(['%s:%s' % (k,repr(v)) for k,v in items])

    class TreeBuilder(xml.sax.handler.ContentHandler):
        def __init__(self):
            self.stack = []
            self.root = DataNode()
            self.current = self.root
            self.text_parts = []
        def startElement(self, name, attrs):
            self.stack.append((self.current, self.text_parts))
            self.current = DataNode()
            self.text_parts = []
            # xml attributes --> python attributes
            for k, v in list(attrs.items()):
                self.current._add_xml_attr(_name_mangle(k), v)
        def endElement(self, name):
            text = ''.join(self.text_parts).strip()
            if text:
                self.current.data = text
            if self.current._attrs:
                obj = self.current
            else:
                # a text only node is simply represented by the string
                obj = text or ''
            self.current, self.text_parts = self.stack.pop()
            self.current._add_xml_attr(_name_mangle(name), obj)
        def characters(self, content):
            self.text_parts.append(content)

    builder = TreeBuilder()
    if isinstance(src,str):
#        print 'src:',src
        xml.sax.parseString(src, builder)
    else:
        xml.sax.parse(src, builder)
    return list(builder.root._attrs.values())[0]

def xls_response(template, context, filename=None):
    # http://ntalikeris.blogspot.com/2007/10/create-excel-file-with-python-my-sort.html
    if not filename:
        filename = os.path.splitext(os.path.split(template)[1])[0]+'.xls'
    t=get_template(template)
    src=t.render(django.template.Context(context))
    src=str(src.encode('utf-8'))
#    print 'src: %s type: %s' % (src,type(src))
    xml=xml2obj(src)

    def assure_list(list_or_item):
        if list_or_item == None:
            return []
        elif type(list_or_item) == list:
            return list_or_item
        else:
            return [list_or_item]
    
    workbook = pyExcelerator.Workbook()
    default_style = pyExcelerator.XFStyle()
    date_style = pyExcelerator.XFStyle()
    date_style.num_format_str = 'M/D/YY'
#    myFont = pyExcelerator.Font()
#    myFont.colour_index=3
#    date_style.font = myFont
    count=0
    for xml_sheet in assure_list(xml.sheet):
        count+=1
#        print 'xml_sheet: %s' % xml_sheet._attrs
        sheet = workbook.add_sheet(xml_sheet.name)
        row_count=0
        for xml_row in assure_list(xml_sheet.row):
            cell_count=0
            if xml_row:
                for xml_cell in assure_list(xml_row.cell):
                    style=default_style
                    data=str(xml_cell)
                    if xml_cell.format=='date':
                        style=date_style
                        try:
                            data=datetime.datetime(int(data[0:4]),int(data[5:7]),int(data[8:10]))
                        except ValueError:
                            pass
                    sheet.write(row_count,cell_count,data,style)

                    cell_count+=1
            row_count+=1
    temp=tempfile.NamedTemporaryFile(suffix='xls')
    workbook.save(temp.name)
    response=HttpResponse(mimetype='application/xls')
    response.write(temp.read())
    response['Content-Disposition'] = 'attachment; filename=%s' % filename
    return response
