from z3c.form.interfaces import IFieldWidget
from z3c.form.widget import FieldWidget
from zope.interface import implements


# TODO: let's remove this, once an alternative is provided by plone.autoform or
# any other package.

# Use the parameterized widget factory to add widgets with specific parameters.
class ParameterizedFieldWidget(object):
    implements(IFieldWidget)

    def __new__(cls, field, request):
        widget = FieldWidget(field, cls.widget(request))
        for k, v in cls.kw.items():
            setattr(widget, k, v)
        return widget

def ParameterizedWidgetFactory(widget, **kw):
    return type('%sFactory' % widget.__name__,
                (ParameterizedFieldWidget,),
                {'widget': widget, 'kw': kw})
