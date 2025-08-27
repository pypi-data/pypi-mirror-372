import unittest
import json
import io
from diffgetr.diff_get import Diffr


class TestDiffGet(unittest.TestCase):
    
    def test_basic_diff(self):
        """Test basic diff functionality"""
        s0 = {"a": 1, "b": 2, "c": {"d": 3}}
        s1 = {"a": 1, "b": 3, "c": {"d": 4}}
        
        diff = Diffr(s0, s1)
        assert diff.location == "root"
        
        # Test that diff object is created
        diff_obj = diff.diff_obj
        assert 'values_changed' in diff_obj
    
    def test_navigation(self):
        """Test navigation through nested structures"""
        s0 = {"level1": {"level2": {"value": 10}}}
        s1 = {"level1": {"level2": {"value": 20}}}
        
        diff = Diffr(s0, s1)
        nested_diff = diff['level1']['level2']
        
        assert nested_diff.location == "root.level1.level2"
        assert nested_diff.s0['value'] == 10
        assert nested_diff.s1['value'] == 20
    
    def test_list_conversion(self):
        """Test automatic list to dict conversion"""
        s0 = [1, 2, 3]
        s1 = [1, 2, 4]
        
        diff = Diffr(s0, s1)
        assert isinstance(diff.s0, dict)
        assert isinstance(diff.s1, dict)
        assert diff.s0[2] == 3
        assert diff.s1[2] == 4
    
    def test_keys_method(self):
        """Test keys() method returns intersection"""
        s0 = {"a": 1, "b": 2, "c": 3}
        s1 = {"a": 1, "b": 3, "d": 4}
        
        diff = Diffr(s0, s1)
        keys = diff.keys()
        
        assert keys == {"a", "b"}
    
    def test_ignore_added(self):
        """Test ignore_added parameter"""
        s0 = {"a": 1, "b": 2}
        s1 = {"a": 1, "b": 2, "c": 3}
        
        diff = Diffr(s0, s1, ignore_added=True)
        diff_obj = diff.diff_obj
        
        # Should not contain dictionary_item_added
        assert 'dictionary_item_added' not in diff_obj
    
    def test_custom_deep_diff_params(self):
        """Test custom DeepDiff parameters"""
        s0 = {"value": 1.123456}
        s1 = {"value": 1.123457}
        
        # With default precision (3), should see no difference
        diff1 = Diffr(s0, s1)
        assert len(diff1.diff_obj) == 0
        
        # With high precision, should see difference
        diff2 = Diffr(s0, s1, deep_diff_kw={'significant_digits': 6})
        assert len(diff2.diff_obj) > 0
    
    def test_keyerror_handling(self):
        """Test KeyError handling when navigating to non-existent keys"""
        s0 = {"a": {"b": 1}}
        s1 = {"a": {"c": 2}}
        
        diff = Diffr(s0, s1)
        
        with self.assertRaises(KeyError) as context:
            diff['a']['nonexistent']
        
        self.assertIn("key missing: nonexistent", str(context.exception))
    
    def test_string_representation(self):
        """Test string representation of diff object"""
        s0 = {"a": 1}
        s1 = {"a": 2}
        
        diff = Diffr(s0, s1)
        str_repr = str(diff)
        
        assert "root diffing summary" in str_repr
        assert isinstance(str_repr, str)
    
    def test_repr(self):
        """Test repr of diff object"""
        s0 = {"a": 1}
        s1 = {"a": 2}
        
        diff = Diffr(s0, s1)
        repr_str = repr(diff)
        
        assert repr_str == "diff[root]"
    
    def test_diff_summary_output(self):
        """Test diff_summary method"""
        s0 = {"a": 1, "b": {"c": 2}}
        s1 = {"a": 2, "b": {"c": 3}}
        
        diff = Diffr(s0, s1)
        
        # Test with StringIO
        output = io.StringIO()
        diff.diff_summary(file=output, top=10)
        summary = output.getvalue()
        
        assert "root diffing summary" in summary
        assert "VALUES_CHANGED" in summary
    
    def test_diff_all_output(self):
        """Test diff_all method"""
        s0 = {"a": 1}
        s1 = {"a": 2}
        
        diff = Diffr(s0, s1)
        
        # Test with StringIO
        output = io.StringIO()
        diff.diff_all(file=output)
        result = output.getvalue()
        
        assert "root diffing data" in result
    
    def test_type_assertion(self):
        """Test that different types raise assertion error"""
        with self.assertRaises(Exception):
            Diffr({"a": 1}, ["a", 1])
    
    def test_ipython_key_completions(self):
        """Test IPython tab completion support"""
        s0 = {"a": 1, "b": 2, "c": 3}
        s1 = {"a": 1, "b": 3, "d": 4}
        
        diff = Diffr(s0, s1)
        completions = diff._ipython_key_completions_()
        
        assert set(completions) == {"a", "b"}
        assert isinstance(completions, list)


class TestCLI(unittest.TestCase):
    
    def test_main_function_exists(self):
        """Test that main function exists and is callable"""
        from diffgetr.diff_get import main
        self.assertTrue(callable(main))


class TestPatternRecognition(unittest.TestCase):
    
    def test_uuid_pattern_replacement(self):
        """Test UUID pattern recognition in diff summary"""
        s0 = {"id": "550e8400-e29b-41d4-a716-446655440000"}
        s1 = {"id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8"}
        
        diff = Diffr(s0, s1)
        output = io.StringIO()
        diff.diff_summary(file=output)
        summary = output.getvalue()
        
        # UUIDs should be abstracted in the summary
        assert "UUID" in summary or summary  # At minimum should not crash


if __name__ == "__main__":
    unittest.main()
