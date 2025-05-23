import pytest
import sys
import importlib
from unittest.mock import patch, MagicMock
# from typing import Type # For type hinting <-- Removed

from undate.converters.base import BaseDateConverter, BaseCalendarConverter
from undate.converters.calendars.gregorian import GregorianDateConverter
# Ensure HebrewDateConverter is available for testing
from undate.converters.calendars.hebrew.converter import HebrewDateConverter
from undate.converters.edtf.converter import EDTFDateConverter # Corrected import
from undate.converters.iso8601 import ISO8601DateFormat # Corrected import

# Dummy converters for testing
class DirectDummyConverter(BaseDateConverter):
    name = "DirectDummy"
    def parse(self, value): pass
    def to_string(self, undate): pass

# This class is defined globally in the test module, so __subclasses__ will find it.
class NestedDummyConverterInTestModule(BaseDateConverter):
    name = "NestedDummyInTestModule"
    def parse(self, value): pass
    def to_string(self, undate): pass

# A dummy subclass of BaseCalendarConverter to ensure it's also found by BaseDateConverter's methods
class DummyCalendarSubclassConverter(BaseCalendarConverter):
    name = "DummyCalendarSubclass"
    calendar_type = "dummy_calendar_for_test" # Required by BaseCalendarConverter
    def parse(self, value): pass # Required by BaseDateConverter
    def to_string(self, undate): pass # Required by BaseDateConverter
    def to_gregorian(self, year, month, day): return (year, month, day) # Required
    def from_gregorian(self, year, month, day): return (year, month, day) # Required
    def min_month(self, year=None): return 1 # Required
    def max_month(self, year=None): return 12 # Required
    def max_day(self, year, month): return 31 # Required


