from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django.db.models import F
from django.contrib import messages
from .models import *

def index(request):
    pro = Products.objects.all()
    return render(request,'index.html',{'pro':pro})

def login(request):
    if request.method == 'POST':
        username = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:
                auth_login(request, user)

                if user.is_superuser:
                    messages.success(request,'Admin login success')
                    return redirect('admin_dashboard')
                
                elif user.user_type == 'Customer':
                    customer = Customer.objects.filter(c_id=user).first()
                    if customer:
                        request.session['uid'] = customer.id
                        messages.success(request,'Customer login success')
                        return redirect('customer_dashboard')
                    else:
                        return redirect('login')

                elif user.user_type == 'Seller':
                    seller = Seller.objects.filter(s_id=user).first()
                    if seller:
                        request.session['uid'] = seller.id
                        messages.success(request,'Seller login success')
                        return redirect('seller_dashboard')
                    else:
                        return redirect('login')

                elif user.user_type == 'Delivery':
                    delivery = Delivery.objects.filter(del_id=user).first()
                    if delivery:
                        request.session['uid'] = delivery.id
                        messages.success(request,'Delivery User login success')
                        return redirect('delivery_dashboard')
                    else:
                        return redirect('login')
                else:
                    messages.error(request, 'User not found')
                    return redirect('login')
            else:
                messages.error(request, 'Your account is inactive. Please contact support.')
                return render(request,'login.html')
        else:
            messages.error(request, 'Invalid credentials. Please try again.')
            return render(request,'login.html')

    return render(request,'login.html')

def admin_dashboard(request):
    return render(request,'admin/admin_dashboard.html')

def adm_customer(request):
    cus = Login.objects.filter(user_type="Customer")
    return render(request,'admin/adm_customer.html',{'cus':cus})

def adm_seller(request):
    sel = Login.objects.filter(user_type="Seller").order_by('-id')
    return render(request,'admin/adm_seller.html',{'sel':sel})
    
def adm_seller_reg_approve(request):
    uid = request.GET.get('id')
    seller = Login.objects.get(id=uid)
    seller.is_active = True
    seller.save()
    return redirect('adm_seller')

def adm_delete_seller(request):
    uid = request.GET.get('id')
    Login.objects.get(id=uid).delete()
    return redirect(adm_seller)

def adm_seller_products(request):
    pro = Products.objects.all()
    return render(request,'admin/adm_seller_products.html',{'pro':pro})

def adm_customer_orders(request):
    cart = Cart.objects.filter(status='Paid').order_by('-id')
    dell = Delivery.objects.filter(status='Available')
    return render(request,'admin/adm_customer_orders.html',{'cart':cart,'del':dell})

def adm_delivery_user(request):
    
    return redirect('adm_customer_orders')

def adm_customer_feedbacks(request):
    fdbk = Feedback.objects.all().order_by('-id')
    status = request.GET.get('status','')
    if status:
        fdbk = fdbk.filter(rating=status)
    return render(request,'admin/adm_customer_feedbacks.html',{'i':fdbk})

def adm_delivery_portal(request):
    dell = Login.objects.filter(user_type="Delivery").order_by('-id')
    return render(request,'admin/adm_delivery_portal.html',{'del':dell})

def adm_approve_delivery(request):
    uid = request.GET.get('id')
    deli = Login.objects.get(id=uid)
    deli.is_active = True
    deli.save()
    return redirect('adm_delivery_portal')

def adm_remove_delivery(request):
    uid = request.GET.get('id')
    Delivery.objects.get(id=uid).delete()
    return redirect('adm_delivery_portal')

############################################_CUSTOMER_############################################

def customer(request):
    if request.method == 'POST':
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        c_dob = request.POST.get('dob')
        c_image = request.FILES.get('image')
        c_email = request.POST.get('email')
        c_password = request.POST.get('password')

        log = Login.objects.create_user(
            first_name = fname,
            last_name = lname,
            email = c_email,
            username = c_email,
            password = c_password,
            user_psd = c_password,
            user_type = 'Customer'
        )

        log.save()

        Customer.objects.create(
            first_name = fname,
            last_name = lname,
            date_of_birth = c_dob,
            email = c_email,
            image = c_image,
            c_id = log
        )

        return redirect('login')

    return render(request,'register.html')

def customer_dashboard(request):
    uid = request.session.get('uid')
    cus = Customer.objects.get(id=uid)
    return render(request,'customer/customer_dashboard.html',{'cus':cus})

