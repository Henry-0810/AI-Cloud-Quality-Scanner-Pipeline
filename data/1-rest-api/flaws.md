# Flawed REST API - Known Issues

1. ❌ SQL Injection vulnerability via string interpolation in SQL queries (register, login, delete).
2. ❌ Storing passwords in plaintext instead of hashing them.
3. ❌ No input validation or error handling.
4. ❌ Uses `request.form` instead of `request.get_json()` for API-style POST requests.
5. ❌ No authentication or authorization checks for deleting users.
6. ❌ SQLite connection and cursor are global (not thread-safe).
7. ❌ Missing HTTPS enforcement or secret key for secure sessions.
8. ❌ No response structure (just strings returned).
9. ❌ Lacks use of ORM or schema validation (e.g., SQLAlchemy, Marshmallow).
10. ❌ Debug mode is on without safeguards (not secure for production).
