run-auth:
	cd data/2-microservice-flow/flawless/auth_service && \
	FLASK_APP=app.py FLASK_ENV=development poetry run flask run --port=5001

run-profile:
	cd data/2-microservice-flow/flawless/profile_service && \
	FLASK_APP=app.py FLASK_ENV=development poetry run flask run --port=5002

run-auth-flawed:
	cd data/2-microservice-flow/flawed/auth_service && \
	FLASK_APP=app.py FLASK_ENV=development poetry run flask run --port=5001

run-profile-flawed:
	cd data/2-microservice-flow/flawed/profile_service && \
	FLASK_APP=app.py FLASK_ENV=development poetry run flask run --port=5002

run-gc:
	cd data/3-comments-nlp/good_comments && \
	FLASK_APP=email_validator.py FLASK_ENV=development poetry run flask run --port=5003

run-bc:
	cd data/3-comments-nlp/bad_comments && \
	FLASK_APP=email_validator.py FLASK_ENV=development poetry run flask run --port=5004