from django import forms
from django.contrib.auth.models import User

from .models import (
    Company,
    Contact,
    Product,
    Sector,
    UserCompany,
    UserPermission,
    UserPreference,
)


class CompanySignUpForm(forms.Form):
    company_name = forms.CharField(label="Nome da empresa", max_length=255)
    company_email = forms.EmailField(label="E-mail da empresa")
    company_phone = forms.CharField(label="Telefone", max_length=20, required=False)
    cnpj = forms.CharField(label="CNPJ", max_length=18, required=False)

    admin_name = forms.CharField(label="Seu nome", max_length=150)
    admin_email = forms.EmailField(label="Seu e-mail")
    username = forms.CharField(label="Usuário de acesso", max_length=150)

    password = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput,
        min_length=6,
    )
    password_confirm = forms.CharField(
        label="Confirmar senha",
        widget=forms.PasswordInput,
        min_length=6,
    )

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Este nome de usuário já está em uso.")
        return username

    def clean_admin_email(self):
        email = self.cleaned_data["admin_email"]
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Já existe um usuário com este e-mail.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm = cleaned_data.get("password_confirm")
        if password and confirm and password != confirm:
            self.add_error("password_confirm", "As senhas não coincidem.")
        return cleaned_data


class LoginForm(forms.Form):
    username = forms.CharField(label="Usuário")
    password = forms.CharField(label="Senha", widget=forms.PasswordInput)


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = [
            "document",
            "display_name",
            "legal_name",
            "phone",
            "email",
            "is_active",
            "cep",
            "address",
            "number",
            "district",
            "city",
            "uf",
            "is_client",
            "is_supplier",
            "is_partner",
            "is_employee",
            "is_other",
            "is_seller",
            "commission",
            "notes",
        ]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "unit", "cost_price", "price", "is_active"]
        labels = {
            "name": "Nome do produto",
            "unit": "Unidade de medida",
            "cost_price": "Valor de custo",
            "price": "Valor de venda",
            "is_active": "Ativo",
        }


class SectorForm(forms.ModelForm):
    class Meta:
        model = Sector
        fields = ["name", "is_active"]
        labels = {
            "name": "Nome do setor",
            "is_active": "Ativo",
        }


# -------- AJUSTES --------

class CompanySettingsForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = [
            "name",
            "cnpj",
            "email",
            "phone",
            "cep",
            "address",
            "number",
            "district",
            "city",
            "uf",
            "logo",
            "whatsapp_default_message",
        ]
        labels = {
            "name": "Nome da empresa",
            "cnpj": "CNPJ",
            "email": "E-mail",
            "phone": "Telefone",
            "cep": "CEP",
            "address": "Endereço",
            "number": "Número",
            "district": "Bairro",
            "city": "Cidade",
            "uf": "UF",
            "logo": "Logo da empresa",
            "whatsapp_default_message": "Mensagem padrão do WhatsApp",
        }
        widgets = {
            "whatsapp_default_message": forms.Textarea(attrs={"rows": 3}),
        }


class UserPreferenceForm(forms.ModelForm):
    class Meta:
        model = UserPreference
        fields = ["theme"]
        labels = {
            "theme": "Tema",
        }


# -------- USUÁRIOS --------

class UserCreateForm(forms.Form):
    full_name = forms.CharField(label="Nome completo", max_length=150)
    email = forms.EmailField(label="E-mail")
    username = forms.CharField(label="Usuário", max_length=150)

    is_active = forms.BooleanField(label="Ativo", required=False, initial=True)
    is_staff = forms.BooleanField(label="Permitir acesso ao admin (staff)", required=False)

    can_manage_contacts = forms.BooleanField(
        label="Pode gerenciar contatos",
        required=False,
        initial=True,
    )
    can_manage_users = forms.BooleanField(
        label="Pode gerenciar usuários",
        required=False,
        initial=False,
    )
    can_manage_products = forms.BooleanField(
        label="Pode gerenciar produtos",
        required=False,
        initial=False,
    )
    can_manage_sectors = forms.BooleanField(
        label="Pode gerenciar setores",
        required=False,
        initial=False,
    )

    password = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput,
        min_length=6,
    )
    password_confirm = forms.CharField(
        label="Confirmar senha",
        widget=forms.PasswordInput,
        min_length=6,
    )

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop("company", None)
        super().__init__(*args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Este nome de usuário já está em uso.")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"]
        if self.company:
            exists_same_company = UserCompany.objects.filter(
                company=self.company,
                user__email=email,
            ).exists()
            if exists_same_company:
                raise forms.ValidationError(
                    "Já existe um usuário com este e-mail nesta empresa."
                )
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm = cleaned_data.get("password_confirm")
        if password and confirm and password != confirm:
            self.add_error("password_confirm", "As senhas não coincidem.")
        return cleaned_data


class UserUpdateForm(forms.Form):
    full_name = forms.CharField(label="Nome completo", max_length=150)
    email = forms.EmailField(label="E-mail")
    is_active = forms.BooleanField(label="Ativo", required=False)
    is_staff = forms.BooleanField(label="Permitir acesso ao admin (staff)", required=False)

    can_manage_contacts = forms.BooleanField(
        label="Pode gerenciar contatos",
        required=False,
    )
    can_manage_users = forms.BooleanField(
        label="Pode gerenciar usuários",
        required=False,
    )
    can_manage_products = forms.BooleanField(
        label="Pode gerenciar produtos",
        required=False,
    )
    can_manage_sectors = forms.BooleanField(
        label="Pode gerenciar setores",
        required=False,
    )

    password = forms.CharField(
        label="Nova senha (opcional)",
        widget=forms.PasswordInput,
        required=False,
        min_length=6,
    )
    password_confirm = forms.CharField(
        label="Confirmar nova senha",
        widget=forms.PasswordInput,
        required=False,
        min_length=6,
    )

    def __init__(self, *args, **kwargs):
        self.user_instance = kwargs.pop("user_instance", None)
        self.company = kwargs.pop("company", None)
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data["email"]
        if not self.company:
            return email

        qs = UserCompany.objects.filter(
            company=self.company,
            user__email=email,
        )
        if self.user_instance:
            qs = qs.exclude(user=self.user_instance)
        if qs.exists():
            raise forms.ValidationError(
                "Já existe um usuário com este e-mail nesta empresa."
            )
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm = cleaned_data.get("password_confirm")
        if password or confirm:
            if password != confirm:
                self.add_error("password_confirm", "As senhas não coincidem.")
        return cleaned_data