### Simple aysnc web app with PostgresSQL and FastAPI 

- postgres database
- FastAPI CRUD operations support

### Build the docker containers and run the app
```
docker-compose up -d --build
```

### Access the app using following urls
- http://localhost:8000/docs#/ <= Swagger UI
- http://localhost:8000  <= api calls

## For Development and debugging the application

### Install
```
docker-compose up -d
```

### before commit/PR push, perform code formatting using Black. Install the pre-commit hook:
```.bash
for i in $(find ${PWD}/src -type f -name '*.py'); do black -S -l 100 $i; done 
```
- Now do the code changes as necessary and when you perform `git commit`, black would auto-format changed files and you can review and git add those files for commit

### TODO
- [ ] add auth support
- [ ] expand db-schema with more columns
- [ ] perform various SQL queries using jinja or something better SQL templates
- [ ] more REST APIs definition
- [ ] introduce GraphQL as well
- [ ] test performance benchmark against similar CRUD synchronous webapp
- [x] add basic sanity tests

### References
- https://testdriven.io/blog/fastapi-crud/#project-setup
