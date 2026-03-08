# API

The API is authenticated and project-scoped. Use the same logged-in session you use in the web application; unauthenticated requests are rejected.

The examples below assume you already have a valid authenticated session cookie available in `cookies.txt`.

Notes:

- non-admin users can only access projects they own or belong to
- non-admin users can only mutate their own runs
- file uploads require the pipeline UUID (`pid`)
- most read endpoints use project and pipeline slugs

## `/api/projects`

Returns the projects visible to the authenticated user.

```bash
curl -b cookies.txt -X POST https://example.com/api/projects
```

Example response:

```json
[
  {
    "pk": 1,
    "name": "LSARP",
    "description": "Large-scale proteomics project",
    "slug": "lsarp"
  }
]
```

## `/api/pipelines`

Returns pipelines in a project visible to the authenticated user.

```bash
curl -b cookies.txt \
  -H 'Content-Type: application/json' \
  -d '{"project":"lsarp"}' \
  https://example.com/api/pipelines
```

## `/api/upload/raw`

Uploads a new RAW file to an existing pipeline and creates a corresponding run.

Required form fields:

- `pid`: pipeline UUID
- `orig_file`: uploaded `.raw` file

```bash
curl -b cookies.txt \
  -F 'pid=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx' \
  -F 'orig_file=@/path/to/sample.raw' \
  https://example.com/api/upload/raw
```

Behavior notes:

- the pipeline must belong to a project the current user can access
- uploads to the seeded demo pipeline are blocked in the web UI; use a normal pipeline for new runs
- repeated uploads with the same displayed filename still create independent runs

## `/api/qc-data`

Returns QC data for a pipeline as a JSON object of column-to-list mappings.

Common request fields:

- `project`: project slug
- `pipeline`: pipeline slug
- `data_range`: number of most recent runs to include
- `columns`: optional list of columns to return

```bash
curl -b cookies.txt \
  -H 'Content-Type: application/json' \
  -d '{"project":"lsarp","pipeline":"sa-tmt11","data_range":30}' \
  https://example.com/api/qc-data
```

The response can include RawTools-derived columns, MaxQuant summary fields, and computed TMT metrics such as:

- `TMT<n>_missing_values`
- `TMT<n>_peptide_count`
- `TMT<n>_protein_group_count`

## `/api/protein-names`

Returns protein-group identifiers, FASTA headers, mean scores, and mean intensities across the selected run set.

Request fields:

- `project`
- `pipeline`
- `data_range`
- `raw_files`: optional list of displayed raw-file names
- `remove_contaminants`: boolean
- `remove_reversed_sequences`: boolean

```bash
curl -b cookies.txt \
  -H 'Content-Type: application/json' \
  -d '{"project":"lsarp","pipeline":"sa-tmt11","data_range":30,"raw_files":[],"remove_contaminants":true,"remove_reversed_sequences":true}' \
  https://example.com/api/protein-names
```

## `/api/protein-groups`

Returns protein-group level data for selected proteins and runs.

Request fields:

- `project`
- `pipeline`
- `data_range`
- `raw_files`: optional list of displayed raw-file names
- `protein_names`: required list of protein-group identifiers
- `columns`: requested columns; include `"Reporter intensity corrected"` to expand to all detected reporter-intensity columns

```bash
curl -b cookies.txt \
  -H 'Content-Type: application/json' \
  -d '{"project":"lsarp","pipeline":"sa-tmt11","data_range":30,"protein_names":["QC1|Peptide1"],"columns":["Reporter intensity corrected"]}' \
  https://example.com/api/protein-groups
```

## `/api/rawfile`

Updates run state for selected files.

Supported actions:

- `flag`
- `unflag`
- `accept`
- `reject`

Selection fields:

- `project`
- `pipeline`
- one of `run_keys`, `raw_file_ids`, or legacy `raw_files`

`run_keys` is the safest selector because it matches the display key used in the UI and disambiguates duplicate filenames.

```bash
curl -b cookies.txt \
  -H 'Content-Type: application/json' \
  -d '{"project":"lsarp","pipeline":"sa-tmt11","action":"accept","run_keys":["abc123_sample.raw"]}' \
  https://example.com/api/rawfile
```

## `/api/flag/create` and `/api/flag/delete`

These endpoints provide explicit flag toggles and use the same selection rules as `/api/rawfile`.

```bash
curl -b cookies.txt \
  -X POST \
  -d 'project=lsarp' \
  -d 'pipeline=sa-tmt11' \
  -d 'run_keys=abc123_sample.raw' \
  https://example.com/api/flag/create
```



