from pickle import FALSE
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.http import JsonResponse
from posApp.models import Category, Products, Sales, salesItems
from django.contrib.auth.models import User 
from django.db.models import Count, Sum
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
import json, sys
from datetime import date, datetime
from django.contrib.auth.hashers import make_password
from .models import UserProfile


#navigation
def user_profile(request):
    if request.user.is_authenticated:
        try:
            return {'profile': UserProfile.objects.get(user=request.user)}
        except UserProfile.DoesNotExist:
            return {'profile': None}
    return {}

# Login
def login_user(request):
    logout(request)
    resp = {"status": 'failed', 'msg': ''}
    username = ''
    password = ''

    if request.POST:
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                resp['status'] = 'success'
                return HttpResponse(json.dumps(resp), content_type='application/json')
            else:
                resp['msg'] = "Votre compte est inactif. Veuillez vous abonner pour accéder à la plateforme."
                return HttpResponse(json.dumps(resp), content_type='application/json')
        else:
           resp['msg'] = ("Impossible de se connecter ?\n"
                           "1- Mot de passe ou nom utilisateur incorrect.\n"
                           "2- Abonnement non renouvelé.\n"
                           "Contactez le support.")

    return HttpResponse(json.dumps(resp), content_type='application/json')

#Logout
def logoutuser(request):
    logout(request)
    return redirect('/')

# Create your views here.
@login_required
def home(request):
    now = datetime.now()
    current_year = now.strftime("%Y")
    current_month = now.strftime("%m")
    current_day = now.strftime("%d")
    categories = len(Category.objects.all())
    products = len(Products.objects.all())
    transaction = len(Sales.objects.filter(
        date_added__year=current_year,
        date_added__month = current_month,
        date_added__day = current_day
    ))
    today_sales = Sales.objects.filter(
        date_added__year=current_year,
        date_added__month = current_month,
        date_added__day = current_day
    ).all()
    total_sales = sum(today_sales.values_list('grand_total',flat=True))
    context = {
        'page_title':'Home',
        'categories' : categories,
        'products' : products,
        'transaction' : transaction,
        'total_sales' : total_sales,
    }
    return render(request, 'posApp/home.html',context)


def about(request):
    context = {
        'page_title':'About',
    }
    return render(request, 'posApp/about.html',context)

#Categories
@login_required
def category(request):
    category_list = Category.objects.filter(id_user = request.user.id)
    # category_list = {}
    context = {
        'page_title':'Category List',
        'category':category_list,
    }
    return render(request, 'posApp/category.html',context)
@login_required
def manage_category(request):
    category = {}
    if request.method == 'GET':
        data =  request.GET
        id = ''
        if 'id' in data:
            id= data['id']
        if id.isnumeric() and int(id) > 0:
            category = Category.objects.filter(id=id).first()

    context = {
        'category' : category
    }
    return render(request, 'posApp/manage_category.html',context)

@login_required
def save_category(request):
    data =  request.POST
    resp = {'status':'failed'}
    try:
        current_user = request.user.id
        if (data['id']).isnumeric() and int(data['id']) > 0 :
            save_category = Category.objects.filter(id = data['id']).update(name=data['name'], description = data['description'],status = data['status'],id_user = current_user)
        else:
            save_category = Category(name=data['name'], description = data['description'],status = data['status'],id_user = current_user)
            save_category.save()
        resp['status'] = 'success'
        messages.success(request, 'Catégorie enregistrée avec succès.')
    except:
        resp['status'] = 'failed'
    return HttpResponse(json.dumps(resp), content_type="application/json")

@login_required
def delete_category(request):
    data =  request.POST
    resp = {'status':''}
    try:
        Category.objects.filter(id = data['id']).delete()
        resp['status'] = 'success'
        messages.success(request, 'Catégorie supprimée avec succès.')
    except:
        resp['status'] = 'failed'
    return HttpResponse(json.dumps(resp), content_type="application/json")

# Products
@login_required
def products(request):
    product_list = Products.objects.filter(id_user = request.user.id)
    context = {
        'page_title':'Product List',
        'products':product_list,
    }
    return render(request, 'posApp/products.html',context)

@login_required
def manage_products(request):
    product = {}
    categories = Category.objects.filter(status = 1, id_user=request.user.id).all()
    if request.method == 'GET':
        data =  request.GET
        id = ''
        if 'id' in data:
            id= data['id']
        if id.isnumeric() and int(id) > 0:
            product = Products.objects.filter(id=id).first()

    context = {
        'product' : product,
        'categories' : categories
    }
    return render(request, 'posApp/manage_product.html',context)
def test(request):
    categories = Category.objects.all()
    context = {
        'categories' : categories
    }
    return render(request, 'posApp/test.html',context)
