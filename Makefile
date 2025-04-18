run-auth:
	cd data/2-microservice-flow/flawless/auth_service && \
	FLASK_APP=app.py FLASK_ENV=development poetry run flask run --port=5001

run-profile:
	cd data/2-microservice-flow/flawless/profile_service && \
	FLASK_APP=app.py FLASK_ENV=development poetry run flask run --port=5002
