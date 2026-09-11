# Destination restoration checkpoint

Restoration ID: `{{restoration_id}}`
Status timestamp: `{{timestamp_with_timezone}}`

## Status

- Source capture: `{{status}}`
- Local package integrity: `{{status}}`
- Destination download: `{{status}}`
- Staged restoration: `{{status}}`
- Application cutover: `{{status}}`
- Runtime loading: `{{status}}`
- Shared-writer cutover: `{{status}}`

## Source and destination

- Source device: `{{source_device}}`
- Destination device: `{{destination_device}}`
- Source state root: `{{source_state_root}}`
- Destination state root: `{{destination_state_root}}`
- Destination staging root: `{{destination_staging_root}}`
- Client versions: `{{client_versions}}`

## Recovery layers

| Layer | Location | Capture cutoff | Integrity | Applied |
| --- | --- | --- | --- | --- |
| Baseline | `{{baseline_location}}` | `{{baseline_cutoff}}` | `{{status}}` | `{{status}}` |
| Delta | `{{delta_location}}` | `{{delta_cutoff}}` | `{{status}}` | `{{status}}` |
| Final checkpoint | `{{checkpoint_location}}` | `{{checkpoint_cutoff}}` | `{{status}}` | `{{status}}` |

## Preserved destination state

`{{destination_backup_and_preservation_notes}}`

## Verification

`{{manifest_database_task_project_and_file_checks}}`

## Exclusions and gaps

`{{credentials_placeholders_missing_files_and_product_boundaries}}`

## Resume safely

`{{next_permitted_action_and_required_user_gate}}`
