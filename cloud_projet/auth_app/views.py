from django.shortcuts import render, redirect, get_object_or_404
from .form import CustomUserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Permission, User
from .form import GroupCreateForm
from django.contrib.auth.decorators import permission_required
#from django.contrib.auth.models import Group
from .models import Group, Membership
#from .models import CustomGroup, Membership


def inscription(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('auth_app:connexion')
    else:
        form = CustomUserCreationForm()
    return render(request, 'auth_app/inscription.html', {'form': form}) # => templates/auth_app/inscription.html


def connexion(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home_app:folder_list')
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    return render(request, 'auth_app/connexion.html')

def deconnexion(request):
    logout(request)
    return redirect('auth_app:connexion')

@login_required
def create_group(request):
    if request.method == 'POST':
        form = GroupCreateForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.owner = request.user
            group.save()
            
            # codenames = [
            #     'add_file',
            #     'delete_file',
            #     'view_file',
            #     'add_folder',
            #     'delete_folder',
            #     'view_folder',
            # ]

            # permissions = Permission.objects.filter(codename__in=codenames)
            # group.permissions.add(*permissions)
            
            # Ajouter le créateur au groupe
            # request.user.groups.add(group)
            
            # # Ajouter le créateur au groupe en utilisant la classe Membership
            # # membership = Membership.objects.create(user=request.user, group=group, is_admin=True)
            # # membership.save()
            
            # # Définir les codenames des permissions à assigner
            # codenames_owner = [
            #     'add_user',
            #     'change_user',
            #     'delete_user',
            #     'view_user',
                
            #     'add_group',
            #     'change_group',
            #     'delete_group',
            #     'view_group',
                
            # ]
            
            # Récupérer les permissions correspondantes
            # required_permissions = Permission.objects.filter(codename__in=codenames_owner)
            
            # print(required_permissions)
            
            # Assigner les permissions à l'utilisateur
            #request.user.user_permissions.add(*required_permissions)
            
            # Add the group creator using the Membership class
            membership = Membership.objects.create(user=request.user, group=group)
            membership.save()
            
            return redirect("home_app:folder_list")
    else:
        form = GroupCreateForm()
    return render(request, 'auth_app/create_group.html', {'form': form})





# def add_user_to_group(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         group_name = request.POST.get('group_name')
        
#         user = get_object_or_404(User, username=username)
#         group = get_object_or_404(CustomGroup, name=group_name)
        
#         user.groups.add(group)
#         messages.success(request, f'User {username} added to group {group_name}.', extra_tags="success")
#         return redirect('home_app:folder_list')
    
    
#     groups = request.user.groups.all()
#     #users = User.objects.all()
#     return render(request, 'auth_app/add_members.html', {'groups': groups})


# def add_user_to_group(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         group_name = request.POST.get('group_name')
        
#         user = get_object_or_404(User, username=username)
#         group = get_object_or_404(Group, name=group_name)
        
#         #user.groups.add(group)
        
#         # Ajouter l'utilisateur à la classe Membership
#         membership = Membership.objects.create(user=user, group=group)
#         membership.save()
        
#         messages.success(request, f'User {username} added to group {group_name}.', extra_tags="success")
#         return redirect('home_app:folder_list')
    
#     groups = Group.objects.filter(owner=request.user)
#     return render(request, 'auth_app/add_members.html', {'groups': groups})


def add_user_to_group(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        group_name = request.POST.get('group_name')
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, f'User {username} does not exist.', extra_tags="danger")
            return redirect('auth_app:add_members')
        
        group = get_object_or_404(Group, name=group_name)
        
        membership = Membership.objects.create(user=user, group=group)
        membership.save()
        
        messages.success(request, f'User {username} added to group {group_name}.', extra_tags="success")
        return redirect('home_app:folder_list')
    
    groups = Group.objects.filter(owner=request.user)
    return render(request, 'auth_app/add_members.html', {'groups': groups})


#@permission_required('auth.view_group', raise_exception=True)
def list_group_users(request):
    # Récupérer les groupes dont l'utilisateur actuel est le propriétaire
    groups = Group.objects.filter(owner=request.user)  # Assurez-vous d'avoir un champ 'created_by' dans le modèle Group
    
    
    # Préparer une liste avec les utilisateurs de chaque groupe
    groups_with_users = []
    for group in groups:
        users = group.members.all()
        groups_with_users.append({
            'group': group,
            'users': users
        })
        print(group)
        print(users)
    
    return render(request, 'auth_app/group_manager.html', {'groups_with_users': groups_with_users})

# def list_group_users(request):
#     # Récupérer les groupes auxquels l'utilisateur actuel appartient
#     memberships = Membership.objects.filter(user=request.user)

#     print(memberships)
#     # Préparer une liste avec les utilisateurs de chaque groupe
#     groups_with_users = []
#     for membership in memberships:
#         group = membership.group
#         users = membership.user
#         print(group)
#         groups_with_users.append({
#             'group': group,
#             'users': users
#         })
    
    # return render(request, 'auth_app/group_manager.html', {'groups_with_users': groups_with_users})
    

@login_required
def remove_user_from_group(request, user_id, group_id):
    if request.method == 'POST':
        group = get_object_or_404(Group, id=group_id, owner=request.user)
        user = get_object_or_404(User, id=user_id)

        
        membership = Membership.objects.filter(user=user, group=group)
        for m in membership:
            print(f"User: {m.user.username}, Group: {m.group.name}")

        membership.delete()
        messages.success(request, f'User {user.username} removed from group {group.name}.', extra_tags="success")

        return redirect('auth_app:group_manager')

    groups = Group.objects.filter(owner=request.user)
    return render(request, 'auth_app/group_manager.html', {'groups': groups})
    