@login_required
def save_product(request):
    data = request.POST
    resp = {'status': 'failed'}
    id = ''

    if 'id' in data:
        id = data['id']

    category = Category.objects.filter(id=data['category_id']).first()
    current_user = request.user.id

    try:
        if id.isnumeric() and int(id) > 0:
            # Mise à jour du produit existant
            product = Products.objects.get(id=id)
            product.category_id = category
            product.name = data['name']
            product.description = data['description']
            product.price = float(data['price'])
            product.quantity = data['quantity']
            product.status = data['status']
            product.id_user = current_user

            # Générer le nouveau code basé sur l'ID de l'utilisateur et l'ID du produit
            new_code = f'{current_user}-prod-{product.id}'
            product.code = new_code  # Mettre à jour le code
            product.save()  # Sauvegarder le produit
        else:
            # Création d'un nouveau produit
            new_product = Products(
                code='',  # Laisser vide pour générer plus tard
                category_id=category,
                name=data['name'],
                description=data['description'],
                price=float(data['price']),
                quantity=data['quantity'],
                status=data['status'],
                id_user=current_user
            )
            new_product.save()  # Sauvegarder le produit
            # Générer le code basé sur l'ID de l'utilisateur et l'ID du produit
            new_code = f'{current_user}-prod-{new_product.id}'
            new_product.code = new_code  # Mettre à jour le code du produit
            new_product.save()  # Sauvegarder le produit avec le code mis à jour

        resp['status'] = 'success'
        messages.success(request, 'Product Successfully saved.')
    except Exception as e:
        resp['status'] = 'failed'
        resp['msg'] = str(e)  # Inclure le message d'erreur pour le débogage

    return HttpResponse(json.dumps(resp), content_type="application/json")

@login_required
def delete_product(request):
    data =  request.POST
    resp = {'status':''}
    try:
        Products.objects.filter(id = data['id']).delete()
        resp['status'] = 'success'
        messages.success(request, 'Product Successfully deleted.')
    except:
        resp['status'] = 'failed'
    return HttpResponse(json.dumps(resp), content_type="application/json")
@login_required
def pos(request):
    products = Products.objects.filter(status = 1,id_user = request.user.id)
    product_json = []
    for product in products:
        product_json.append({'id':product.id, 'name':product.name, 'quantity':product.quantity, 'price':float(product.price)})
    context = {
        'page_title' : "Point of Sale",
        'products' : products,
        'product_json' : json.dumps(product_json)
    }
    # return HttpResponse('')
    return render(request, 'posApp/pos.html',context)

## User

@login_required
def users(request):
    # Précharge les profils liés
    user_list = User.objects.select_related('profile').all()

    context = {
        'page_title': 'User List',
        'users': user_list,
    }
    return render(request, 'posApp/user.html', context)

@login_required
def manage_users(request):
    user = {}
    # Récupérer tous les utilisateurs sans filtre
    users = User.objects.all()  # Cette ligne récupère tous les utilisateurs de la base de données
    
    if request.method == 'GET':
        data = request.GET
        user_id = ''
        
        if 'id' in data:
            user_id = data['id']
        
        if user_id.isnumeric() and int(user_id) > 0:
            user = User.objects.filter(id=user_id).first()
    
    context = {
        'user': user,
        'users': users,
    }
    
    return render(request, 'posApp/manage_user.html', context)

@login_required
def save_user(request):
    data = request.POST
    resp = {'status':'failed'}
    id = ''
    if 'id' in data :
        id=data['id']
    
    try:
        
        if id.isnumeric() and int(id) > 0:
            # Mise à jour de l'utilisateur
            user = User.objects.get(id=id)

            # Mettre à jour uniquement les champs modifiés
            if 'first_name' in data:
                user.first_name = data['first_name']  # Mettre à jour uniquement si fourni
            if 'last_name' in data:
                user.last_name = data['last_name']
            if 'username' in data:
                user.username = data['username']
            if 'email' in data:
                user.email = data['email']

            # Mise à jour du mot de passe uniquement si un nouveau mot de passe est fourni
            if 'password' in data and data['password']:
                user.password = make_password(data['password'])
           # Gestion de user_type via le profil
            profile, created = UserProfile.objects.get_or_create(user=user)
            if 'user_type' in data:
                user_type = data['user_type']
                if user_type in ['admin', 'binome', 'employe']:
                    profile.user_type = user_type
                    profile.save()  # Sauvegarder le profil si mis à jour

            # Sauvegarder les modifications
            user.save()
            print(f"Après sauvegarde - ID de l'utilisateur : {user.id}")
            print(f"Nom : {user.first_name}, Prénom : {user.last_name}, Email : {user.email},Type : {profile.user_type}")
        else:
            new_user = User(
                first_name = data['first_name'],
                last_name=data['last_name'],   # Nom de famille de l'utilisateur
                username=data['username'],  # Nom d'utilisateur
                email=data['email'],  # Adresse email
                password=make_password(data['password']),  # Hachage du mot de passe
             )
            new_user.save()
            # Créer un profil utilisateur
            new_profile = UserProfile.objects.create(user=new_user, user_type=data['user_type'])
            
        resp['status'] = 'success'
        messages.success(request, 'Utilisateur enregistre avec succes')
    except Exception as e:
        resp['status'] = 'failed'
        resp['msg'] = str(e)  # Inclure le message d'erreur pour le débogage

    return HttpResponse(json.dumps(resp), content_type="application/json")

