# SuperU - AI Voice Assistant Platform

[![PyPI version](https://img.shields.io/pypi/v/superu.svg)](https://pypi.org/project/superu/)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

SuperU is a powerful Python SDK for creating AI-powered voice assistants that can make automated phone calls, handle customer interactions, and integrate with your existing APIs and tools.

## 🚀 Features

- **AI Voice Assistants**: Create intelligent voice agents with custom personalities
- **Automated Phone Calls**: Make outbound calls with AI assistants
- **Multi-language Support**: Hindi, English (Indian, American, British accents), and more
- **Tool Integration**: Connect your APIs for dynamic data retrieval during calls
- **Call Analytics**: Comprehensive analysis and transcription of all interactions
- **Flexible Configuration**: Support for multiple AI models, transcribers, and voice providers

## 📦 Installation

```bash
pip install superu
```

## 🔑 Getting Started

### 1. Get Your API Key

1. Visit [dev.superu.ai](https://dev.superu.ai/) and sign up
2. Go to your dashboard
3. Copy your API key

### 2. Basic Usage

```python
import superu

# Initialize the client
client = superu.SuperU('your_api_key_here')

# Create a basic assistant
assistant = client.assistants.create_basic(
    name="Customer Service Assistant",
    voice_id="90ipbRoKi4CpHXvKVtl0",  # Anika - Indian English
    first_message="Hello! How can I help you today?",
    system_prompt="You are a helpful customer service representative."
)

# Make a phone call
call = client.calls.create(
    from_='918035737904',  # Your SuperU number
    to_='+919876543210',   # Customer's number
    assistant_id=assistant['id'],
    max_duration_seconds=300
)

print(f"Call initiated: {call['call_uuid']}")
```

## 🎯 Advanced Usage

### Creating an Advanced Assistant

```python
# Advanced assistant with custom configuration
advanced_config = {
    "name": "Sales Assistant",
    "voice": {
        "model": "eleven_flash_v2_5",
        "voiceId": "xnx6sPTtvU635ocDt2j7",  # Chinmay - Indian English Male
        "provider": "11labs",
        "stability": 0.9,
        "similarityBoost": 0.9,
        "useSpeakerBoost": True
    },
    "model": {
        "model": "gpt-4o-mini",
        "provider": "openai",
        "temperature": 0.7,
        "messages": [
            {
                "role": "system",
                "content": "You are a professional sales representative..."
            }
        ]
    },
    "transcriber": {
        "model": "nova-2",
        "language": "en",
        "provider": "deepgram",
        "endpointing": 300
    },
    "firstMessage": "Hi! I'm calling to discuss our latest offers.",
    "endCallMessage": "Thank you for your time. Have a great day!"
}

assistant = client.assistants.create(**advanced_config)
```

### Available Voices

| Voice ID | Language | Gender | Accent | Name |
|----------|----------|---------|---------|------|
| `gHu9GtaHOXcSqFTK06ux` | Hindi | Female | Standard | Anjali - Soothing Hindi Voice |
| `m5qndnI7u4OAdXhH0Mr5` | Hindi | Male | Standard | Krishna - Energetic Hindi Voice |
| `90ipbRoKi4CpHXvKVtl0` | English | Female | Indian | Anika - Customer Care Agent |
| `xnx6sPTtvU635ocDt2j7` | English | Male | Indian | Chinmay - Calm & Energetic |
| `kdmDKE6EkgrWrrykO9Qt` | English | Female | American | Alexandra |
| `XA2bIQ92TabjGbpO2xRr` | English | Male | American | Jerry |
| `MzqUf1HbJ8UmQ0wUsx2p` | English | Female | British | Katie X |
| `qxjGnozOAtD4eqNuXms4` | English | Male | British | John Shaw - Customer Care |

### Creating Custom Tools

Enable your assistant to call your APIs during conversations:

```python
# Create a tool for checking user information
tool = client.tools.create(
    name="check-user-status",
    description="Check if a user exists in our database",
    parameters={
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "description": "User's email address"
            }
        },
        "required": ["email"]
    },
    tool_url="/api/check-user",
    tool_url_domain="https://your-api.com",
    async_=False
)

# Use the tool in your assistant
assistant_config["model"]["toolIds"] = [tool['id']]
```

### Call Analysis

```python
# Get call analysis
call_uuid = call['call_uuid']
analysis = client.calls.analysis(call_uuid)

print(f"Call duration: {analysis['duration']}")
print(f"Transcript: {analysis['transcript']}")
print(f"Sentiment: {analysis['sentiment']}")
```

### Twilio Integration

```python
# Use your own Twilio number
call = client.calls.create_twilio_call(
    phoneNumberId="your_twilio_number_id",
    to_="+919876543210",
    assistant_id=assistant['id']
)

# Analyze Twilio calls
analysis = client.calls.analysis_twilio_call(call['call_uuid'])
```

## 🛠️ Configuration Options

### Transcriber Options

- **Deepgram**: High-quality, fast transcription with multilingual support
- **AssemblyAI**: Advanced transcription with sentiment analysis
- **Azure**: Microsoft's speech-to-text service
- **11Labs**: ElevenLabs transcription service

### AI Models

- **OpenAI**: GPT-4o, GPT-4, GPT-3.5-turbo with customizable temperature and tools
- Support for custom knowledge bases and function calling

### Voice Providers

- **ElevenLabs**: Premium voice synthesis with multiple models and languages
- Customizable stability, similarity boost, and speaker enhancement

## 📊 Use Cases

- **Customer Service**: Automated support calls with intelligent responses
- **Sales Outreach**: Personalized sales calls with lead qualification
- **Appointment Booking**: Automated scheduling and reminders
- **Survey Collection**: Interactive voice surveys with data collection
- **Lead Qualification**: Intelligent lead scoring and follow-up
- **Order Status**: Automated order updates and delivery notifications

## 🔧 API Reference

### Core Methods

```python
# Client initialization
client = superu.SuperU(api_key)

# Assistants
client.assistants.create_basic(**params)
client.assistants.create(**params)

# Calls
client.calls.create(**params)
client.calls.create_twilio_call(**params)
client.calls.analysis(call_uuid)
client.calls.analysis_twilio_call(call_uuid)

# Tools
client.tools.create(**params)
```

### Call Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `from_` | str | Yes | Caller ID (international format) |
| `to_` | str | Yes | Recipient number (international format) |
| `assistant_id` | str | Yes | Assistant ID to handle the call |
| `max_duration_seconds` | int | No | Maximum call duration (default: 180) |
| `first_message_url` | str | No | URL to initial audio message |

## 🤝 Support

- **Documentation**: [dev.superu.ai](https://dev.superu.ai/)
- **Issues**: Report bugs and feature requests on GitHub
- **Email**: Contact support for enterprise solutions

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🚀 Getting Help

```python
# Example: Complete workflow
import superu
import time

# Initialize
client = superu.SuperU('your_api_key')

# Create assistant
assistant = client.assistants.create_basic(
    name="Demo Assistant",
    voice_id="90ipbRoKi4CpHXvKVtl0",
    first_message="Hello! This is a demo call.",
    system_prompt="You are a friendly demo assistant."
)

# Make call
call = client.calls.create(
    from_='your_superu_number',
    to_='+919876543210',
    assistant_id=assistant['id']
)

# Wait for call completion
time.sleep(30)

# Get analysis
analysis = client.calls.analysis(call['call_uuid'])
print("Call completed successfully!")
```

---

**Ready to build intelligent voice applications?** Get started with SuperU today!