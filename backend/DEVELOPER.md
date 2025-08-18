## Generating Test Data 
To generate dummy students, projects and preferences for testing, run:
`make testdata`

Optional: 
- `make testdata ARGS="--path \path\to\file""`
- `make testdata ARGS="--memberpref-path \path\to\file"`

- Default command Uses CSV files stored in default path: /backend/admin_app/fixtures 
- To specify different files, add arguments: 
    - '--path' : CSV for Student Data
    - '--project-path' : CSV for Project Data
    - '--memberpref-path' : CSV for GroupPreference Data
    - '--projectpref-path' : CSV for ProjectPreference Data  
- Ensure files are in the **same structure** as default files 
- To clear test data, add '--reset' flag

## All make commands: 
`make help`
`make testdata` 
`make migrate` (Runs Django migrations)
`make shell` (Opens Django shell inside container)
`make db` (Connects to psql database inside container)
`make rebuild` (Rebuilds & starts docker container)
`make bash` (Bash inside container)