def customer_profile(request):
    uid = request.session['uid']
    cus = Customer.objects.get(id=uid)
    return render(request,'customer/customer_profile.html',{'i':cus})

def customer_update_profile(request):
    uid = request.session['uid']
    cus = Customer.objects.get(id=uid)
    if request.method == 'POST':
        cus.first_name = request.POST.get('fname')
        cus.last_name = request.POST.get('lname')
        cus.date_of_birth = request.POST.get('dob')
        cus.email = request.POST.get('email')
        if "image" in request.FILES:
            cus.image = request.FILES.get('image')

        cus.save()

        return redirect('customer_profile')

    return render(request,'customer/customer_update_profile.html',{'i':cus})

def customer_view_products(request):
    products = Products.objects.all
    return render(request,'customer/customer_view_products.html',{'i':products})

def customer_add_to_cart(request):
    uid = request.session['uid']
    cid = Customer.objects.get(id=uid)
    pro = request.GET.get('id')
    pid = Products.objects.get(id=pro)
    cart = Cart.objects.filter(products=pro,customer=cid,status='Cart').exists()

    if cart:
        messages.error(request,"Already exists in cart!")
        return redirect('customer_view_products')

    Cart.objects.create(
        customer = cid,
        products = pid,
        quantity = int(1),
        price = pid.price,
        status = 'Cart',
        Normal_status = 'Cart'
    )
    messages.error(request,"Added to cart!")
    return redirect('customer_view_products')

def customer_checkout(request):
    uid = request.session.get('uid')
    cus = Customer.objects.get(id=uid)
    cart = Cart.objects.filter(customer=cus,status='Cart')
    total_price = sum(float(total.price) for total in cart)

    if request.method == 'POST':
        
        for i in cart:
            Products.objects.filter(id=i.products.id).update(
                quantity=F('quantity') - i.quantity
            )

        cart.update(Normal_status='Order',status='Paid')
        messages.success(request,"Payment success.")
        return redirect('customer_view_products')

    return render(request,'customer/customer_checkout.html',{'total':total_price, 'cart':cart, 'cus':cus})

def customer_remove_item_from_cart(request):
    uid = request.GET.get('id')
    Cart.objects.get(id=uid).delete()
    return redirect('customer_view_cart')

def customer_view_cart(request):
    uid = request.session.get('uid')
    cid = Customer.objects.get(id=uid)
    cart = Cart.objects.filter(customer=cid,status='Cart')
    return render(request,'customer/customer_view_cart.html',{'cart':cart})

def customer_update_cart(request):
    uid = request.GET.get('id')
    cart = Cart.objects.get(id=uid)
    price = float(cart.products.price)

    if request.method == 'POST':
        qty = request.POST.get('update_qty')

        if int(qty) <= 0:
            return redirect('customer_view_cart')
        cart.quantity = int(qty)
        cart.price = cart.quantity * price
        cart.save()
        
    return redirect('customer_view_cart')

def customer_cart_history(request):
    uid = request.session.get('uid')
    cid = Customer.objects.get(id=uid)
    cart = Cart.objects.filter(customer=cid,status='Paid')
    return render(request,'customer/customer_cart_history.html',{'cart':cart})

def customer_feedback(request):
    uid = request.GET.get('id')
    cart_id = Cart.objects.get(id=uid)
    if request.method == 'POST':
        c_rating = request.POST.get('rating')
        c_feedback = request.POST.get('feedback')

        Feedback.objects.create(
            rating = c_rating,
            feedback = c_feedback,
            cart = cart_id
        )

        messages.success(request,"Feedback submited successfully!")
        return redirect('customer_cart_history')

    return render(request,'customer/customer_feedback.html')

############################################_SELLER_############################################

def seller(request):
    if request.method == 'POST':
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        idnum = request.POST.get('idnum')
        dob = request.POST.get('dob')
        s_image = request.FILES.get('image')
        s_email = request.POST.get('email')
        s_password = request.POST.get('password')

        log = Login.objects.create_user(
            first_name = fname,
            last_name = lname,
            email = s_email,
            username = s_email,
            password = s_password,
            user_psd = s_password,
            user_type = 'Seller'
        )

        log.is_active = False
        log.save()

        Seller.objects.create(
            first_name = fname,
            last_name = lname,
            id_number = idnum,
            date_of_birth = dob,
            email = s_email,
            image = s_image,
            s_id = log
        )

        messages.success(request,"Seller account created successfully! Please wait for admin approval.")
        return redirect('login')

    return render(request,'seller.html')