class TestSubclassDiscoveryAndAvailability:

    def test_import_converters_caching_and_effect(self):
        BaseDateConverter.import_converters.cache_clear()

        with patch('pkgutil.iter_modules') as mock_iter_modules:
            # To make the test simpler, assume iter_modules returns a list of mock ModuleInfo objects
            # representing some modules to be imported.
            # We need to ensure these mock objects have 'name' and 'ispkg' attributes.
            mock_module_info1 = MagicMock()
            mock_module_info1.name = "mock_converter_module1"
            mock_module_info1.ispkg = False
            
            mock_module_info2 = MagicMock()
            mock_module_info2.name = "mock_converter_module2"
            mock_module_info2.ispkg = False
            
            # iter_modules should yield tuples (importer, name, ispkg) or ModuleInfo objects
            # Let's use ModuleInfo for more accurate mocking
            from pkgutil import ModuleInfo
            # Simplify to one mock module to debug count issues
            mock_importer_obj = MagicMock()
            mock_iter_modules.return_value = [
                ModuleInfo(module_finder=mock_importer_obj, name="single_mock_module", ispkg=False),
            ]

            # Mock importlib.import_module to prevent actual imports and track calls
            with patch('importlib.import_module') as mock_import_lib_module:
                # First call: iter_modules and import_module should be called
                initial_import_count = BaseDateConverter.import_converters()
                assert initial_import_count == 1 # Expect 1 due to one mock module
                assert mock_iter_modules.call_count == 1
                # import_module is called for "single_mock_module"
                assert mock_import_lib_module.call_count == 1 

                # Second call: due to @cache, iter_modules and import_module should NOT be called again
                cached_import_count = BaseDateConverter.import_converters()
                assert cached_import_count == initial_import_count 
                assert mock_iter_modules.call_count == 1 
                assert mock_import_lib_module.call_count == 1
        
        # Clear cache again for subsequent tests
        BaseDateConverter.import_converters.cache_clear()

        # Verify that known converter modules were loaded into sys.modules (original check, needs actual imports)
        # This part needs to be outside the mocks that prevent actual imports.
        # We can do a separate small test for the side effect of loading.
        BaseDateConverter.import_converters() # Actual call to load modules
        # This is an effect of a successful import_converters run
        assert 'undate.converters.edtf' in sys.modules
        assert 'undate.converters.iso8601' in sys.modules
        assert 'undate.converters.calendars.gregorian' in sys.modules
        assert 'undate.converters.calendars.hebrew' in sys.modules


    def test_actual_module_loading_effect(self):
        # This test ensures that import_converters actually loads modules.
        # It's a simplified version of the side-effect check from the previous test.
        BaseDateConverter.import_converters.cache_clear()
        
        # Check a module that is part of the standard converters, e.g., edtf
        # Ensure it's not in sys.modules if we could guarantee a fresh Python session (hard in tests)
        # Instead, we rely on import_converters to load it if it's not there,
        # and then check its presence.
        
        # Force unload if it was loaded by a previous test run in the same session, for a cleaner check.
        # This is a bit heavy-handed for a test but helps ensure we're testing the loading.
        if 'undate.converters.edtf' in sys.modules:
            del sys.modules['undate.converters.edtf']
        if 'undate.converters.iso8601' in sys.modules:
            del sys.modules['undate.converters.iso8601']

        import_count = BaseDateConverter.import_converters()
        assert import_count > 0 # It should find and try to load actual modules

        assert 'undate.converters.edtf' in sys.modules
        assert 'undate.converters.iso8601' in sys.modules
        BaseDateConverter.import_converters.cache_clear() # clean up for other tests


    def test_subclasses_discovery(self):
        # Ensure converters are imported. Cache clear ensures import_converters runs.
        BaseDateConverter.import_converters.cache_clear()
        BaseDateConverter.import_converters() # This populates the class registry

        discovered_converter_types = BaseDateConverter.subclasses()
        
        # 1. Test for direct dummy subclass defined in this test file
        assert DirectDummyConverter in discovered_converter_types
        # 2. Test for "nested" dummy subclass (also defined in this test file)
        assert NestedDummyConverterInTestModule in discovered_converter_types
        
        # 3. Check for known actual direct subclasses of BaseDateConverter
        assert EDTFDateConverter in discovered_converter_types # Corrected class name
        assert ISO8601DateFormat in discovered_converter_types # Corrected class name
        
        # 3. Check for known actual calendar converter subclasses (which are subclasses of BaseCalendarConverter)
        assert GregorianDateConverter in discovered_converter_types
        assert HebrewDateConverter in discovered_converter_types
        assert DummyCalendarSubclassConverter in discovered_converter_types # Our dummy calendar subclass

        # 4. Check that BaseCalendarConverter itself is NOT included
        assert BaseCalendarConverter not in discovered_converter_types

    def test_available_converters_map(self):
        # Ensure converters are imported. Cache clear ensures import_converters runs.
        BaseDateConverter.import_converters.cache_clear()
        BaseDateConverter.import_converters()

        available = BaseDateConverter.available_converters()
        
        # Check for dummy converters
        assert DirectDummyConverter.name in available
        assert available[DirectDummyConverter.name] == DirectDummyConverter
        assert NestedDummyConverterInTestModule.name in available
        assert available[NestedDummyConverterInTestModule.name] == NestedDummyConverterInTestModule
        
        # Check for actual direct subclasses
        assert EDTFDateConverter.name in available, f"{EDTFDateConverter.name} not in available"
        retrieved_edtf = available[EDTFDateConverter.name]
        assert retrieved_edtf.__name__ == EDTFDateConverter.__name__
        assert retrieved_edtf.__module__ == EDTFDateConverter.__module__
        
        # Detailed check for ISO8601DateFormat
        assert ISO8601DateFormat.name in available, \
            f"{ISO8601DateFormat.name} key missing from available converters"
        converter_from_dict_iso = available.get(ISO8601DateFormat.name)
        assert converter_from_dict_iso is not None, \
            f"{ISO8601DateFormat.name} not found in available converters using .get()"
        # Compare by name and module to avoid issues with object identity after reloads
        assert converter_from_dict_iso.__name__ == ISO8601DateFormat.__name__, \
            f"Name mismatch for {ISO8601DateFormat.name}"
        assert converter_from_dict_iso.__module__ == ISO8601DateFormat.__module__, \
            f"Module mismatch for {ISO8601DateFormat.name}"
        
        # Check for calendar converter subclasses
        # For these, direct object comparison should be fine if their modules are not reloaded by other tests.
        # However, to be safe, could also convert to name/module comparison.
        assert GregorianDateConverter.name in available
        retrieved_gregorian = available[GregorianDateConverter.name]
        assert retrieved_gregorian == GregorianDateConverter # Assuming Gregorian not reloaded by test_actual_module_loading_effect
        
        assert HebrewDateConverter.name in available
        retrieved_hebrew = available[HebrewDateConverter.name]
        assert retrieved_hebrew == HebrewDateConverter # Assuming Hebrew not reloaded

        assert DummyCalendarSubclassConverter.name in available
        assert available[DummyCalendarSubclassConverter.name] == DummyCalendarSubclassConverter

        # 4. Check that BaseCalendarConverter is NOT in the available map by its name
        # BaseCalendarConverter does not have a 'name' field, so it would use the class name if it were included.
        assert BaseCalendarConverter.__name__ not in available
        # Also check its default generated name if it had one (it doesn't, but good for robustness)
        # The `name` property of BaseDateConverter generates a name like "Base Calendar Converter"
        # if `cls.name` is not set.
        assert "Base Calendar Converter" not in available


    def test_nested_subclass_discovery_via_dynamic_module_mock(self):
        """
        Tests discovery of subclasses from a dynamically created and imported module.
        This more closely simulates finding converters in other files.
        """
        BaseDateConverter.import_converters.cache_clear()

        # Define module and class names
        dummy_module_name = "temp_dynamic_undate_converter_module"
        dummy_class_name = "DynamicModuleConverter"
        dummy_converter_name_attr = "DynamicModuleTestConverter"

        # Ensure the dummy module is not in sys.modules from a previous failed run
        if dummy_module_name in sys.modules:
            del sys.modules[dummy_module_name]

        # Create dummy module content
        dummy_module_content = f"""
from undate.converters.base import BaseDateConverter

class {dummy_class_name}(BaseDateConverter):
    name = "{dummy_converter_name_attr}"
    def parse(self, value): return "parsed"
    def to_string(self, undate): return "stringified"
"""
        # Create a mock module object
        mock_module = importlib.util.spec_from_loader(dummy_module_name, loader=None)
        if mock_module is None: # Should not happen with a basic name
            pytest.fail("Failed to create module spec")
            
        dynamic_module = importlib.util.module_from_spec(mock_module)
        
        # Execute the class definition in the context of the new module
        exec(dummy_module_content, dynamic_module.__dict__)
        
        # Add the mock module to sys.modules so it can be "imported"
        sys.modules[dummy_module_name] = dynamic_module
        
        # The class we want to find
        DynamicTestConverterClass = getattr(dynamic_module, dummy_class_name)

        # Now, we need to make import_converters "find" this module.
        # We'll mock pkgutil.iter_modules for the 'undate.converters' path.
        # We need to know where 'undate.converters' is.
        import undate.converters
        converters_path = undate.converters.__path__ # This is a list of paths

        # original_iter_modules = importlib.import_module('pkgutil').iter_modules <-- Removed

        def simplified_mock_iter_modules(path=None, prefix=''):
            # We expect import_converters to call iter_modules with the path to undate.converters
            # and prefix 'undate.converters.'
            # This mock is now more focused based on the previous analysis.
            if path == converters_path and prefix == "undate.converters.":
                # Return only our dynamic module as a raw 3-tuple to test unpacking.
                # Name should be the simple module name for import_module.
                mock_importer_for_dynamic = MagicMock()
                return iter([
                    (mock_importer_for_dynamic, dummy_module_name, False) # Yield raw tuple
                ])
            else:
                # If called with other paths/prefixes (it shouldn't be by import_converters' current logic),
                # return an empty iterator to avoid unexpected behavior.
                return iter([])

        with patch('pkgutil.iter_modules', side_effect=simplified_mock_iter_modules):
            # Mock importlib.import_module to return our dynamic module when its name is requested
            original_import_module = importlib.import_module # Save for fallback if needed
            def side_effect_importlib(name, package=None):
                # name will be like "undate.converters.temp_dynamic_undate_converter_module"
                if name == f"undate.converters.{dummy_module_name}":
                    return dynamic_module # Return the already "loaded" module
                # Fallback for any other imports (e.g. if test setup imports something else)
                return original_import_module(name, package)

            with patch('importlib.import_module', side_effect=side_effect_importlib):
                # The actual import_module call within import_converters will be like:
                # importlib.import_module(f"{package_to_scan.__name__}.{module_info.name}")
                # So, we need to handle that specific call.

                # Let original import_module handle other imports, but return our module for the dummy one
                def side_effect_import_module(name, package=None):
                    if name == f"undate.converters.{dummy_module_name}":
                         return dynamic_module
                    # For other modules, like the actual converters, we need to let them load
                    # so that __subclasses__ can find them too for a complete list.
                    # However, import_converters itself tries to import them.
                    # The goal here is to ensure our *new* dynamic one is added.
                    # The easiest is to ensure import_converters tries to import it,
                    # and since it's in sys.modules, it will be "found".
                    
                    # The issue: import_converters itself calls import_module.
                    # If we mock import_module completely, real converters won't load.
                    # Solution: Let import_module work, but ensure our module is in sys.modules.
                    # The `patch('pkgutil.iter_modules', ...)` makes import_converters *try* to import it.
                    # Since `dummy_module_name` is in `sys.modules`, it will be successfully "imported".
                    return importlib.import_module(name, package)


                # Let's use the actual import_module, relying on sys.modules and mocked iter_modules
                BaseDateConverter.import_converters.cache_clear()
                import_count = BaseDateConverter.import_converters()
                assert import_count > 0 # Should have "imported" our module + others

        # Check if the dynamically created class is now part of the subclasses
        subclasses_after_dynamic_import = BaseDateConverter.subclasses()
        assert DynamicTestConverterClass in subclasses_after_dynamic_import

        available_after_dynamic_import = BaseDateConverter.available_converters()
        assert dummy_converter_name_attr in available_after_dynamic_import
        assert available_after_dynamic_import[dummy_converter_name_attr] == DynamicTestConverterClass

        # Cleanup: remove the dummy module from sys.modules
        if dummy_module_name in sys.modules:
            del sys.modules[dummy_module_name]
        
        # Clear cache again to avoid interference with other tests
        BaseDateConverter.import_converters.cache_clear()
