from django.db import models
from django.contrib.auth.models import AbstractUser

class Login(AbstractUser):
    user_type = models.CharField(max_length=255, null=True)
    user_psd = models.CharField(max_length=255, null=True)

class Customer(models.Model):
    first_name = models.CharField(max_length=255, null=True)
    last_name = models.CharField(max_length=255, null=True)
    date_of_birth = models.CharField(max_length=255, null=True)
    email = models.CharField(max_length=255, null=True)
    image = models.ImageField(null=True)
    c_id = models.ForeignKey(Login, on_delete=models.CASCADE, null=True)

class Seller(models.Model):
    first_name = models.CharField(max_length=50, null=True)
    last_name = models.CharField(max_length=50, null=True)
    id_number = models.CharField(max_length=50, null=True)
    date_of_birth = models.CharField(max_length=50, null=True)
    email = models.CharField(max_length=50, null=True)
    image = models.ImageField(null=True)
    s_id = models.ForeignKey(Login, on_delete=models.CASCADE, null=True)

class Products(models.Model):
    product_name = models.CharField(max_length=255, null=True)
    sku = models.CharField(max_length=255, null=True)
    image = models.ImageField(null=True)
    description = models.CharField(max_length=255, null=True)
    batch = models.CharField(max_length=255, null=True)
    quantity = models.IntegerField(null=True)
    price = models.IntegerField(null=True)
    p_id = models.ForeignKey(Seller, on_delete=models.CASCADE, null=True)

class Cart(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True)
    products = models.ForeignKey(Products, on_delete=models.CASCADE, null=True)
    quantity = models.CharField(max_length=255, null=True)
    price = models.CharField(max_length=255, null=True)
    status = models.CharField(max_length=255, null=True)
    Normal_status = models.CharField(max_length=255, null=True)

class Feedback(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True)
    feedback = models.CharField(max_length=255, null=True)
    rating = models.CharField(max_length=255, null=True)

class Delivery(models.Model):
    first_name = models.CharField(max_length=255, null=True)
    last_name = models.CharField(max_length=255, null=True)
    date_of_birth = models.CharField(max_length=255, null=True)
    card_number = models.CharField(max_length=255, null=True)
    card_image = models.ImageField(null=True)
    email = models.CharField(max_length=255, null=True)
    image = models.ImageField(null=True)
    status = models.CharField(max_length=255, null=True)
    del_id = models.ForeignKey(Login, on_delete=models.CASCADE, null=True)