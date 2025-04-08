from unittest import TestCase

from gi.repository import GLib, Gtk

Gtk.init()
from pygobject_templatemeta.template import Template

TEST_XML = """<?xml version="1.0" encoding="utf-8" ?>
<interface>
    <template class='TemplateTest' parent='GtkWidget'>
        <signal name='notify' handler='on_test_notify' />
        <child>
            <object class='GtkButton' id='test_button'>
                <property name='label'>Test Button</property>
            </object>
        </child>
    </template>
</interface>
"""


class TestTemplate(TestCase):

    def test_template(self, template: Template):
        self.assertTrue(template.class_name == 'TemplateTest')
        self.assertTrue(template.parent_type is Gtk.Widget)
        self.assertTrue(len(template.children) == 1)
        self.assertEqual(len(template.children), 1)
        self.assertIn('test_button', template.children)

        for k, v in {'type_name': 'GtkButton',
                     'id_': 'test_button'}.items():
            self.assertEqual(getattr(template.children['test_button'], k), v)

        return True

    def test_from_string(self):
        template = Template.from_string(TEST_XML.encode())
        self.assertTrue(self.test_template(template))

    def test_from_bytes(self):
        test_bytes = GLib.Bytes(TEST_XML.encode('utf-8'))
        template = Template.from_bytes(test_bytes)
        self.assertTrue(self.test_template(template))