def seller_dashboard(request):
    uid = request.session.get('uid')
    sel = Seller.objects.get(id=uid)
    cus = Cart.objects.filter(status='Paid',products__p_id=sel).order_by('-id')
    total = sum(float(i.price) for i in cus if i.status == 'Paid')
    return render(request,'seller/seller_dashboard.html',{'sel':sel,'cus':cus,'total':total})

def seller_cus_feedback(request):
    uid = request.session.get('uid')
    sel = Seller.objects.get(id=uid)
    feedback = Feedback.objects.filter(cart__products__p_id = sel).order_by('-id')
    return render(request,'seller/seller_cus_feedback.html',{'i':feedback,'sel':sel})

def seller_deliver_pro(request):
    uid = request.GET.get('id')
    cart = Cart.objects.get(id=uid)
    cart.Normal_status = 'Shipped'
    cart.save()
    return redirect('seller_dashboard')

def seller_delete_from_cart(request):
    uid = request.GET.get('id')
    Cart.objects.get(id=uid).delete()
    return redirect('seller_dashboard')

def seller_profile(request):
    uid = request.session['uid']
    seller = Seller.objects.get(id=uid)
    return render(request,'seller/seller_profile.html',{'i':seller})

def seller_profile_update(request):
    uid = request.session['uid']
    seller = Seller.objects.get(id=uid)

    if request.method == 'POST':
        seller.first_name = request.POST.get('fname')
        seller.last_name = request.POST.get('lname')
        seller.date_of_birth = request.POST.get('dob')
        if 'image' in request.FILES:
            seller.image = request.FILES.get('image')

        seller.save()

        return redirect('seller_profile')

    return render(request,'seller/seller_profile_update.html',{'i':seller})

def seller_add_products(request):
    uid = request.session['uid']
    seller = Seller.objects.get(id=uid)

    if request.method == 'POST':
        p_name = request.POST.get('pname')
        p_sku = request.POST.get('sku')
        p_image = request.FILES.get('image')
        p_desc = request.POST.get('desc')
        p_batch = request.POST.get('batch')
        p_qty = request.POST.get('qty')
        p_price = request.POST.get('price')

        Products.objects.create(
            product_name = p_name,
            sku = p_sku,
            image = p_image,
            description = p_desc,
            batch = p_batch,
            quantity = p_qty,
            price = p_price,
            p_id = seller
        )

        return redirect('seller_view_products')

    return render(request,'seller/seller_add_products.html')

def seller_view_products(request):
    uid = request.session['uid']
    products = Products.objects.filter(p_id=uid)
    return render(request,'seller/seller_view_products.html',{'products':products})

def seller_edit_product(request):
    uid = request.GET.get('id')
    pro = Products.objects.get(id=uid)
    if request.method == 'POST':
        pro.product_name = request.POST.get('pname')
        pro.sku = request.POST.get('sku')
        pro.description = request.POST.get('desc')
        pro.batch = request.POST.get('batch')
        pro.quantity = request.POST.get('qty')
        pro.price = request.POST.get('price')
        if "image" in request.FILES:
            pro.image = request.FILES.get('image')

        pro.save()

        return redirect('seller_view_products')

    return render(request,'seller/seller_edit_product.html',{'i':pro})

def seller_delete_products(request):
    uid = request.GET.get('id')
    Products.objects.get(id=uid).delete()
    return redirect('seller_view_products')

############################################_DLIVERY_############################################

def delivery_reg(request):
    if request.method == 'POST':
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        dob = request.POST.get('dob')
        idnum = request.POST.get('idnum')
        d_image = request.FILES.get('image')
        d_card_image = request.FILES.get('idfile')
        d_email = request.POST.get('email')
        d_password = request.POST.get('password')

        log = Login.objects.create_user(
            first_name = fname,
            last_name = lname,
            email = d_email,
            username = d_email,
            password = d_password,
            user_psd = d_password,
            user_type = 'Delivery'
        )

        log.is_active = False
        log.save()

        Delivery.objects.create(
            first_name = fname,
            last_name = lname,
            date_of_birth = dob,
            card_number = idnum,
            card_image = d_card_image,
            email = d_email,
            image = d_image,
            status = 'Available',
            del_id = log
        )

        messages.success(request,'Delivery registration successfull !')
        return redirect('login')

    return render(request,'delivery_reg.html')

def delivery_dashboard(request):
    return render(request,'delivery/delivery_dashboard.html')