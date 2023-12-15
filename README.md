# library-service
## 👩‍💻 _Setup Telegram Bot_ 
<details>
  <summary>Click me</summary>

  ### 🧠 Create bot in Bot Father  
- Start chat with [Bot Father](https://t.me/BotFather)
- ```/newbot``` - to create new bot
- Send bot's name
- ```/setprivacy``` - change to **Disable**
- Copy and save **API Key**,  **Bot Link**

### 👯 Create chat
- You need to create channel
- Than, you should add your bot using  **Bot Link**

### 🤔 Find chat id
- Write some message in chat
- Go to ```https://api.telegram.org/bot<TOKEN>/getUpdates```.
- In ```<TOKEN>``` place **API Key**
- You will get response:
```json
  "chat": {
    "id": -4017738106,
    "title": "Order Tickets",
    "type": "group",
    "all_members_are_administrators": true
   },
  ``` 
- Save your **Chat ID**
- Write all saved information inside [.env](.env) file like that:
```
TELEGRAM_API_KEY=6503311767:AAEkcCdnc3MewRnLe53YZgnDSdqdq1pq7mE
TELEGRAM_CHAT_ID=-4017738106
  ``` 
### 📫 Image configure
You can change images that bot sends in [telegram_notifications.py](notifications%2Ftelegram_notifications.py)
```python
BORROW_PHOTO = ("link-to-image")
PAYMENT_PHOTO = ("link-to-image")
```
</details>