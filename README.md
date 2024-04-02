## run
localhost server
```bash
python -m http.server 8080
```

or in Window:
```bash
./run.ps1
```

### inject project data
python .internals/injectHtml.py -c '.internals/project.csv' -t '.internals/template.html' -i 'index.html' -o 'index.html'

## deploy
deploy ignore path:
```
README.md
run.ps1
```
