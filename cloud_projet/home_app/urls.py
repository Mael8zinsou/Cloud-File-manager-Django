from django.urls import path
from . import views

app_name = 'home_app'  # utilisation de namespace


urlpatterns = [
    #path('folder/', views.folder_list, name='folder_list'),
    #path('folder/<int:folder_id>', views.folder_list_id, name='folder_list_id'),
    #path('upload/', views.upload_file, name='upload_file'),
    path('create/', views.create_folder, name='create_folder'),
    path('create/<int:folder_id>/', views.create_folder, name='create_folder_with_id'),
    path('folders/<int:folder_id>/', views.folder_list, name='folder_list_with_id'),
    path('folders/', views.folder_list, name='folder_list'),
    path('group/folders/<int:group_id>/<int:folder_id>', views.folder_list, name='group_list_with_id'),
    path('group/folder/<int:group_id>', views.folder_list, name='group_list'),
    
    path('group/create/<int:group_id>', views.create_folder, name='group_create_folder'),
    path('group/create/<int:group_id>/<int:folder_id>', views.create_folder, name='group_create_folder_with_id'),
    
    #path('delete/<int:file_id>/', views.delete_file, name='delete_file'),
    path('delete/<int:group_id>/<int:file_id>/', views.delete_file, name='delete_file'),
    path('delete/<int:file_id>/', views.delete_file, name='delete_file_user'),
    
    path('view/<int:file_id>/', views.view_file, name='view_file'),
    path('view/<int:group_id>/<int:file_id>/', views.view_file, name='view_file_group'),
    #path('delete_fold/<int:folder_id>/', views.delete_folder, name='delete_folders'),
    path('delete_fold/<int:group_id>/<int:folder_id>/', views.delete_folder, name='delete_folders'),
    path('delete_fold/<int:folder_id>/', views.delete_folder, name='delete_folders_user'),
    
    # ne pas oublier de verifier si la taille est suffisante pour copier un dosssier
    path('move_folder/<int:folder_id>/', views.move_folder, name='move_folder'),
    path('move_folder/<int:group_id>/<int:folder_id>/', views.move_folder, name='move_folder_group'),
    
    path('copy_folder/<int:folder_id>/', views.copy_folder, name='copy_folder'),
    path('copy_folder/<int:group_id>/<int:folder_id>/', views.copy_folder, name='copy_folder_group'),
    
    path('move_file/<int:file_id>/', views.move_file, name='move_file'),
    path('move_file/<int:group_id>/<int:file_id>/', views.move_file, name='move_file_group'),
    
    
    path('copy_file/<int:file_id>/', views.copy_file, name='copy_file'),
    path('copy_file/<int:group_id>/<int:file_id>/', views.copy_file, name='copy_file_group'),
]