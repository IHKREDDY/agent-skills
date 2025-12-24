# Code Review Security Checklist

## Input Validation

- [ ] All user inputs are validated and sanitized
- [ ] Input length limits are enforced
- [ ] Special characters are properly escaped
- [ ] File uploads have type and size restrictions
- [ ] JSON/XML parsing is safe from injection attacks

## Authentication & Authorization

- [ ] Authentication is required where needed
- [ ] Authorization checks are performed before operations
- [ ] Passwords are properly hashed (bcrypt, argon2)
- [ ] Session tokens are secure and have expiration
- [ ] Multi-factor authentication is considered for sensitive operations
- [ ] OAuth/JWT tokens are validated properly

## Data Protection

- [ ] Sensitive data is encrypted at rest
- [ ] Sensitive data is encrypted in transit (HTTPS/TLS)
- [ ] API keys and secrets are not hard-coded
- [ ] Environment variables are used for configuration
- [ ] Personally Identifiable Information (PII) is handled properly
- [ ] Database credentials are secured

## SQL & Database

- [ ] Parameterized queries are used (no string concatenation)
- [ ] ORM is used properly without raw SQL injection risks
- [ ] Database permissions follow least privilege principle
- [ ] No sensitive data in database names or column names visible in errors

## Cross-Site Scripting (XSS)

- [ ] User-generated content is properly escaped before display
- [ ] HTML sanitization is applied where needed
- [ ] Content-Security-Policy headers are set
- [ ] Framework auto-escaping is enabled

## Cross-Site Request Forgery (CSRF)

- [ ] CSRF tokens are used for state-changing operations
- [ ] SameSite cookie attribute is set
- [ ] Origin/Referer headers are validated

## API Security

- [ ] Rate limiting is implemented
- [ ] API authentication is required
- [ ] CORS is properly configured
- [ ] API responses don't leak sensitive information
- [ ] Verbose error messages are not exposed to clients

## Dependencies

- [ ] Dependencies are up to date
- [ ] Known vulnerable packages are not used
- [ ] Package lock files are committed
- [ ] Dependencies are from trusted sources

## Error Handling

- [ ] Errors are logged but not exposed to users
- [ ] Stack traces are not shown in production
- [ ] Error messages don't reveal system information
- [ ] Exceptions are caught and handled appropriately

## Logging & Monitoring

- [ ] Security events are logged
- [ ] Logs don't contain sensitive information
- [ ] Failed authentication attempts are logged
- [ ] Suspicious activity is detectable

## File Operations

- [ ] Path traversal attacks are prevented
- [ ] File permissions are appropriate
- [ ] Temporary files are cleaned up
- [ ] File operations have proper access controls

## Command Execution

- [ ] User input is never passed to system commands
- [ ] If shell commands are needed, they are properly sanitized
- [ ] Principle of least privilege for command execution

## Cryptography

- [ ] Strong encryption algorithms are used (AES-256, RSA-2048+)
- [ ] Random number generation is cryptographically secure
- [ ] Encryption keys are properly managed
- [ ] No custom/weak cryptographic implementations

## Session Management

- [ ] Session IDs are random and unpredictable
- [ ] Sessions expire after appropriate timeout
- [ ] Session fixation is prevented
- [ ] Logout properly invalidates sessions

## HTTP Headers

- [ ] Security headers are set (X-Frame-Options, X-Content-Type-Options)
- [ ] HSTS is enabled for HTTPS sites
- [ ] Cache-Control headers prevent sensitive data caching
