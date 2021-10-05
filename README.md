# Stripe Assignment
## _Django Stripe microservice_
In this project we will integrate Stripe service into Django using a microservice.
Django comes with an admin dashboard, that will be useful to create users. Also we have created a JWT authentication system to mimic a real world microservice. The token obtain and refresh methods would have been in another microservice in the real world, but we have included them to run the demo.
In order to run the server and make the demo work, first you must fulfill some requirements.

## Requirements
- Install Docker and Docker compose.
-- https://docs.docker.com/engine/install/
-- https://docs.docker.com/compose/install/
- Create an account in Stripe
-- https://dashboard.stripe.com/login.

With this you can start! Let's run the server.

## Running the server
We're assuming you're in the root folder.

1. First you need to make a copy of the file `.env.sample` and rename it `.env`
If you read the environment variable names is straightforward if you want to change them.
In order to make the integration with Stripe we will have to complete some variables later: `STRIPE_API_SECRET`, `STRIPE_BASIC_PRODUCT_PRICE_ID`, `STRIPE_PRO_PRODUCT_PRICE_ID`, `STRIPE_WEBHOOK_SECRET` but it's not necessary now.

2. Run the project in your local machine
```sh
docker-compose up --build
```

And that's it!!! Now you can go to `http://localhost:8000/api/docs/` and if all it's ok, you will see a Swagger page with documentation of the API.

## Creating Stripe products
As we told you before we need some Stripe data in order to make the project work properly.
- Get Stripe secret key in `https://dashboard.stripe.com/test/apikeys`
-- Set the variable `STRIPE_API_SECRET` with the secret key value in `.env` file.
- Create a basic and a pro product in `https://dashboard.stripe.com/test/products`
-- Just add new recurring products with some price and then in the product detail get the price id of the
product. It will be something similar to `price_1JgB7xxxxxxxxxxxxx`.
Set the variables `STRIPE_BASIC_PRODUCT_PRICE_ID` and `STRIPE_PRO_PRODUCT_PRICE_ID` with the prices references.
- To simulate the Stripe webhook behaviour in your local machine, you will need to install the Stripe CLI to redirect the data to your server. Follow the instructions in `https://stripe.com/docs/stripe-cli`
-- Once installed and configured run the client to redirect the events to our local server. You can get the webhook secret from the Stripe CLI output and save it to the variable `STRIPE_WEBHOOK_SECRET` in `.env`. The `STRIPE_WEBHOOK_SECRET` variable is not needed in local, it's just an extra validation for production environments.
```sh
stripe listen --forward-to localhost:8000/api/stripe-webhook/
```

