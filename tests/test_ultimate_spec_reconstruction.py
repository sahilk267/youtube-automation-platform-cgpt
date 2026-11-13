from pathlib import Path
import tempfile
from tools.materialize_ultimate import materialize

def test_ultimate_exact_reconstruction():
    with tempfile.TemporaryDirectory() as d:
        out=Path(d)/"ultimate"
        materialize(out)
        assert (out/"projects/ULTIMATE_DEPENDENCY_RULES.md").is_file()
        assert not (out/"projects/COMBINED_MIGRATION_PLAN.md").exists()
