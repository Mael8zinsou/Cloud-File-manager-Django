from django.urls import path

from . import views

app_name = 'auth_app'

urlpatterns = [
    path('connexion', views.connexion, name='connexion'),
    path('deconnexion', views.deconnexion, name='deconnexion'),
    path('create-group/', views.create_group, name='create_group'),
    path('add-member/', views.add_user_to_group, name='add_members'),
    path('groupe-manager/', views.list_group_users, name='group_manager'),
    path('remove-member/<int:user_id>/<int:group_id>', views.remove_user_from_group, name='remove_members'),
    path('', views.inscription, name='inscription')
]