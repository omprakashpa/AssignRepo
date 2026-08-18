const serviceKey = process.env.SERVICE_KEY;

module.exports = {
  PORT: process.env.PORT || 3001,
  PYTHON_API_URL: process.env.PYTHON_API_URL || 'http://localhost:8000',
  // Secret is injected by the runtime; it is never stored in source control.
  SERVICE_KEY: serviceKey || null,
  RETRY_ATTEMPTS: 3,
  TIMEOUT_MS: 5000,
};
