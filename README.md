# library-service
## 👩‍💻 _Setup Telegram Bot_ 
#### You must add admin Chat ID and Initialize Chat to take notification to Telegram. 

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

## 🐻 _Setup User Chat ID_ 
#### If User add his Chat ID and Initialize Chat with Bot, he can take notification to Telegram. 
<details>
  <summary>Click me</summary>

  ### 🐦 Initialize Chat with Bot  
- Sent ```/start```  to [Checks and Orders Bot](https://t.me/ChecksOrdersBot)
  
### 🐧 Get Chat ID  
- Sent ```/start```  to [Get My ID Bot](https://t.me/getmyid_bot)
- Copy ```Your user ID: 751285126```

### ☃️ Save Chat ID
- Go to ```/api/user/me/``` 
- Paste Chat id to ```Telegram chat id``` field
- Make sure that you ```Initialized Chat with Bot```
- Select ```Chat initialized``` checkbox
- Make ```PUT``` request
- All must be like here:
![img.png](https://i.ibb.co/WD284Rw/Example.png)


### 🧣 That all !
#### 🎄 Now you will get new notification to your Telegram !

</details>