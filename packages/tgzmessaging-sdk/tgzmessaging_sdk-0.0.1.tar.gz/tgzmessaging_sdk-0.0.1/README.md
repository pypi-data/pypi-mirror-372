# WhatsApp Services

This branch contains core services required for managing and handling WhatsApp Business messaging workflows.

## 📦 Included Services

### 1. WhatsApp Template Service
Handles operations related to WhatsApp message templates, including:
- Template creation and validation
- Support for **NAMED** and **TEXT** parameter formats
- Category and language management
- Template structure generation for API submission
- Syncing with Meta's WhatsApp Business API (future scope)

### 2. WhatsApp Webhook Service
Manages incoming events from WhatsApp Business Webhooks:
- Message delivery reports (sent, delivered, read)
- User replies and inbound messages
- Message status updates
- Signature validation (optional for security)

## 🛠 Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run the services individually
python template_service/main.py
python webhook_service/main.py
