from django.conf import settings
from django.db import models


def company_logo_upload_path(instance, filename):
    # arquivos em media/company_logos/<company_id>/<filename>
    return f"company_logos/{instance.id}/{filename}"


class Company(models.Model):
    name = models.CharField("Nome da empresa", max_length=255)
    cnpj = models.CharField("CNPJ", max_length=18, blank=True, null=True)
    email = models.EmailField("E-mail", unique=True)
    phone = models.CharField("Telefone", max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Endereço da empresa
    cep = models.CharField("CEP", max_length=9, blank=True, null=True)
    address = models.CharField("Endereço", max_length=255, blank=True, null=True)
    number = models.CharField("Número", max_length=20, blank=True, null=True)
    district = models.CharField("Bairro", max_length=100, blank=True, null=True)
    city = models.CharField("Cidade", max_length=100, blank=True, null=True)
    uf = models.CharField("UF", max_length=2, blank=True, null=True)

    # Ajustes
    logo = models.ImageField(
        "Logo da empresa",
        upload_to=company_logo_upload_path,
        blank=True,
        null=True,
    )
    whatsapp_default_message = models.TextField(
        "Mensagem padrão do WhatsApp",
        blank=True,
        null=True,
        help_text="Mensagem sugerida ao iniciar uma conversa pelo WhatsApp.",
    )

    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"

    def __str__(self):
        return self.name


class UserCompany(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="company_link",
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="users",
    )
    is_owner = models.BooleanField(
        "Dono da empresa",
        default=False,
        help_text="Usuário principal, não pode perder acesso.",
    )

    class Meta:
        verbose_name = "Usuário da empresa"
        verbose_name_plural = "Usuários da empresa"
        ordering = ["company", "user__username"]

    def __str__(self):
        return f"{self.user.username} - {self.company.name}"


class Contact(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="contacts",
        verbose_name="Empresa",
    )

    document = models.CharField("CPF/CNPJ", max_length=20, blank=True, null=True)

    display_name = models.CharField(
        "Nome do cliente / Nome fantasia",
        max_length=255,
    )
    legal_name = models.CharField(
        "Razão social",
        max_length=255,
        blank=True,
        null=True,
    )

    phone = models.CharField("Telefone", max_length=20, blank=True, null=True)
    email = models.EmailField("E-mail do contato", blank=True, null=True)
    is_active = models.BooleanField("Ativo", default=True)

    cep = models.CharField("CEP", max_length=9, blank=True, null=True)
    address = models.CharField("Endereço", max_length=255, blank=True, null=True)
    number = models.CharField("Número", max_length=20, blank=True, null=True)
    district = models.CharField("Bairro", max_length=100, blank=True, null=True)
    city = models.CharField("Cidade", max_length=100, blank=True, null=True)
    uf = models.CharField("UF", max_length=2, blank=True, null=True)

    is_client = models.BooleanField("Cliente", default=True)
    is_supplier = models.BooleanField("Fornecedor", default=False)
    is_partner = models.BooleanField("Parceiro", default=False)
    is_employee = models.BooleanField("Funcionário", default=False)
    is_other = models.BooleanField("Outros", default=False)
    is_seller = models.BooleanField("Vendedor", default=False)

    commission = models.DecimalField(
        "Comissão (%)",
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Informe a comissão em porcentagem, ex.: 5,00 para 5%.",
    )

    notes = models.TextField("Observações", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Contato"
        verbose_name_plural = "Contatos"
        ordering = ["display_name"]

    def __str__(self):
        return self.display_name


class Product(models.Model):
    UNIT_CHOICES = [
        ("M2", "m²"),
        ("UN", "Unidade"),
    ]

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name="Empresa",
    )

    name = models.CharField("Nome do produto", max_length=255)
    unit = models.CharField(
        "Unidade de medida",
        max_length=3,
        choices=UNIT_CHOICES,
        default="M2",
    )
    price = models.DecimalField(
        "Valor de venda",
        max_digits=12,
        decimal_places=2,
    )
    cost_price = models.DecimalField(
        "Valor de custo",
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
    )
    is_active = models.BooleanField("Ativo", default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def profit_value(self):
        if self.cost_price is None:
            return None
        return self.price - self.cost_price

    @property
    def profit_percent(self):
        if self.cost_price is None or not self.price:
            return None
        profit = self.price - self.cost_price
        return (profit / self.price) * 100


class Sector(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="sectors",
        verbose_name="Empresa",
    )
    name = models.CharField("Nome do setor", max_length=150)
    is_active = models.BooleanField("Ativo", default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Setor"
        verbose_name_plural = "Setores"
        ordering = ["name"]

    def __str__(self):
        return self.name


class UserPermission(models.Model):
    """
    Permissões por usuário dentro da empresa.
    """
    user_company = models.OneToOneField(
        UserCompany,
        on_delete=models.CASCADE,
        related_name="permissions",
        verbose_name="Usuário da empresa",
    )
    can_manage_contacts = models.BooleanField("Pode gerenciar contatos", default=True)
    can_manage_users = models.BooleanField("Pode gerenciar usuários", default=False)
    can_manage_products = models.BooleanField("Pode gerenciar produtos", default=False)
    can_manage_sectors = models.BooleanField("Pode gerenciar setores", default=False)

    class Meta:
        verbose_name = "Permissão do usuário"
        verbose_name_plural = "Permissões dos usuários"

    def __str__(self):
        return f"Permissões de {self.user_company.user.username}"


class UserPreference(models.Model):
    THEME_CHOICES = [
        ("dark", "Escuro"),
        ("light", "Claro"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="preferences",
    )
    theme = models.CharField(
        "Tema",
        max_length=10,
        choices=THEME_CHOICES,
        default="dark",
    )

    class Meta:
        verbose_name = "Preferência do usuário"
        verbose_name_plural = "Preferências dos usuários"

    def __str__(self):
        return f"Preferências de {self.user.username}"