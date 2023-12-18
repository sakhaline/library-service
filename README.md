# Library Service API

This is a Django-based RESTful API for managing a library system with book 
borrowings, payments, and notifications. The API supports CRUD operations 
for books, user management, borrowing, payments, and integrates with the 
Stripe payment gateway and Telegram API.

## Table of Contents

- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Setup Telegram Bot](#setup-telegram-bot)
  - [Setup User Chat ID](#setup-user-chat-id)
- [Components](#usage)
  - [Books Service](#books-service)
  - [Users Service](#users-service)
  - [Borrowings Service](#borrowings-service)
  - [Notifications Service (Telegram)](#notifications-service-(telegram))
  - [Payments Service (Stripe)](#payments-service-(stripe))
- [Documentation](#documentation)
- [DB Schema](#db-schema)

## Getting Started

### 🛜 _Prerequisites_

- Python 3.x
- Docker
- Docker Compose

### ⚙️ _Installation_

1. Clone the repository:

   ```bash
   git clone https://github.com/sakhaline/library-service.git
   cd library-service-api
2. You can open project in IDE and configure .env file using .env.sample file 
as an example.
3. Create a virtual environment:
    ```bash
   # On Linux or macOS
    python3 -m venv venv

    # On Windows
    python -m venv venv
4. Activate the virtual environment:
    ````bash
   # On Linux or macOS
    source venv/bin/activate

    # On Windows
    .\venv\Scripts\activate
5. Install dependencies:
    ````bash
   pip install -r requirements.txt
6. Build and run the Docker containers:
    ````bash
    docker-compose up --build
The API will be accessible at http://localhost:8000/.

### 👩‍💻 _Setup Telegram Bot_ 
#### You must add admin Chat ID and Initialize Chat to take notification to Telegram. 

<details>
  <summary>Click me</summary>

  #### 🧠 Create bot in Bot Father  
- Start chat with [Bot Father](https://t.me/BotFather)
- ```/newbot``` - to create new bot
- Send bot's name
- ```/setprivacy``` - change to **Disable**
- Copy and save **API Key**,  **Bot Link**

#### 👯 Create chat
- You need to create channel
- Than, you should add your bot using  **Bot Link**

#### 🤔 Find chat id
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
#### 📫 Image configure
You can change images that bot sends in [telegram_notifications.py](notifications%2Ftelegram_notifications.py)
```python
BORROW_PHOTO = ("link-to-image")
PAYMENT_PHOTO = ("link-to-image")
```
</details>

### 🐻 _Setup User Chat ID_ 
#### If User add his Chat ID and Initialize Chat with Bot, he can take notification to Telegram. 
<details>
  <summary>Click me</summary>

  #### 🐦 Initialize Chat with Bot  
- Sent ```/start```  to [Checks and Orders Bot](https://t.me/ChecksOrdersBot)
  
#### 🐧 Get Chat ID  
- Sent ```/start```  to [Get My ID Bot](https://t.me/getmyid_bot)
- Copy ```Your user ID: 751285126```

#### ☃️ Save Chat ID
- Go to ```/api/user/me/``` 
- Paste Chat id to ```Telegram chat id``` field
- Make sure that you ```Initialized Chat with Bot```
- Select ```Chat initialized``` checkbox
- Make ```PUT``` request
- All must be like here:
![img.png](https://i.ibb.co/WD284Rw/Example.png)


#### 🎄 Now you will get new notification to your Telegram !

</details>

## Components
### 📚 _Books Service_

#### Managing books (CRUD operations)
<details>
  <summary>Description</summary>
The Books Service in the Library API offers complete
CRUD functionality, including the initialization of 
the "books" app, creation of a book model, and 
implementation of serializers and views for 
essential endpoints. 
Additionally, robust permissions are enforced, ensuring 
that only admin users have the authority to create, 
update, and delete books, while all users, 
including those not authenticated, can access a 
comprehensive list of available books. JWT 
token authentication from the users' service 
enhances security and user-specific interactions 
within the Books Service.
</details>

<details>
  <summary>API Endpoints</summary>

- **POST:** `/books/` - Add a new book
- **GET:** `/books/` - Get a list of books
- **GET:** `/books/<id>/` - Get detailed information about a book
- **PUT/PATCH:** `/books/<id>/` - Update book details (including inventory)
- **DELETE:** `/books/<id>/` - Delete a book
</details>

### 👨‍👩‍👧‍👦 _Users Service_
#### Managing authentication & user registration

<details>
  <summary>Description</summary>
The Users Service in the Library API implements full 
CRUD functionality, beginning with the initialization 
of the "users" app. This involves adding a user model 
with email support and integrating JWT (JSON Web Token) 
authentication for enhanced security. The implementation includes 
serializers and views for all endpoints, ensuring a 
seamless and secure user management system.
</details>

<details>
  <summary>API Endpoints</summary>

- **POST:** `/users/` - Register a new user
- **POST:** `/users/token/` - Get JWT tokens
- **POST:** `/users/token/refresh/` - Refresh JWT token
- **GET:** `/users/me/` - Get user's profile information
- **PUT/PATCH:** `/users/me/` - Update user's profile information
</details>

### 🗒 _Borrowings Service_
#### Managing users' borrowings of books

<details>
  <summary>Description</summary>
The Borrowings Service in the Library API provides robust 
functionality for managing book borrowings. It includes 
the initialization of the borrowing app, a model with 
constraints for accurate tracking, and a read serializer 
for detailed book information. The service offers endpoints 
for listing, retrieving details, and creating borrowings, 
with validations for inventory and user permissions. 
Borrowings can be marked as returned, triggering inventory 
updates, and notifications are sent for new borrowings and 
overdue items. Telegram integration enables real-time 
notifications, and a scheduled task checks for daily 
overdue borrowings, providing detailed alerts or a 
notification of no overdue borrowings. This service ensures 
efficient borrowing processes and timely communication with users.
</details>

<details>
  <summary>API Endpoints</summary>

- **POST:** `/borrowings/` - Add a new borrowing (decrement inventory by 1)
- **GET:** `/borrowings/?user_id=...&is_active=...` - Get borrowings by user id and active/inactive status
- **GET:** `/borrowings/<id>/` - Get specific borrowing
- **POST:** `/borrowings/<id>/return/` - Set actual return date (increment inventory by 1)
</details>

### 💬 _Notifications Service (Telegram)_
#### Sending notifications about new borrowing created, borrowings overdue & successful payment

- Notifications are sent asynchronously using Django Celery.
- Interacts with other services to send notifications to library administrators.
- Uses Telegram API, Telegram Chats & Bots.

### 💵 _Payments Service (Stripe)_

<details>
  <summary>Description</summary>
Stripe is a widely used payment processing platform that enables businesses 
and individuals to accept online payments. 
Stripe offers a RESTful API that allows developers to interact with various resources,
such as customers, payments, subscriptions, and more.
Admins Only - Refund money to a user in case of unexpected 
issues. Accessible to users with is_staff = True.
</details>

* Stripe API: https://stripe.com/docs/api

### Bellow we can see how the payment session looks like:
![payment](https://github.com/sakhaline/library-service/assets/61559978/ad279349-31ab-4f3d-b8eb-d44c886cc3fe)

<details>
  <summary>Payment Endpoints</summary>

- **GET:** `/api/payment` - Add a new borrowing (decrement inventory by 1)
- **GET:** `/api/payment/pk/` - Get borrowings by user id and active/inactive status
- **GET:** `/api/payment/pk/success/` - Get specific borrowing
- **GET:** `/api/payment/pk/cancel/` - Set actual return date (increment inventory by 1)
- **GET:** `/api/payment/pk/refund/` - Set actual return date (increment inventory by 1)
</details>

#### You can test how the payment session works using these test card credentials 💳:
* Email: `doe@gmail.com`
* Cardholder name: `Joe Doe` 
* Card Number: `4242 4242 4242 4242`
* Date MM/YY: `11/30` (random feature date)
* CVC: `123`

#### Perform payments for book borrowings through the platform

<details>
  <summary>API Endpoints:</summary>

- **GET:** `/success/` - Check successful Stripe payment
- **GET:** `/cancel/` - Return payment paused message
</details>

_Interacts with Stripe API using the `stripe` package._

## Documentation
The API is documented using the OpenAPI standard.
Access the API documentation by running the server and navigating to http://localhost:8000/api/doc/swagger/ or http://localhost:8000/api/doc/redoc/.

## DB Schema
