import pytest
import os
import sys

if __name__ == "__main__":
    # Set environment variable to use template-based generation instead of transformers
    os.environ["USE_TRANSFORMERS"] = "False"
    
    # Run pytest with verbosity
    sys.exit(pytest.main(["-v", "tests/"])) 