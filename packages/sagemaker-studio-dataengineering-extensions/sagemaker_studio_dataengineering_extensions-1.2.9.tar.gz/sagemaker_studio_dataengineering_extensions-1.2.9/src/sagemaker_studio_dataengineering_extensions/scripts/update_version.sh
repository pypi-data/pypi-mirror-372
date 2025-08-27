#!/bin/bash

# File path
INIT_FILE="src/sagemaker_studio_dataengineering_extensions/__init__.py"

# Check if the --force parameter is provided
FORCE_UPDATE_VERSION=false
if [ "$1" == "--force" ]; then
    FORCE_UPDATE_VERSION=true
fi

# Get current datetime in YYYYMMDDhhmmss format
CURRENT_DATETIME=$(date +"%Y%m%d%H%M%S")

# Extract current version from __init__.py
CURRENT_VERSION=$(grep "__version__" "$INIT_FILE" | cut -d'"' -f2)

# Function to generate new build number
generate_build_number() {
    local datetime=$1
    local current_datetime=$2
    
    if [ "$datetime" = "$current_datetime" ]; then
        # Same second, increment by 1
        echo "$((current_datetime + 1))"
    else
        # New time, use current datetime
        echo "$CURRENT_DATETIME"
    fi
}

# Check if current version has a build number
if [[ $CURRENT_VERSION =~ ^([0-9]+\.[0-9]+\.[0-9]+)\.([0-9]{14})$ ]]; then
    # Version with build number - always update
    BASE_VERSION="${BASH_REMATCH[1]}"
    BUILD_DATETIME="${BASH_REMATCH[2]}"
    
    NEW_BUILD=$(generate_build_number "$BUILD_DATETIME" "$CURRENT_DATETIME")
    NEW_VERSION="${BASE_VERSION}.${NEW_BUILD}"
else
    # Simple version number (like 1.0.5)
    if [ "$FORCE_UPDATE_VERSION" = true ]; then
        # Only update if --force flag is provided
        NEW_VERSION="${CURRENT_VERSION}.${CURRENT_DATETIME}"
    else
        # Keep current version
        NEW_VERSION="$CURRENT_VERSION"
    fi
fi

# Update __init__.py with new version
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' "s/__version__=\".*\"/__version__=\"$NEW_VERSION\"/" "$INIT_FILE"
else
    # Linux and others
    sed -i "s/__version__=\".*\"/__version__=\"$NEW_VERSION\"/" "$INIT_FILE"
fi

echo "Version updated from $CURRENT_VERSION to $NEW_VERSION in $INIT_FILE"

# Optional: Display the updated line
# grep "__version__" "$INIT_FILE"