## Usage example
Now we have all the project running and we can do a sample usage demo.
By default an `admin` superuser is created with the password `qweqweqwE1`. With this user you can go to the Django admin dashboard `http://localhost:8000/admin/` to add or remove users.
1. Add a new user from `http://localhost:8000/admin/users/` to subscribe to Stripe.
2. Now you can goto `http://localhost:8000/api/docs/` to start the demo using the Swagger client to make requests.
3. First we need to authenticate, to this we will use the enpoint `api/token/obtain` and click the button `Try it out`
4. Fill the data with the `username` and `password` of the user you created in the Django admin dashboard and click `Execute`.
5. It will return something similar to this:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTYzMzQ0OTIwOCwianRpIjoiMzY0YzQ1NTNmZTg0NGJiM2JlOWQ2NjE2YWZhYzA0MjciLCJpZCI6ImFjOWJjOGE1LWQyMDYtNDg5MC05Mjc1LWQxOTg2ZGI1NjkzNSIsImFwcF9uYW1lIjoiU3RyaXBlIEFzc2lnbm1lbnQifQ.iUvKMwyn3vIz-mYk4Bkw1GaCkyUksXW3lZoug9GlcWo7_dyl25DI9Xi-O5_TqC39mByYbwBiuejpHPeNskZjoYARvvzD6iZ1ZFqUaHjj1i36KQQuygAKnFNTfqOqXbx_Pccugix5SAtyYRb-RZncS_sxUz0jCXobGD__WqHqe97My1ZzGhjfZiBxm_n8TWbZRdkfTV0DxjsGhzvNEdDHkkP80ibqGhQJTgvJLFHnchnDc20GFeHH-jtJlWM5d7WmfDErZbMviVdPGBAMQnRVcTcAB6fI-bsj0YykimuOCFzB-3wBhx-5Ebtpj2q83kbASqT6LvVUu-JKj7y7Lu2YVlJHpkGMjzTdbCC1vRaOLOHl0YGiOwhiRqmxwAVzpROXJFxhcGJbdjuPpcGZRcpJ3cicM_7mA-rWgQvGjl7dNVE3xVAdaPNW4_g3u_6E5NBTP4dfqN2zWi_TzXaEtFlzT44vTB82Xga269MkMGORf-dOVQVIx7F3Nb-ZDXz24VKwK14VuzztEDLFQaMntbzhpsHcVVgOCMrxPs15NspwTi4DjUDfH9R6mcSA-3MDvkcPr17gMgME5IZUndHyWk5mHIh1OFv-YJtXfPN4pZZcO7S5hxl9UF1kZdZAWJ1r7pno08evDOQeRolyw4L82EwY7AHC3ExPsYhuLInf-BQb76Y",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjMzMzYzMTA4LCJqdGkiOiJjNDY0MmE0NzFmNTQ0NmRhYmMxYTY4ZDQzYTQ5MzBmOCIsImlkIjoiYWM5YmM4YTUtZDIwNi00ODkwLTkyNzUtZDE5ODZkYjU2OTM1IiwiYXBwX25hbWUiOiJTdHJpcGUgQXNzaWdubWVudCJ9.AXeQSUtW4YYfCHVlFUgi-4GpyoGmyBXxXDxKaxIwJThd35Z7AtkISvaHmPJkKb8LMUnYr1BeuHO4GqPFNA-adn1tIcO8lmhSYAijolP9FQUlfA_2z19z4PCRD4A0K6DYQK6T_leUn8AiKi68CmkURHyH7lI9ftU6tO8iZ7I-KN6Ix5sk0u4q4AHe30Ekf1K26IdKz66IvyhcXnbeT2zbuiLLn0GgYb4_P3kaECj-cK_84KrUG0J4HSP9XOhcETWnoLSCHG6hgBQrx_ctXxsp0wqr8LW-PgwHFhOai7WgQN9vGdqOGC7DeUbiVi5VYmYy-WhSoUpLBHTLhoBj6Tj9IOiXtYQUvUdJ8HgQtWmrFzJ8phNHy_6GSXln92WjiGFZjpBO201d-2BrZl-7APiEAEGZlPzdgss0npxZevGzw0NklIbtZeESNdZ1u58tgQZ2rg10U7tFW86g-0SbpPHLfD3Ll-ClgG_zzldzOAB1a6ACq5L4R2dNxEfbJljLysxbFL6cVVgN3arERscCL2TPI6dqFR8jPTMGdhJNXHUpgWWqHROcRIZIwWalcTP2kC7jGSSyXRG6HOAXQADcHZ8OGSr4olbsV2tckhjvjX2mfRpJBVmTIREUak9m8IULJVbg3BqQ58v2Qf9bij1mMnWKtftE1v7M4Muv5tkbHRtLaGg"
}
```
6. You need to copy the `access` value. And paste it in the upper `Authorize` button modal window.
7. In the `jwtAuth  (apiKey)` window just add `JWT ACCESS_VALUE` in the value input and click `Authorize` button.
8. Now we can subscribe to Stripe using the endpoint `api/subscriptions/subscribe`. Internally the project has 2 subscription products stored, the `basic_subscription` and the `pro_subscription` products. Use the endpoint and fill the data with something similar to this. And then click the `Execute` button.
```json
{
  "subscription_product": "basic_subscription",
  "card_number": "4242424242424242",
  "card_expiration_month": 12,
  "card_expiration_year": 2030,
  "card_cvc": 999
}
```
9. This will return a http response with 200 status if all goes well or a http response with 400 status if there is an error. Inside the response there will be a message detailing the error.
10. You cannot subscribe again with a user if it's already subscribed. It will return http response with a 409 status.
11. To check the status of your subscription we can make a get request using the endpoint `api/subscriptions/status`, it will return a response similar to this:
```json
{
  "status": "successful",
  "payment_gateway_status": "active",
  "current_period_start": "2021-10-04T14:31:51Z",
  "current_period_end": "2021-11-04T14:31:51Z",
  "id_reference": "sub_1JgsCpKBAHswNGjYZ238Ljws",
  "price_reference": "price_1JgB7LKBAHswNGjYXDWXgEnJ",
  "purchase_date": "2021-10-04"
}
```
12. And that's it! You have finished the base demo.
13. You can test to subscribe with as many users as you want and using different testing cards described in here: `https://stripe.com/docs/testing#international-cards`
14. It's interesting to test cards with extra security using 3D secure. For example using the card number `4000002500003155`. You will see the subscription will be in a failed status until you manually complete the card verificantion using the Stripe dashboard.

> NOTE
> Remember you can create new users or delete the `Customer`, `PaymentMethod` and `Subscription` related to a user
> if you need it to subscribe again, using the Django dashboard in the url `http://localhost:8000/admin/`


## Run the tests
With the server running you can launch the Django tests:
```sh
docker-compose exec django python manage.py test
```

You can also run the python linter in order to be PEP8 compliant.
```sh
docker-compose exec django sh lint.sh
```

## Deployment
We're using Docker to configure the project, so in order to deploy the project the simpliest way is to replicate the same steps described above. We recommend using `staging` or `production` as value for the variable `ENVIRONMENT` inside the `.env` file. This is to hide sensible information deactivating the debug mode.
It's also recommended to use gunicorn instead of Django runserver command for performance issues. The command to run the server would be this one:
```sh
gunicorn --bind 0.0.0.0:8000 --workers 3 stripe_assignment.wsgi
```
The last step you need to do is to create a new webhook endpoint using Stripe dashboard. We need to receive the Stripe events or the platform will not work. The url to point will be:
```sh
http(s)://IP_OR_URL:8000/api/stripe-webhook/
```