@login_required
def delete_user(request):
    data =  request.POST
    resp = {'status':''}
    try:
        User.objects.filter(id = data['id']).delete()
        resp['status'] = 'success'
        messages.success(request, "l'utilisateur a ete supprime avec succes")
    except:
        resp['status'] = 'failed'
    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def checkout_modal(request):
    grand_total = 0
    if 'grand_total' in request.GET:
        grand_total = request.GET['grand_total']
    context = {
        'grand_total' : grand_total,
    }
    return render(request, 'posApp/checkout.html',context)

@login_required
def save_pos(request):
    resp = {'status':'failed','msg':''}
    data = request.POST
    pref = datetime.now().year + datetime.now().year
    i = 1
    while True:
        code = '{:0>5}'.format(i)
        i += int(1)
        check = Sales.objects.filter(code = str(pref) + str(code)).all()
        if len(check) <= 0:
            break
    code = str(pref) + str(code)

    try:
        sales = Sales(code=code, sub_total = data['sub_total'], tax = data['tax'], tax_amount = data['tax_amount'], grand_total = data['grand_total'], tendered_amount = data['tendered_amount'], amount_change = data['amount_change'],id_user = request.user.id).save()
        sale_id = Sales.objects.last().pk
        i = 0
        for prod in data.getlist('product_id[]'):
            product_id = prod
            sale = Sales.objects.filter(id=sale_id).first()
            product = Products.objects.filter(id=product_id).first()
            qty = data.getlist('qty[]')[i]
            price = data.getlist('price[]')[i]
            total = float(qty) * float(price)
            print({'sale_id' : sale, 'product_id' : product, 'qty' : qty, 'price' : price, 'total' : total})
            if product.quantity >= int(qty):
                product.quantity -= int(qty)  # Enlever la quantité vendue du stock
                product.save()
            else:
                resp['msg'] = f"Stock insuffisant pour le produit {product.name}"
                return HttpResponse(json.dumps(resp),content_type="application/json")

            salesItems(sale_id = sale, product_id = product, qty = qty, price = price, total = total).save()
            i += int(1)
        resp['status'] = 'success'
        resp['sale_id'] = sale_id
        messages.success(request, "Sale Record has been saved.")
    except:
        resp['msg'] = "An error occured"
        print("Unexpected error:", sys.exc_info()[0])
    return HttpResponse(json.dumps(resp),content_type="application/json")

@login_required
def salesList(request):
    sales = Sales.objects.filter(id_user = request.user.id)
    sale_data = []
    for sale in sales:
        data = {}
        for field in sale._meta.get_fields(include_parents=False):
            if field.related_model is None:
                data[field.name] = getattr(sale,field.name)
        data['items'] = salesItems.objects.filter(sale_id = sale).all()
        data['item_count'] = len(data['items'])
        if 'tax_amount' in data:
            data['tax_amount'] = format(float(data['tax_amount']),'.2f')
        # print(data)
        sale_data.append(data)
    # print(sale_data)
    context = {
        'page_title':'Sales Transactions',
        'sale_data':sale_data,
    }
    # return HttpResponse('')
    return render(request, 'posApp/sales.html',context)

@login_required
def receipt(request):
    id = request.GET.get('id')
    sales = Sales.objects.filter(id = id).first()
    transaction = {}
    for field in Sales._meta.get_fields():
        if field.related_model is None:
            transaction[field.name] = getattr(sales,field.name)
    if 'tax_amount' in transaction:
        transaction['tax_amount'] = format(float(transaction['tax_amount']))
    ItemList = salesItems.objects.filter(sale_id = sales).all()
    username = request.user.username
    context = {
        "transaction" : transaction,
        "salesItems" : ItemList,
        "username": username
    }

    return render(request, 'posApp/receipt.html',context)
    # return HttpResponse('')

@login_required
def delete_sale(request):
    resp = {'status':'failed', 'msg':''}
    id = request.POST.get('id')
    try:
        delete = Sales.objects.filter(id = id).delete()
        resp['status'] = 'success'
        messages.success(request, 'Sale Record has been deleted.')
    except:
        resp['msg'] = "An error occured"
        print("Unexpected error:", sys.exc_info()[0])
    return HttpResponse(json.dumps(resp), content_type='application/json')