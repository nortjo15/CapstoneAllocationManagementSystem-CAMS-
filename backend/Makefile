# Makefile 
CONTAINER_NAME_B = i2a-project-allocation-backend-1
CONTAINER_NAME_F = i2a-project-allocation-frontend-1
POSTGRES_HOST = dpg-d3p0f7umcj7s739louvg-a.singapore-postgres.render.com
POSTGRES_USER = cams_user
POSTGRES_DB = i2a_postgres_database

.PHONY: help 
help: 
	@echo "Common commands:"
	@echo " make testdata	- Generate test data"
	@echo " make migrate	- Run Django migrations"
	@echo " make shell	- Open Django shell inside container"
	@echo " make db	- Connect to psql inside container"
	@echo " make rebuild	- Rebuild container"
	@echo " make bash	- Connect to bash inside container"

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
	docker exec -e PGPASSWORD=oxh68Dm0EPYorASbiinv12pgRiopLtfm -it $(CONTAINER_NAME_B) psql \
	  -h $(POSTGRES_HOST) \
	  -U $(POSTGRES_USER) \
	  -d $(POSTGRES_DB)

.PHONY: rebuild 
rebuild: 
	docker-compose down
	docker-compose build --no-cache 
	docker-compose up -d 

.PHONY: bash
bash:
	docker exec -it $(CONTAINER_NAME_B) bash
