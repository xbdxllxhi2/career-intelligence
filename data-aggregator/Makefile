
.PHONY: init start stop logs restart reset user install-requirements

init:
	docker compose run --rm airflow-webserver airflow db init

user:
	docker compose run --rm airflow-webserver airflow users create \
		--username admin \
		--password admin \
		--firstname Abdellahi \
		--lastname Abdellahi \
		--role Admin \
		--email admin@example.com

install-requirements:
	docker compose exec --user airflow airflow-webserver bash -c "pip install -r /requirements.txt"
	docker compose exec --user airflow airflow-scheduler bash -c "pip install -r /requirements.txt"

start:
	docker compose up -d

stop:
	docker compose down

restart:
	docker compose down
	docker compose up -d

logs:
	docker compose logs -f

reset:
	docker compose down --volumes --remove-orphans
	rm -rf logs/*
	rm -rf dags/__pycache__/
