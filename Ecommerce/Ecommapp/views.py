from django.shortcuts import render,HttpResponse,redirect
from .models import Product,CartItem,Order
from django.db.models import Q
from .forms import CreateUserForm,AddProduct
from django.contrib.auth import login,logout,authenticate
from django.contrib import messages
import random,razorpay
from django.core.mail import send_mail

# Create your views here.
def index(request):
    products = Product.objects.all()
    context={}
    context['products']= products
    return render(request,"index.html",context)

def detail(request,pid):
    product = Product.objects.get(product_id = pid)
    return render(request,"details.html",{'product':product})

def viewcart(request):
    if request.user.is_authenticated:
        allproducts = CartItem.objects.filter(user = request.user)
    else:
        return redirect("/login")
    context = {}
    context['cart_items']=allproducts
    total_price = 0
    for x in allproducts:
        total_price += (x.product.price * x.quantity)
        print(total_price)
        context['total'] = total_price
        length = len(allproducts)
        context['items'] = length
    return render(request,"cart.html",context)

def addcart(request,pid):
    products = Product.objects.get(product_id = pid)
    user = request.user if request.user.is_authenticated else None
    print(products)
    if user :
        cart_item,created = CartItem.objects.get_or_create(product=products,user = user)
        print(cart_item,created)
    else:
        cart_item,created = CartItem.objects.get_or_create(product=products,user = None)
    if not created:
        cart_item.quantity +=1
    else:
        cart_item.quantity =1
    cart_item.save()
    return redirect("/viewcart")

def remove(request,pid):
    p = CartItem.objects.filter(product_id = pid)
    p.delete()
    return redirect("/viewcart")

def search(request):
    query = request.POST['q']
    print(f"Received Item is {query}")
    if not query:
        result = Product.objects.all()
    else:
        result = Product.objects.filter(
            Q(product_name__icontains = query)|
            Q(category__icontains = query)|
            Q(price__icontains = query)
        )
    return render(request,'search.html',{'results':result,'query':query})

def range(req):
    if req.method == "GET":
        return redirect("/")
    else:
        r1 = req.POST.get("min")
        r2 = req.POST.get("max")
        print(r1,r2)
    if r1 is not None and r2 is not None and r1 !="" and r2 !="":
        queryset = Product.prod.get_price_range(r1,r2)
        context={'products':queryset}
    return render(req,"index.html",context)
    
def watchlist(req):
    queryset = Product.prod.watch_list()
    context={'products':queryset}
    return render(req,'index.html',context)

def mobilelist(req):
    queryset = Product.prod.mobile_list()
    context={'products':queryset}
    return render(req,'index.html',context)

def laptoplist(req):
    queryset = Product.prod.laptop_list()
    context={'products':queryset}
    return render(req,'index.html',context)

def sort(request):
    queryset = Product.objects.all().order_by("price")
    context = {'products':queryset}
    return render(request,'index.html',context)

def sortd(request):
    queryset = Product.objects.all().order_by("-price")
    context = {'products':queryset}
    return render(request,'index.html',context)

def updateqty(req,uval,pid):
    products = Product.objects.get(product_id = pid)
    user = req.user
    c =CartItem.objects.filter(product = products,user = user)
    print(c)
    print(c[0])
    print(c[0].quantity)
    if uval == 1:
        a = c[0].quantity + 1
        c.update(quantity = a)
        print(c[0].quantity)
    elif uval==0:
        a = c[0].quantity - 1
        c.update(quantity = a)
        print(c[0].quantity)
    return redirect("/viewcart")

def register_user(request):
    form = CreateUserForm()
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,("User Created Successfully"))
            return redirect("/login")
        else:
            messages.error(request,("Username or Password Invalid !!"))
    context = {'form':form}
    return render(request,"register.html",context)

def login_user(request):
    if request.method=="POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            messages.success(request,("Logged in Successfully"))
            return redirect("/")
        else:
            messages.error(request,"Error! Try Again!!")
            return redirect('/login')
        
    return render(request,"login.html")

def logout_user(request):
    logout(request)
    messages.success(request,("You are Logout"))
    return redirect("/")

def vieworder(req):
    c = CartItem.objects.filter(user = req.user)
    context={}
    context = {}
    context['cart_items']=c
    total_price = 0
    for x in c:
        total_price += (x.product.price * x.quantity)
        print(total_price)
        context['total'] = total_price
        length = len(c)
        context['items'] = length
    return render(req,"vieworder.html",context)

def makepayment(req):
    c = CartItem.objects.filter(user = req.user)
    oid = random.randrange(1000,9999)
    for x in c:
        Order.objects.create(order_id = oid,product_id = x.product.product_id,user = req.user, quantity = x.quantity)
    orders = Order.objects.filter(user = req.user,is_completed = False)
    total_price = 0
    for x in orders:
        total_price += (x.product.price * x.quantity)
        oid = x.order_id
        print(oid)
    client = razorpay.Client(auth=("rzp_test_59qXQ6StJGhFat", "GvxJTHsElnI5WdRxpcWFzd02"))

    data = {
        "amount": total_price * 100,
        "currency": "INR",
        "receipt": "oid"
        }
    payment = client.order.create(data = data)
    context = {}
    context['data'] = payment
    context['amount'] = payment["amount"]
    uemail = req.user.email
    print(uemail)
    msg=f"""Thank You!!
    your order id is :{oid}
    Total price is :{total_price}"""
    send_mail(
    "Order placed successfully",
    "Order Details",
    "cashcurio@gmail.com",   #senders mail id
    ["to@example.com"],  #recievers mail id
    fail_silently=False,
)
    c.delete()
    orders.update(is_completed = True)
    return render(req,"payment.html",payment)

def insertProd(req):
    if req.user.is_authenticated:
        user = req.user
        if req.method == "GET":
            form = AddProduct()
            return render(req,"insertProd.html",{'form':form})
        else:
            form = AddProduct(req.POST,req.FILES or None)
            if form.is_valid():
                form.save()
                messages.success(req,("Product Entered Successfully"))
                return redirect("/")
            else:
                messages.error(req,"incorrect data")
                return render(req,"insertProd.html",{'form':form})
                
    else:
        return redirect('/login')
    

