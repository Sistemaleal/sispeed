from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render

from .forms import (
    CompanySignUpForm,
    ContactForm,
    LoginForm,
    ProductForm,
    SectorForm,
    UserCreateForm,
    UserUpdateForm,
    CompanySettingsForm,
    UserPreferenceForm,
)
from .models import (
    Company,
    Contact,
    Product,
    Sector,
    UserCompany,
    UserPermission,
    UserPreference,
)


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    form = LoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"]
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("dashboard")
        messages.error(request, "Usuário ou senha inválidos.")
    return render(request, "auth/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("login")


def company_signup_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    form = CompanySignUpForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        company = Company.objects.create(
            name=form.cleaned_data["company_name"],
            email=form.cleaned_data["company_email"],
            phone=form.cleaned_data["company_phone"],
            cnpj=form.cleaned_data["cnpj"],
        )
        user = User.objects.create_user(
            username=form.cleaned_data["username"],
            email=form.cleaned_data["admin_email"],
            password=form.cleaned_data["password"],
            first_name=form.cleaned_data["admin_name"],
            is_staff=True,
            is_superuser=False,
        )
        user_company = UserCompany.objects.create(
            user=user,
            company=company,
            is_owner=True,
        )

        UserPermission.objects.create(
            user_company=user_company,
            can_manage_contacts=True,
            can_manage_users=True,
            can_manage_products=True,
            can_manage_sectors=True,
        )

        UserPreference.objects.create(
            user=user,
            theme="dark",
        )

        messages.success(request, "Cadastro realizado com sucesso! Faça login.")
        return redirect("login")

    return render(request, "auth/company_signup.html", {"form": form})


@login_required
def dashboard_view(request):
    return render(request, "dashboard/home.html")


# -------- Helpers --------


def _get_user_company(request) -> Company:
    return request.user.company_link.company


def _get_user_company_link(request) -> UserCompany:
    return request.user.company_link


def _get_user_permissions(request) -> UserPermission | None:
    try:
        return request.user.company_link.permissions
    except UserPermission.DoesNotExist:
        return None


def _require_permission(request, field_name: str, redirect_name: str = "dashboard"):
    user_company = _get_user_company_link(request)
    if user_company.is_owner:
        return None

    perms = _get_user_permissions(request)
    if not perms or not getattr(perms, field_name, False):
        messages.error(request, "Você não tem permissão para acessar esta área.")
        return redirect(redirect_name)
    return None


# -------- CONTATOS --------

@login_required
def contacts_list(request):
    deny = _require_permission(request, "can_manage_contacts")
    if deny:
        return deny
    company = _get_user_company(request)
    contacts = Contact.objects.filter(company=company)
    return render(request, "contacts/list.html", {"contacts": contacts})


@login_required
def contacts_create(request):
    deny = _require_permission(request, "can_manage_contacts")
    if deny:
        return deny
    company = _get_user_company(request)
    form = ContactForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        contact = form.save(commit=False)
        contact.company = company
        contact.save()
        messages.success(request, "Contato cadastrado com sucesso.")
        return redirect("contacts_list")
    return render(request, "contacts/form.html", {"form": form, "mode": "create"})


@login_required
def contacts_edit(request, pk):
    deny = _require_permission(request, "can_manage_contacts")
    if deny:
        return deny
    company = _get_user_company(request)
    contact = get_object_or_404(Contact, pk=pk, company=company)
    form = ContactForm(request.POST or None, instance=contact)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Contato atualizado com sucesso.")
        return redirect("contacts_list")
    return render(
        request,
        "contacts/form.html",
        {"form": form, "mode": "edit", "contact": contact},
    )


@login_required
def contacts_delete(request, pk):
    deny = _require_permission(request, "can_manage_contacts")
    if deny:
        return deny
    company = _get_user_company(request)
    contact = get_object_or_404(Contact, pk=pk, company=company)
    if request.method == "POST":
        contact.delete()
        messages.success(request, "Contato excluído com sucesso.")
        return redirect("contacts_list")
    return render(request, "contacts/confirm_delete.html", {"contact": contact})


# -------- USUÁRIOS --------

@login_required
def users_list(request):
    deny = _require_permission(request, "can_manage_users")
    if deny:
        return deny
    company = _get_user_company(request)
    user_links = UserCompany.objects.select_related("user").filter(company=company)
    return render(request, "users/list.html", {"user_links": user_links})


@login_required
def users_create(request):
    deny = _require_permission(request, "can_manage_users")
    if deny:
        return deny
    company = _get_user_company(request)
    form = UserCreateForm(request.POST or None, company=company)
    if request.method == "POST" and form.is_valid():
        user = User.objects.create_user(
            username=form.cleaned_data["username"],
            email=form.cleaned_data["email"],
            password=form.cleaned_data["password"],
            first_name=form.cleaned_data["full_name"],
            is_active=form.cleaned_data["is_active"],
            is_staff=form.cleaned_data["is_staff"],
        )
        user_company = UserCompany.objects.create(
            user=user,
            company=company,
            is_owner=False,
        )

        UserPermission.objects.create(
            user_company=user_company,
            can_manage_contacts=form.cleaned_data["can_manage_contacts"],
            can_manage_users=form.cleaned_data["can_manage_users"],
            can_manage_products=form.cleaned_data["can_manage_products"],
            can_manage_sectors=form.cleaned_data["can_manage_sectors"],
        )

        UserPreference.objects.create(
            user=user,
            theme="dark",
        )

        messages.success(request, "Usuário criado com sucesso.")
        return redirect("users_list")
    return render(request, "users/form.html", {"form": form, "mode": "create"})


@login_required
def users_edit(request, pk):
    deny = _require_permission(request, "can_manage_users")
    if deny:
        return deny
    company = _get_user_company(request)
    user_link = get_object_or_404(UserCompany, pk=pk, company=company)
    user_obj = user_link.user

    perms, _ = UserPermission.objects.get_or_create(
        user_company=user_link,
        defaults={
            "can_manage_contacts": True,
            "can_manage_users": False,
            "can_manage_products": False,
            "can_manage_sectors": False,
        },
    )

    initial = {
        "full_name": user_obj.first_name,
        "email": user_obj.email,
        "is_active": user_obj.is_active,
        "is_staff": user_obj.is_staff,
        "can_manage_contacts": perms.can_manage_contacts,
        "can_manage_users": perms.can_manage_users,
        "can_manage_products": perms.can_manage_products,
        "can_manage_sectors": perms.can_manage_sectors,
    }
    form = UserUpdateForm(
        request.POST or None,
        initial=initial,
        user_instance=user_obj,
        company=company,
    )

    if request.method == "POST" and form.is_valid():
        user_obj.first_name = form.cleaned_data["full_name"]
        user_obj.email = form.cleaned_data["email"]
        user_obj.is_active = form.cleaned_data["is_active"]
        user_obj.is_staff = form.cleaned_data["is_staff"]

        new_password = form.cleaned_data.get("password")
        if new_password:
            user_obj.set_password(new_password)

        user_obj.save()

        if user_link.is_owner:
            perms.can_manage_contacts = True
            perms.can_manage_users = True
            perms.can_manage_products = True
            perms.can_manage_sectors = True
        else:
            perms.can_manage_contacts = form.cleaned_data["can_manage_contacts"]
            perms.can_manage_users = form.cleaned_data["can_manage_users"]
            perms.can_manage_products = form.cleaned_data["can_manage_products"]
            perms.can_manage_sectors = form.cleaned_data["can_manage_sectors"]
        perms.save()

        messages.success(request, "Usuário atualizado com sucesso.")
        return redirect("users_list")

    return render(
        request,
        "users/form.html",
        {"form": form, "mode": "edit", "user_link": user_link},
    )


@login_required
def users_delete(request, pk):
    deny = _require_permission(request, "can_manage_users")
    if deny:
        return deny
    company = _get_user_company(request)
    user_link = get_object_or_404(UserCompany, pk=pk, company=company)
    user_obj = user_link.user

    if user_link.is_owner:
        messages.error(request, "Você não pode excluir o usuário dono da empresa.")
        return redirect("users_list")

    if request.user == user_obj:
        messages.error(request, "Você não pode excluir o próprio usuário.")
        return redirect("users_list")

    if request.method == "POST":
        user_obj.delete()
        messages.success(request, "Usuário excluído com sucesso.")
        return redirect("users_list")

    return render(request, "users/confirm_delete.html", {"user_link": user_link})


# -------- PRODUTOS --------

@login_required
def products_list(request):
    deny = _require_permission(request, "can_manage_products")
    if deny:
        return deny
    company = _get_user_company(request)
    products = Product.objects.filter(company=company)
    return render(request, "products/list.html", {"products": products})


@login_required
def products_create(request):
    deny = _require_permission(request, "can_manage_products")
    if deny:
        return deny
    company = _get_user_company(request)
    form = ProductForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        product = form.save(commit=False)
        product.company = company
        product.save()
        messages.success(request, "Produto cadastrado com sucesso.")
        return redirect("products_list")
    return render(request, "products/form.html", {"form": form, "mode": "create"})


@login_required
def products_edit(request, pk):
    deny = _require_permission(request, "can_manage_products")
    if deny:
        return deny
    company = _get_user_company(request)
    product = get_object_or_404(Product, pk=pk, company=company)
    form = ProductForm(request.POST or None, instance=product)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Produto atualizado com sucesso.")
        return redirect("products_list")
    return render(
        request,
        "products/form.html",
        {"form": form, "mode": "edit", "product": product},
    )


@login_required
def products_delete(request, pk):
    deny = _require_permission(request, "can_manage_products")
    if deny:
        return deny
    company = _get_user_company(request)
    product = get_object_or_404(Product, pk=pk, company=company)
    if request.method == "POST":
        product.delete()
        messages.success(request, "Produto excluído com sucesso.")
        return redirect("products_list")
    return render(request, "products/confirm_delete.html", {"product": product})


# -------- SETORES --------

@login_required
def sectors_list(request):
    deny = _require_permission(request, "can_manage_sectors")
    if deny:
        return deny
    company = _get_user_company(request)
    sectors = Sector.objects.filter(company=company)
    return render(request, "sectors/list.html", {"sectors": sectors})


@login_required
def sectors_create(request):
    deny = _require_permission(request, "can_manage_sectors")
    if deny:
        return deny
    company = _get_user_company(request)
    form = SectorForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        sector = form.save(commit=False)
        sector.company = company
        sector.save()
        messages.success(request, "Setor cadastrado com sucesso.")
        return redirect("sectors_list")
    return render(request, "sectors/form.html", {"form": form, "mode": "create"})


@login_required
def sectors_edit(request, pk):
    deny = _require_permission(request, "can_manage_sectors")
    if deny:
        return deny
    company = _get_user_company(request)
    sector = get_object_or_404(Sector, pk=pk, company=company)
    form = SectorForm(request.POST or None, instance=sector)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Setor atualizado com sucesso.")
        return redirect("sectors_list")
    return render(
        request,
        "sectors/form.html",
        {"form": form, "mode": "edit", "sector": sector},
    )


@login_required
def sectors_delete(request, pk):
    deny = _require_permission(request, "can_manage_sectors")
    if deny:
        return deny
    company = _get_user_company(request)
    sector = get_object_or_404(Sector, pk=pk, company=company)
    if request.method == "POST":
        sector.delete()
        messages.success(request, "Setor excluído com sucesso.")
        return redirect("sectors_list")
    return render(request, "sectors/confirm_delete.html", {"sector": sector})


# -------- AJUSTES --------

@login_required
def settings_view(request):
    company = _get_user_company(request)

    if request.method == "POST":
        company_form = CompanySettingsForm(
            request.POST,
            request.FILES,
            instance=company,
        )
    else:
        company_form = CompanySettingsForm(instance=company)

    prefs, _ = UserPreference.objects.get_or_create(
        user=request.user,
        defaults={"theme": "dark"},
    )

    if request.method == "POST":
        pref_form = UserPreferenceForm(request.POST, instance=prefs)

        if company_form.is_valid() and pref_form.is_valid():
            company_form.save()
            pref_form.save()
            messages.success(request, "Ajustes salvos com sucesso.")
            return redirect("settings")
    else:
        pref_form = UserPreferenceForm(instance=prefs)

    return render(
        request,
        "settings/index.html",
        {
            "company_form": company_form,
            "pref_form": pref_form,
        },
    )