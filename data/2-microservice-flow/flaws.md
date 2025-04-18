# Benchmark 2 – Microservice Interaction (Flawed Version)

This benchmark contains multiple architectural and security flaws for tool detection.

## 🔴 List of Flaws

1. **Hardcoded Secret Key**  
   Both services use a hardcoded JWT secret in code (`app.config['SECRET_KEY'] = 'hardcoded-secret'`), which is insecure.

2. **No Token Expiration**  
   Tokens do not expire. JWTs issued can be reused indefinitely.

3. **No User Validation in AuthService**  
   The `auth_service` does not validate username/password before issuing a JWT. Any username is accepted.

4. **Token Passed in Query String**  
   The `profile_service` accepts the token via URL query string (`?token=...`), which is insecure (exposed in browser history, logs, etc.).

5. **No Error Handling for JWT Decode**  
   The `profile_service` does not catch exceptions like expired/invalid tokens. A malformed or expired token will crash the app.

6. **No Profile Mapping Based on Authenticated User**  
   Regardless of who logs in, the `profile_service` always returns Alice's profile.

7. **No Inter-service Auth or API Key**  
   No service-to-service authentication is implemented (e.g., no API key between services or firewall).

8. **No Logging or Observability**  
   Neither service logs requests, errors, or authentication attempts.

## 🧪 Purpose

These flaws are designed to test:
- Whether Amazon Q or CodeGuru can detect insecure token handling and poor microservice communication patterns.
- If context-aware understanding (e.g., missing auth flow or shared secrets) is captured.
