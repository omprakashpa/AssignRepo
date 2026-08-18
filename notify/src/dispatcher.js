const axios = require('axios');
const config = require('./config');

async function dispatch(webhook, payload) {
  for (let attempt = 1; attempt <= config.RETRY_ATTEMPTS; attempt++) {
    try {
      const headers = {
        'Content-Type': 'application/json',
      };

      if (config.SERVICE_KEY) {
        headers['X-Service-Key'] = config.SERVICE_KEY;
      }

      await axios.post(webhook.url, payload, {
        timeout: config.TIMEOUT_MS,
        headers,
      });

      return { webhookId: webhook.id, success: true, attempt };
    } catch (err) {
      if (attempt === config.RETRY_ATTEMPTS) {
        return {
          webhookId: webhook.id,
          success: false,
          error: err.message,
          attempt,
        };
      }
    }
  }
}

module.exports = { dispatch };
