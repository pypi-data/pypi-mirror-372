# Sentor Python SDK

A Python SDK for interacting with the Sentor ML API for sentiment analysis. This SDK provides a simple and intuitive interface for sentiment analysis operations.

## Features

- 🚀 Python 3.7+ support
- ⚡ Simple and intuitive API
- 🌍 Support for multiple languages
- 📦 Batch processing capabilities
- 🛡️ Comprehensive error handling
- 🔄 Real-time sentiment analysis

## Installation

```bash
pip install sentor-ml
```

### Work like a PRO

1. Go to [Sentor ML API](https://sentor.app/api)
2. Subscribe to the Starter plan
3. Get your API key

## Usage

### Basic Usage

```python
from sentor import SentorClient

# Initialize the client
client = SentorClient('your-api-key')

# Analyze sentiment
input_data = [
    {
      "doc": "In the competitive landscape of consumer electronics, Apple and Samsung continue to lead the market with innovative products and strong brand loyalty. While Apple focuses on a tightly integrated ecosystem with devices like the iPhone, iPad, and Mac, Samsung excels in offering a wide range of options across various price points, especially in its Galaxy smartphone lineup. Both companies push the boundaries of technology, from cutting-edge chipsets to advanced camera systems, often setting industry trends that others follow.",
      "doc_id": "0",
      "entities": [
        "Apple",
        "Samsung",
        "camera"
      ]
    },
    {
      "doc": "Apple's new iPhone is amazing!",
      "doc_id": "1",
      "entities": [
        "Apple",
        "iPhone"
      ]
    },
    {
      "doc": "Samsung's new phone is amazing!",
      "doc_id": "2",
      "entities": [
        "Samsung",
        "phone"
      ]
    }
  ]
result = client.analyze(input_data)
print(result)
```

### Sample Output

```json
{
  "results": [
    {
      "doc_id": "0",
      "predicted_class": 2,
      "predicted_label": "positive",
      "probabilities": {
        "negative": 0.00007679959526285529,
        "neutral": 0.0002924697764683515,
        "positive": 0.9996306896209717
      },
      "details": [
        {
          "sentence_index": 0,
          "sentence_text": "In the competitive landscape of consumer electronics, Apple and Samsung continue to lead the market with innovative products and strong brand loyalty.",
          "predicted_class": 2,
          "predicted_label": "positive",
          "probabilities": {
            "negative": 0.00009389198385179043,
            "neutral": 0.00032428017584607005,
            "positive": 0.9995818734169006
          }
        },
        {
          "sentence_index": 1,
          "sentence_text": "While Apple focuses on a tightly integrated ecosystem with devices like the iPhone, iPad, and Mac, Samsung excels in offering a wide range of options across various price points, especially in its Galaxy smartphone lineup.",
          "predicted_class": 2,
          "predicted_label": "positive",
          "probabilities": {
            "negative": 0.00005746580063714646,
            "neutral": 0.00012963586777914315,
            "positive": 0.99981290102005
          }
        },
        {
          "sentence_index": 2,
          "sentence_text": "Both companies push the boundaries of technology, from cutting-edge chipsets to advanced camera systems, often setting industry trends that others follow.",
          "predicted_class": 2,
          "predicted_label": "positive",
          "probabilities": {
            "negative": 0.00006366783054545522,
            "neutral": 0.00044553453335538507,
            "positive": 0.9994907379150391
          }
        }
      ]
    },
    {
      "doc_id": "1",
      "predicted_class": 2,
      "predicted_label": "positive",
      "probabilities": {
        "negative": 0.00010637375817168504,
        "neutral": 0.0002509312762413174,
        "positive": 0.9996427297592163
      },
      "details": [
        {
          "sentence_index": 0,
          "sentence_text": "Apple's new iPhone is amazing!",
          "predicted_class": 2,
          "predicted_label": "positive",
          "probabilities": {
            "negative": 0.00010637375817168504,
            "neutral": 0.0002509312762413174,
            "positive": 0.9996427297592163
          }
        }
      ]
    },
    {
      "doc_id": "2",
      "predicted_class": 2,
      "predicted_label": "positive",
      "probabilities": {
        "negative": 0.00010637375817168504,
        "neutral": 0.0002509312762413174,
        "positive": 0.9996427297592163
      },
      "details": [
        {
          "sentence_index": 0,
          "sentence_text": "Samsung's new phone is amazing!",
          "predicted_class": 2,
          "predicted_label": "positive",
          "probabilities": {
            "negative": 0.00010637375817168504,
            "neutral": 0.0002509312762413174,
            "positive": 0.9996427297592163
          }
        }
      ]
    }
  ]
}
```

## API Reference

Please refer to the [Sentor ML API Documentation](https://sentor.app/docs) for more details.
You can also try the API in the [Sentor ML API Swagger Playground](https://sentor.app/docs).

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see the [LICENSE](LICENSE) file for details.