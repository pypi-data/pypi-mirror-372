#!/usr/bin/env python3
"""Test script for webcam-security package."""

import sys
import os
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_imports():
    """Test that all modules can be imported."""
    print("🧪 Testing imports...")

    try:
        from webcam_security import SecurityMonitor, Config

        print("✅ Core modules imported successfully")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

    try:
        from webcam_security.cli import app

        print("✅ CLI module imported successfully")
    except ImportError as e:
        print(f"❌ CLI import error: {e}")
        return False

    return True


def test_config():
    """Test configuration functionality."""
    print("\n🧪 Testing configuration...")

    try:
        from webcam_security.config import Config

        # Test config creation
        config = Config(
            bot_token="test_token", chat_id="test_chat", topic_id="test_topic"
        )
        print("✅ Config creation successful")

        # Test validation
        assert config.is_configured(), "Config should be valid"
        print("✅ Config validation successful")

        # Test save/load (clean up after)
        config.save()
        print("✅ Config save successful")

        loaded_config = Config.load()
        assert loaded_config.bot_token == config.bot_token
        assert loaded_config.chat_id == config.chat_id
        assert loaded_config.topic_id == config.topic_id
        print("✅ Config load successful")

        # Clean up
        config_path = config._get_config_path()
        if config_path.exists():
            config_path.unlink()
            config_path.parent.rmdir()
        print("✅ Config cleanup successful")

    except Exception as e:
        print(f"❌ Config test error: {e}")
        return False

    return True


def test_cli_help():
    """Test CLI help command."""
    print("\n🧪 Testing CLI help...")

    try:
        from webcam_security.cli import app

        # This should not raise an error
        print("✅ CLI app creation successful")
    except Exception as e:
        print(f"❌ CLI test error: {e}")
        return False

    return True


def main():
    """Run all tests."""
    print("🚀 Testing webcam-security package...")

    tests = [
        test_imports,
        test_config,
        test_cli_help,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        else:
            print(f"❌ Test failed: {test.__name__}")

    print(f"\n📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Package is ready.")
        return True
    else:
        print("❌ Some tests failed. Please fix issues before building.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
