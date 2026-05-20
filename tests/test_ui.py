import unittest
import sys
import os
import pandas as pd

# Add root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestUIImports(unittest.TestCase):
    def test_imports(self):
        """Ensure core UI modules and app can be imported without errors."""
        import ui.overview_tab
        import ui.skill_tab
        import ui.manpower_tab
        import ui.audit_tab
        import ui.backlog_tab
        
        # Assert penetration tab is removed
        with self.assertRaises(ImportError):
            import ui.penetration_tab

    def test_backlog_logic(self):
        """Mock test to ensure backlog tab is structured correctly."""
        from ui.backlog_tab import render_backlog
        self.assertTrue(callable(render_backlog))

if __name__ == '__main__':
    unittest.main()

