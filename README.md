# py-iMessage API

This is a simple Python API to interact with iMessages on macOS.

We hope this API can help you connect your iMessage with Large Language Models (LLMs). By integrating this API with an LLM, you can create powerful applications such as automated responses, message summarization, sentiment analysis, or even a chatbot that can interact through iMessage. This combination opens up possibilities for more intelligent and context-aware messaging experiences, leveraging the capabilities of both iMessage and advanced AI models.

## Installation

To install py-imessage-api, follow these steps:
```bash
# 1. Clone the repository:
git clone https://github.com/yourusername/py-imessage-api.git
# 2. Navigate to the cloned directory:
cd py-imessage-api
# 3. Install the package locally:
pip install -e .
```

This will install the package in editable mode, allowing you to make changes to the source code if needed.

## Features

- Send and receive text messages
- Send image and file attachments
- Retrieve chat history
- Support for individual and group chats

## Usage

Here's a basic example of how to use the IMessageAPI:

```python
from py_imessage_api import IMessageAPI

# Initialize the API with the path to your iMessage database
api = IMessageAPI("/Users/YourUsername/Library/Messages/chat.db")

# Get all recipients
recipients = api.get_all_recipients()

# Send a text message
api.send_message("Hello, world!", "+1234567890")

# Send a file
api.send_message("/Users/YourUsername/Pictures/image.jpg", "+1234567890", message_type="file")

# Get the last 10 messages from a chat
messages = api.get_messages("+1234567890", n=10)
```

## Note
1. All files must be in the /Users/MyUserName/Pictures folder. See [this link](https://apple.stackexchange.com/questions/429586/cannot-send-image-files-from-messages-using-applescript-on-monterey) for more information.
2. For sending voice messages, you need to generate a corresponding .caf file and send it as a file attachment. However, due to some unknown issues, the recipient may not be able to directly receive and play the voice message. This feature is still under investigation and improvement.

## Requirements
macOS (tested on macOS Monterey)
Python 3.6+
pandas

## License
This project is licensed under the MIT License.

## References
1. [imessage_tools](https://github.com/my-other-github-account/imessage_tools)
2. [iMessage-Attachment-Extractor](https://github.com/adama11/iMessage-Attachment-Extractor)
3. [AppleScriptLangGuide](https://developer.apple.com/library/archive/documentation/AppleScript/Conceptual/AppleScriptLangGuide/introduction/ASLR_intro.html)