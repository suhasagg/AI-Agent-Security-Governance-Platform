up:
	docker compose up --build
down:
	docker compose down -v
python-test:
	cd python-governance && pytest -q
java-test:
	cd java-tools && mvn test
