# Makefile 
CONTAINER_NAME_B = i2a-project-allocation-backend-1
CONTAINER_NAME_D = i2a-project-allocation-db-1
CONTAINER_NAME_F = i2a-project-allocation-frontend-1

.PHONY: help 
help: 
	@echo "Common commands:"
	@echo " make testdata	- Generate test data"
	@echo " make migrate 	- Run Django migrations"
	@echo " make shell 		- Open Django shell inside container"
	@echo " make db			- Connect to psql inside container"
	@echo " make rebuild	- Rebuild container"

.PHONY: testdata 
testdata:
	docker exec -it $(CONTAINER_NAME_B) python manage.py generate_test_data $(ARGS)

.PHONY: migrate
migrate:
	docker exec -it $(CONTAINER_NAME_B) python manage.py migrate 

.PHONY: shell
shell:
	docker exec -it $(CONTAINER_NAME_B) python manage.py shell

.PHONY: db 
db: 
	docker exec -it $(CONTAINER_NAME_D) psql -U cas_db -d cas_db_user 

.PHONY: rebuild 
rebuild: 
	docker-compose down
	docker-compose build --no-cache 
	docker-compose up -d 