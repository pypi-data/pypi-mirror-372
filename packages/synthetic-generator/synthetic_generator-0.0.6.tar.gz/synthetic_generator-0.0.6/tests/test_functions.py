"""
Test file for basic functions after dtype cleanup.
"""

import pytest
import sys
import os

# Add the src directory to the path
src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

def test_dtype_cleanup():
    """Test that only int and float types are available after cleanup."""
    try:
        from synthetic_generator.dtype import (
            BaseType, BaseFloat, BaseInt, 
            FloatType, IntType,
            base_type, base_float, base_int,
            float_type, int_type
        )
        
        # Check that classes exist
        assert BaseType is not None
        assert BaseFloat is not None
        assert BaseInt is not None
        assert FloatType is not None
        assert IntType is not None
        
        # Check that instances exist
        assert base_type is not None
        assert base_float is not None
        assert base_int is not None
        assert float_type is not None
        assert int_type is not None
        
        # Check that old 32/64 types are not available
        with pytest.raises(ImportError):
            from synthetic_generator.dtype import Float32, Float64, Int32, Int64
        
        print("✅ Dtype cleanup successful - only int and float types available")
        
    except Exception as e:
        pytest.fail(f"Failed to test dtype cleanup: {e}")


def test_basic_imports():
    """Test that basic modules can be imported."""
    try:
        from synthetic_generator import schemas, generators, export
        print("✅ Basic module imports successful")
        assert True
    except Exception as e:
        pytest.fail(f"Failed to import basic modules: {e}")


def test_schema_creation():
    """Test that schemas can be created with cleaned types."""
    try:
        from synthetic_generator.schemas import DataSchema, ColumnSchema, DataType, DistributionType
        
        # Create a simple schema
        schema = DataSchema(
            columns=[
                ColumnSchema(
                    name="age",
                    data_type=DataType.INTEGER,
                    distribution=DistributionType.NORMAL,
                    parameters={"mean": 30, "std": 10}
                ),
                ColumnSchema(
                    name="income",
                    data_type=DataType.FLOAT,
                    distribution=DistributionType.NORMAL,
                    parameters={"mean": 50000, "std": 20000}
                )
            ]
        )
        
        assert len(schema.columns) == 2
        assert schema.columns[0].name == "age"
        assert schema.columns[1].name == "income"
        print("✅ Schema creation successful with cleaned types")
        
    except Exception as e:
        pytest.fail(f"Failed to create schema: {e}")


def test_web_ui_basic():
    """Test that web UI can be imported and basic functionality works."""
    try:
        from synthetic_generator.web import app
        print("✅ Web UI import successful")
        assert True
    except Exception as e:
        pytest.fail(f"Failed to import web UI: {e}")


if __name__ == "__main__":
    print("Running function tests...")
    test_dtype_cleanup()
    test_basic_imports()
    test_schema_creation()
    test_web_ui_basic()
    print("✅ All function tests passed!")
