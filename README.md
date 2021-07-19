# DjangoCatering
Catering site made on Django. Located in Szczecin


<!-- ABOUT THE PROJECT -->
## About The Project
Hi! Welcome on my Django Project!. It is catering site, you are able to order some diets on your address.


### Functions
* Ability to order diets as logged user and guest
* Date of order validation
* App is connected with Google Maps API. It calculates distance between catering and order destination, my site has Autocomplete address function included too.
* Order history for logged user
* Ability for site moderator to create new diet offers and diet examples
* Contact form 
* Two payment option - Tranfer and simulated request for Przelewy24( I don't have Przelewy24 account so it is impossible to make it to the end)
### Stack

* Python3
* django~=3.2.4
* django-crispy-forms
* Pillow~=8.2.0
* requests~=2.25.1
* holidays~=0.11.1
* djangorestframework~=3.12.4

<!-- How to install -->
## How to instal:
Clone repository from GitHub or download it. 

Open Dockerfile and set your environment variables:



  ```sh
FROM python:latest
ENV GOOGLE_MAPS_KEY ##YourKey

ENV EMAIL_USER ##YourKey

ENV EMAIL_PASS ##YourKey

WORKDIR /Catering

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
  ```

  
Create image:

  ```sh
docker build .
 ```
Run docker image:
  ```sh
docker run -d -p [PORT] [CONTAINER_ID]
 ```
## Settings:



###Google Maps :
To get API key, visit https://developers.google.com/maps and follow the instructions.

###Email:
Just pass email password and address to Dockerfile, be sure that your email account allows to use extern applications.

 #Order terms:

* Catering works delivers only on working days
* Weekends and holidays are not included
* Diet can be ordered minimum 3 days ahead from today's date
* If your location is less than 5 km, delivery is for free
* If your location is more than 5 km and less than 10, you need to pay extra
* If location is more than 10 km , diet cannot be ordered

## Diets offer:
My site has 3 diets included, admin can extend the offer if it's necessary.
![img.png](img.png)
## Order history:

Logged user has ability to check, his orders history
![img_1.png](img_1.png)


## Cart
Every order is collected in a cart:

![img_2.png](img_2.png)


If diet is out of date, it shows a message, that user should change it.

![img_3.png](img_3.png)
## Checkout

There are two terms, to make a checkout:
* There must be minimum one diet in a cart.
* Diets from a cart must have to be up to date.



Customer has to fill all fields and choice payment option, after
that system sends email to user.

I made registration request to Przelewy24, but it can't be finalised without Przelewy24 shop account, but serializer looks working good ;)
This is how it looks like if you choose Przelewy24 payment:

![img_4.png](img_4.png)


##Tests:
Test will be included in a future




ENJOY!

 
  


<!-- CONTACT -->
## Contact

Sebastian Szymański - shadow.smoke7@gmail.com

