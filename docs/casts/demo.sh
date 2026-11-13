
#!/usr/bin/env bash
set -euo pipefail

API="http://localhost:5000"
DELAY=2

section() {
    printf '\n\033[1;36m# %s\033[0m\n\n' "$1"
    sleep "$DELAY"
}

run() {
    printf '\033[1;32m$ %s\033[0m\n' "$1"
    sleep 0.3
    eval "$1"
    printf '\n'
    sleep "$DELAY"
}

# Run from the repository root, with MTS already started.

clear
section "Metadata Transformation Service (MTS)"
section "1. Check service health"
run "curl -fsS $API/health | jq"

section "2. Discover supported schemas and crosswalks"
run "curl -fsS $API/api/v1/schemas | jq"
run "curl -fsS $API/api/v1/crosswalks | jq"

section "3. Discover available converters and capabilities"
run "curl -fsS $API/api/v1/converters | jq"
run "curl -fsS $API/api/v1/capabilities | jq"

section "4. DataCite XML to Dublin Core XML"
run "curl -fsS $API/api/v1/transform \
-F source_schema=datacite-4.1 \
-F target_schema=oai-dc \
-F file=@examples/inputs/datacite.xml | jq -r '.metadata'"

section "5. DataCite JSON to Dublin Core JSON"
run "curl -fsS $API/api/v1/transform \
-F source_schema=datacite-4.1 \
-F target_schema=oai-dc \
-F input_format=json -F output_format=json \
-F file=@examples/inputs/datacite.json | jq -r '.metadata' | jq"

section "6. DataCite JSON to Dublin Core XML"
run "curl -fsS $API/api/v1/transform \
-F source_schema=datacite-4.1 \
-F target_schema=oai-dc \
-F input_format=json -F output_format=xml \
-F file=@examples/inputs/datacite.json | jq -r '.metadata'"

section "7. Reverse crosswalk: Dublin Core XML to DataCite JSON"
run "curl -fsS $API/api/v1/transform \
-F source_schema=oai-dc \
-F target_schema=datacite-4.1 \
-F input_format=xml -F output_format=json \
-F file=@examples/inputs/dublincore.xml | jq -r '.metadata' | jq"

section "8. Convert JSON to XML without a crosswalk"
run "curl -fsS $API/api/v1/transform \
-F source_schema=oai-dc \
-F target_schema=oai-dc \
-F input_format=json -F output_format=xml \
-F file=@examples/inputs/dublincore.json | jq '{metadata, report}'"

section "9. Inspect the transformation report"
run "curl -fsS $API/api/v1/transform \
-F source_schema=datacite-4.1 \
-F target_schema=oai-dc \
-F input_format=json -F output_format=json \
-F file=@examples/inputs/datacite.json | jq '.report'"

section "10. Invalid schema: demonstrate error handling"
run "curl -sS $API/api/v1/transform \
-F source_schema=unknown \
-F target_schema=oai-dc \
-F file=@examples/inputs/datacite.xml | jq"

section "End of MTS demonstration"
