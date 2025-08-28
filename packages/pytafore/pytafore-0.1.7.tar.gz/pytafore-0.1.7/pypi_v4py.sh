#!/bin/bash
pip install hatch wheel twine

# Build the package
hatch build

# Upload to pypi
twine upload dist/*