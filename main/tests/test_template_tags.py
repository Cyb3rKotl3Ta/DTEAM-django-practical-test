from django.test import TestCase
from django.template import Context, Template
from django.contrib.auth.models import User

from ..templatetags.settings_extras import (
    lookup, get_type, is_list, is_dict, format_setting_value
)


class TemplateTagsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_lookup_filter_with_dict(self):
        """Test lookup filter with dictionary."""
        test_dict = {'key1': 'value1', 'key2': 'value2', 'key3': 123}
        
        self.assertEqual(lookup(test_dict, 'key1'), 'value1')
        self.assertEqual(lookup(test_dict, 'key2'), 'value2')
        self.assertEqual(lookup(test_dict, 'key3'), 123)
        self.assertIsNone(lookup(test_dict, 'nonexistent'))

    def test_lookup_filter_with_none(self):
        """Test lookup filter with None."""
        self.assertIsNone(lookup(None, 'key'))

    def test_lookup_filter_with_non_dict(self):
        """Test lookup filter with non-dictionary object."""
        self.assertIsNone(lookup('string', 'key'))
        self.assertIsNone(lookup(123, 'key'))

    def test_get_type_filter(self):
        """Test get_type filter."""
        self.assertEqual(get_type('string'), 'str')
        self.assertEqual(get_type(123), 'int')
        self.assertEqual(get_type(123.45), 'float')
        self.assertEqual(get_type(True), 'bool')
        self.assertEqual(get_type([1, 2, 3]), 'list')
        self.assertEqual(get_type({'key': 'value'}), 'dict')
        self.assertEqual(get_type(None), 'NoneType')

    def test_is_list_filter(self):
        """Test is_list filter."""
        self.assertTrue(is_list([1, 2, 3]))
        self.assertTrue(is_list([]))
        self.assertFalse(is_list('string'))
        self.assertFalse(is_list(123))
        self.assertFalse(is_list({'key': 'value'}))
        self.assertFalse(is_list(None))

    def test_is_dict_filter(self):
        """Test is_dict filter."""
        self.assertTrue(is_dict({'key': 'value'}))
        self.assertTrue(is_dict({}))
        self.assertFalse(is_dict('string'))
        self.assertFalse(is_dict(123))
        self.assertFalse(is_dict([1, 2, 3]))
        self.assertFalse(is_dict(None))

    def test_format_setting_value_boolean(self):
        """Test format_setting_value filter with boolean values."""
        self.assertEqual(format_setting_value(True), 'True')
        self.assertEqual(format_setting_value(False), 'False')

    def test_format_setting_value_list(self):
        """Test format_setting_value filter with list values."""
        self.assertEqual(format_setting_value([1, 2, 3]), '[1, 2, 3]')
        self.assertEqual(format_setting_value(['a', 'b', 'c']), '[a, b, c]')
        self.assertEqual(format_setting_value([]), '[]')

    def test_format_setting_value_tuple(self):
        """Test format_setting_value filter with tuple values."""
        self.assertEqual(format_setting_value((1, 2, 3)), '[1, 2, 3]')
        self.assertEqual(format_setting_value(('a', 'b', 'c')), '[a, b, c]')
        self.assertEqual(format_setting_value(()), '[]')

    def test_format_setting_value_dict(self):
        """Test format_setting_value filter with dictionary values."""
        result = format_setting_value({'key1': 'value1', 'key2': 'value2'})
        self.assertIn('key1: value1', result)
        self.assertIn('key2: value2', result)

    def test_format_setting_value_long_string(self):
        """Test format_setting_value filter with long string values."""
        long_string = 'a' * 150
        result = format_setting_value(long_string)
        self.assertEqual(result, 'a' * 100 + '...')

    def test_format_setting_value_short_string(self):
        """Test format_setting_value filter with short string values."""
        short_string = 'short'
        result = format_setting_value(short_string)
        self.assertEqual(result, 'short')

    def test_format_setting_value_number(self):
        """Test format_setting_value filter with number values."""
        self.assertEqual(format_setting_value(123), '123')
        self.assertEqual(format_setting_value(123.45), '123.45')

    def test_lookup_filter_in_template(self):
        """Test lookup filter in Django template."""
        template_string = """
        {% load settings_extras %}
        <div>
            <p>Value1: {{ test_dict|lookup:'key1' }}</p>
            <p>Value2: {{ test_dict|lookup:'key2' }}</p>
            <p>Missing: {{ test_dict|lookup:'missing' }}</p>
        </div>
        """
        
        template = Template(template_string)
        context = Context({
            'test_dict': {'key1': 'value1', 'key2': 'value2'}
        })
        
        rendered = template.render(context)
        
        self.assertIn('Value1: value1', rendered)
        self.assertIn('Value2: value2', rendered)
        self.assertIn('Missing: ', rendered)  # Should be empty for missing key

    def test_get_type_filter_in_template(self):
        """Test get_type filter in Django template."""
        template_string = """
        {% load settings_extras %}
        <div>
            <p>String type: {{ test_string|get_type }}</p>
            <p>Number type: {{ test_number|get_type }}</p>
            <p>List type: {{ test_list|get_type }}</p>
        </div>
        """
        
        template = Template(template_string)
        context = Context({
            'test_string': 'hello',
            'test_number': 123,
            'test_list': [1, 2, 3]
        })
        
        rendered = template.render(context)
        
        self.assertIn('String type: str', rendered)
        self.assertIn('Number type: int', rendered)
        self.assertIn('List type: list', rendered)

    def test_is_list_filter_in_template(self):
        """Test is_list filter in Django template."""
        template_string = """
        {% load settings_extras %}
        <div>
            <p>Is list: {{ test_list|is_list }}</p>
            <p>Is not list: {{ test_string|is_list }}</p>
        </div>
        """
        
        template = Template(template_string)
        context = Context({
            'test_list': [1, 2, 3],
            'test_string': 'hello'
        })
        
        rendered = template.render(context)
        
        self.assertIn('Is list: True', rendered)
        self.assertIn('Is not list: False', rendered)

    def test_is_dict_filter_in_template(self):
        """Test is_dict filter in Django template."""
        template_string = """
        {% load settings_extras %}
        <div>
            <p>Is dict: {{ test_dict|is_dict }}</p>
            <p>Is not dict: {{ test_string|is_dict }}</p>
        </div>
        """
        
        template = Template(template_string)
        context = Context({
            'test_dict': {'key': 'value'},
            'test_string': 'hello'
        })
        
        rendered = template.render(context)
        
        self.assertIn('Is dict: True', rendered)
        self.assertIn('Is not dict: False', rendered)

    def test_format_setting_value_filter_in_template(self):
        """Test format_setting_value filter in Django template."""
        template_string = """
        {% load settings_extras %}
        <div>
            <p>Boolean: {{ test_bool|format_setting_value }}</p>
            <p>List: {{ test_list|format_setting_value }}</p>
            <p>String: {{ test_string|format_setting_value }}</p>
        </div>
        """
        
        template = Template(template_string)
        context = Context({
            'test_bool': True,
            'test_list': [1, 2, 3],
            'test_string': 'hello'
        })
        
        rendered = template.render(context)
        
        self.assertIn('Boolean: True', rendered)
        self.assertIn('List: [1, 2, 3]', rendered)
        self.assertIn('String: hello', rendered)

    def test_template_tags_with_settings_context(self):
        """Test template tags with settings context from context processor."""
        from ..context_processors import settings_context
        from django.test import RequestFactory
        
        factory = RequestFactory()
        request = factory.get('/')
        request.user = self.user
        
        # Get settings context
        context_dict = settings_context(request)
        
        template_string = """
        {% load settings_extras %}
        <div>
            <p>DEBUG: {{ settings|lookup:'DEBUG' }}</p>
            <p>DEBUG Type: {{ settings|lookup:'DEBUG'|get_type }}</p>
            <p>Is DEBUG bool: {{ settings|lookup:'DEBUG'|format_setting_value }}</p>
        </div>
        """
        
        template = Template(template_string)
        context = Context(context_dict)
        
        rendered = template.render(context)
        
        self.assertIn('DEBUG:', rendered)
        self.assertIn('DEBUG Type: bool', rendered)
        # DEBUG might be False in test environment
        self.assertIn('Is DEBUG bool:', rendered)
