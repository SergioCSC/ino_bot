# ino_bot

This bot collects messages from chosen channels, deletes "ЭТО СООБЩЕНИЕ РАСПРОСТРАНЕНО ..." text from it and send it to user. My bot is hosted on Amazon AWS Lambda, but you can run it everywhere.

In order to use it, you have to create file token.txt in project folder with single string: your telegram bot token.

See https://t.me/antiebala_bot

### Run on AWS Lambda

My bot is hosted on **Amazon Lambda**. If you want host it there too:

* Create AWS Lambda function
* Use *python 3.9* runtime for it
* Create API gateway trigger in your Lambda and use it as a webhook for telegram bot using such HTTP request:

      https://api.telegram.org/bot*your-bot-token-here*/setWebhook?url=*lambda-trigger-url-here*

* Add *pandas* layer (version 3) to your Lambda function 
* The sole python library which doesn't exists in this layer is *python-telegram-bot* and it must be contained in *libs_for_aws_lambda* folder, so install it to this folder: 
    ```console
    pip install python-telegram-bot --target libs_for_aws_lambda --upgrade --python 3.9 --only-binary=:all:
    ```
    
### Run locally

If you want to run this code locally, you need to install some python libraries (*python-telegram-bot*, *beatifulsoup4*, *requests*):

```console
pip install -r requirements.txt
```

Then run

```console
python tg_api_connector.py
```

