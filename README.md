### Simple aysnc web app with PostgresSQL and FastAPI 

- postgres database
- FastAPI CRUD operations support

### Build the docker containers and run the app
```
docker-compose up -d --build
```

### Access the app using following urls
- http://localhost:8002/docs#/ <= Swagger UI
- http://localhost:8002  <= api calls

## For Development and debugging the application

### Install Poetry
```.bash
python3 -m pip install --pre poetry
```

### install and run aysncweb
```.env
git clone https://github.com/abakhru/aysncweb.git && cd aysncweb
poetry shell && poetry install && poetry show --tree
```

### before commit/PR push, perform code formatting using Black. Install the pre-commit hook:
```
brew install pre-commit
cd ~/src/aysncweb; pre-commit install
# black --config ./pyproject.toml .  <= only needed if you need to format whole project files
```
- Now do the code changes as necessary and when you perform `git commit`, black would auto-format changed files and you can review and git add those files for commit
 
### TODO
- [] add auth support
- [] expand db-schema with more columns
- [] perform various SQL queries using jinja or something better SQL templates
- [] more REST apis definition
- [] introduce GraphQL as well
- [] test performance benchmark agains similar CRUD synchornus webapp