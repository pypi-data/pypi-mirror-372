# Ask Sage Python Client v1.4

This is the official Python client for the Ask Sage API. It allows you to interact with the Ask Sage service, providing a simple and pythonic way to make requests to the service.

Check Ask Sage API documentation here: https://docs.asksage.ai

## Installation

You can install the Ask Sage Python client via pip:

pip install asksageclient

## Usage

First, import the client:

from asksageclient import AskSageClient

Then, instantiate the client:

client = AskSageClient('your_email_here', 'your_api_key_here')
Warning: Do not store credentials in code, use environment variables/secrets instead

Now, you can use the client to interact with the Ask Sage service. For example, to interact with the main endpoint:

response = client.query(message='Who is Nic Chaillan?')

print(response)

## Endpoints

The client provides methods for all the Ask Sage API endpoints:

- `get_models`
- `add_dataset`
- `delete_dataset`
- `assign_dataset`
- `get_user_logs`
- `get_user_logins`
- `query`
- `query_plugin`
- `execute_plugin`
- `follow_up_questions`
- `tokenizer`
- `get_personas`
- `get_datasets`
- `get_plugins`
- `count_monthly_tokens`
- `count_monthly_teach_tokens`
- `train`
- `train_with_file`
- `file`

Each method corresponds to an endpoint of the Ask Sage API. The `content` parameter should be a dictionary containing the data you want to send in the request body.

## Error Handling

The client includes basic error handling. If a request fails, it will print an error message and return `None`.

## Contributing

Contributions are welcome! Please submit a pull request or create an issue to contribute to this project.

## License

See the LICENSE file for details.
