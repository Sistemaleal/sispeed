from django.contrib import admin
from django.urls import path

from core import views as core_views

urlpatterns = [
    path("admin/", admin.site.urls),

    path("", core_views.login_view, name="login"),
    path("logout/", core_views.logout_view, name="logout"),
    path("cadastro-empresa/", core_views.company_signup_view, name="company_signup"),
    path("dashboard/", core_views.dashboard_view, name="dashboard"),

    # Contatos
    path("contatos/", core_views.contacts_list, name="contacts_list"),
    path("contatos/novo/", core_views.contacts_create, name="contacts_create"),
    path("contatos/<int:pk>/editar/", core_views.contacts_edit, name="contacts_edit"),
    path("contatos/<int:pk>/excluir/", core_views.contacts_delete, name="contacts_delete"),

    # Usuários
    path("usuarios/", core_views.users_list, name="users_list"),
    path("usuarios/novo/", core_views.users_create, name="users_create"),
    path("usuarios/<int:pk>/editar/", core_views.users_edit, name="users_edit"),
    path("usuarios/<int:pk>/excluir/", core_views.users_delete, name="users_delete"),

    # Produtos
    path("produtos/", core_views.products_list, name="products_list"),
    path("produtos/novo/", core_views.products_create, name="products_create"),
    path("produtos/<int:pk>/editar/", core_views.products_edit, name="products_edit"),
    path("produtos/<int:pk>/excluir/", core_views.products_delete, name="products_delete"),

    # Setores
    path("setores/", core_views.sectors_list, name="sectors_list"),
    path("setores/novo/", core_views.sectors_create, name="sectors_create"),
    path("setores/<int:pk>/editar/", core_views.sectors_edit, name="sectors_edit"),
    path("setores/<int:pk>/excluir/", core_views.sectors_delete, name="sectors_delete"),

    # Ajustes
    path("ajustes/", core_views.settings_view, name="settings"),
]