from django.db import models
from django.db.models.query import QuerySet
from django.contrib.auth.models import User

# Create your models here.
#Custom Manager vuwa wzpy ujdp kkrj


class CustomManager(models.Manager):
    def get_price_range(self,r1,r2):
        return self.filter(price__range=(r1,r2))
    
    def watch_list(self):
        return self.filter(category__exact="watch")
    
    def mobile_list(self):
        return self.filter(category__exact="mobile")
    
    def laptop_list(self):
        return self.filter(category__exact="laptop")
    
    def get_queryset(self) -> QuerySet:
        return super().get_queryset().order_by("price")
    
        
    
class Product(models.Model):
    product_id = models.IntegerField(primary_key=True)
    product_name = models.CharField(max_length = 55)
    desc= models.CharField(max_length = 255)
    type = (('mobile','mobile'),("watch","watch"),("laptop","laptop"))
    category = models.CharField(max_length=6, choices=type)
    price = models.IntegerField()
    image = models.ImageField(upload_to = 'photo/')
    user = models.ForeignKey(User,on_delete = models.CASCADE,blank = True, null = True)
    
    prod = CustomManager()
    objects = models.Manager()
    
class CartItem(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default = 0)
    date_added = models.DateTimeField(auto_now_add = True)
    user = models.ForeignKey(User,on_delete = models.CASCADE,default = 1)
    
class Order(models.Model):
    order_id = models.IntegerField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default = 0)
    user = models.ForeignKey(User,on_delete = models.CASCADE,default = 1)
    is_completed = models.BooleanField(default = False)