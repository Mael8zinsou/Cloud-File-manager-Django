from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.clickjacking import xframe_options_exempt
from django.http import HttpResponse

from .models import File, Folder
from .form import FolderForm
from auth_app.models import Group, Membership
import os

mapping = {
    '.png': 'Images', '.jpeg': 'Images', '.jpg': 'Images', '.bmp': 'Images', '.svg': 'Images',
    '.tiff': 'Images', '.gif': 'Images', '.eps': 'Images', '.psd': 'Images', '.ai': 'Images',

    '.docx': 'Documents', '.pdf': 'Documents', '.txt': 'Documents', '.doc': 'Documents',
    '.ppt': 'Documents', '.pptx': 'Documents', '.xls': 'Documents', '.xlsx': 'Documents',
    '.csv': 'Documents', '.rtf': 'Documents', '.html': 'Documents', '.htm': 'Documents',
    '.css': 'Documents', '.js': 'Documents', '.json': 'Documents', '.xml': 'Documents',
    '.md': 'Documents', '.sql': 'Documents', '.ts': 'Documents', '.yaml': 'Documents',
    '.yml': 'Documents', '.ini': 'Documents', '.woff': 'Documents', '.woff2': 'Documents',
    '.ttf': 'Documents', '.eot': 'Documents', '.otf': 'Documents',

    '.mp3': 'Media', '.wav': 'Media', '.flac': 'Media', '.aac': 'Media', '.ogg': 'Media',
    '.wma': 'Media', '.m4a': 'Media', '.mp4': 'Media', '.avi': 'Media', '.mkv': 'Media',
    '.mov': 'Media', '.wmv': 'Media', '.flv': 'Media', '.webm': 'Media',

    '.exe': 'Others', '.dll': 'Others', '.apk': 'Others', '.dmg': 'Others', '.iso': 'Others',
    '.py': 'Others', '.java': 'Others', '.c': 'Others', '.cpp': 'Others', '.cs': 'Others',
    '.php': 'Others', '.rb': 'Others', '.go': 'Others', '.swift': 'Others', '.kt': 'Others',
    '.sh': 'Others', '.bat': 'Others', '.ps1': 'Others', '.pfg': 'Others', '.log': 'Others',
    '.zip': 'Others', '.rar': 'Others', '.7z': 'Others', '.tar': 'Others', '.gz': 'Others',
    '.xz': 'Others', '.ipa': 'Others', '.deb': 'Others', '.rpm': 'Others'
}

@login_required
def folder_list(request, group_id=None, folder_id=None):
    if group_id:
        current_group = get_object_or_404(Group, id=group_id)
    else:
        current_group = None

    if folder_id:
        if current_group:
            current_folder = get_object_or_404(Folder, id=folder_id, group=current_group)
            files = File.objects.filter(folder=current_folder, group=current_group)
            subfolders = Folder.objects.filter(parent_folder=current_folder, group=current_group)
        else:
            current_folder = get_object_or_404(Folder, id=folder_id, owner=request.user)
            files = File.objects.filter(owner=request.user, folder=current_folder, group__isnull=True)
            subfolders = Folder.objects.filter(owner=request.user, parent_folder=current_folder, group__isnull=True)
    else:
        current_folder = None
        if current_group:
            files = File.objects.filter(folder__isnull=True, group=current_group)
            subfolders = Folder.objects.filter(parent_folder__isnull=True, group=current_group)
        else:
            files = File.objects.filter(owner=request.user, folder__isnull=True, group__isnull=True)
            subfolders = Folder.objects.filter(owner=request.user, parent_folder__isnull=True, group__isnull=True)

    size = sum_by_type(request)
    total_size = calculate_total_size(size)

    ###################################################################################   Upload a file
    if total_size["unformatted"] <= 100e6:
        if request.method == 'POST' and 'file' in request.FILES:
            uploaded_file = request.FILES['file']
            if uploaded_file.size > 40e6:
                messages.error(request, 'File size exceeds the 40 MB limit.', extra_tags='danger')
                return redirect("home_app:folder_list")
            new_file = File(
                owner=request.user,
                folder=current_folder,
                group=current_group,
                name=uploaded_file.name,
                content=uploaded_file.read()
            )
            new_file.save()
            size = sum_by_type(request)
            total_size = calculate_total_size(size)
            return redirect("home_app:folder_list")
    else:
        messages.error(request, 'You have access to 100 MB Only', extra_tags='danger')
        return redirect("home_app:folder_list")
    ###################################################################################
    
    parent_fold = []
    stock_fold = current_folder
    while stock_fold is not None and stock_fold.parent_folder is not None:
        stock_fold = stock_fold.parent_folder
        parent_fold.append(stock_fold)
    parent_fold.reverse()

    groups_owner = Group.objects.filter(owner=request.user)
    user_memberships = Membership.objects.filter(user=request.user)
    
    print(files)
    print(folder_id, group_id)
    context = {
        'folders': subfolders,
        'files': files,
        'size': size,
        'current_folder': current_folder,
        'current_group': current_group,
        'total_size': total_size,
        'parent_fold': parent_fold,
        "groups_owner": groups_owner,
        "user_memberships": user_memberships
    }
    return render(request, 'home_app/home_list.html', context)

@login_required
def create_folder(request, group_id=None, folder_id=None):
    if group_id:
        current_group = get_object_or_404(Group, id=group_id)
    else:
        current_group = None

    if folder_id:
        if current_group:
            current_folder = get_object_or_404(Folder, id=folder_id, group=current_group)
        else:
            current_folder = get_object_or_404(Folder, id=folder_id, owner=request.user)
    else:
        current_folder = None

    if request.method == 'POST':
        form = FolderForm(request.POST)
        if form.is_valid():
            folder = form.save(commit=False)
            folder.owner = request.user
            folder.parent_folder = current_folder
            folder.group = current_group
            folder.save()
            if folder.parent_folder:
                if group_id:
                    return redirect('home_app:group_list_with_id', group_id=group_id, folder_id=folder.parent_folder.id)
                else:
                    return redirect('home_app:folder_list_with_id', folder_id=folder.parent_folder.id)
            else:
                if group_id:
                    return redirect('home_app:group_list', group_id=group_id)
                else:
                    return redirect('home_app:folder_list')
    else:
        form = FolderForm()
    return render(request, 'home_app/create_folder.html', {'form': form, 'current_folder': current_folder, 'current_group': current_group})

def sum_by_type(request):
    totals = {}
    counts = {}
    files_size = File.objects.filter(owner=request.user)
    for file in files_size:
        file_type = mapping.get(file.extension_file.lower(), 'Others')
        if file_type not in totals:
            totals[file_type] = 0
            counts[file_type] = 0
        totals[file_type] += file.size()
        counts[file_type] += 1
    result = {}
    for Type in totals.keys():
        result[Type] = {
            'total_size': formatted_size(totals[Type]),
            'count': counts[Type],
            'total_unformatted': totals[Type]
        }
    return result

def formatted_size(value):
    size = value
    for unit in ['Octets', 'Ko', 'Mo']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return size




def calculate_total_size(result):
    totals = 0
    for type_ in result:
        totals += result[type_]["total_unformatted"]
    
    percentages = {}
    for type_ in result:
        percentage = (result[type_]["total_unformatted"] / 100e6) * 100
        percentages[type_] = round(percentage, 1)
        result[type_]["percentage"] = round(percentage, 1)
    
    return {
        'formatted_total': formatted_size(totals),
        'percentages': percentages,
        'unformatted' : totals
    }
    

def delete_file(request, group_id=None, file_id=None):
    if group_id:
        current_group = get_object_or_404(Group, id=group_id)
        file = get_object_or_404(File, id=file_id, group=current_group)
    else:
        file = get_object_or_404(File, id=file_id, owner=request.user)
    folder = file.folder
    file.delete()
    messages.success(request, 'File deleted successfully.', extra_tags="success")
    if group_id and folder:
        return redirect('home_app:group_list_with_id', group_id=group_id, folder_id=folder.id)
    elif group_id:
        return redirect('home_app:group_list', group_id=group_id)
    elif folder:
        return redirect('home_app:folder_list_with_id', folder_id=folder.id)
    else:
        return redirect('home_app:folder_list')

@xframe_options_exempt
def view_file(request, group_id=None, file_id=None):
    if group_id:
        current_group = get_object_or_404(Group, id=group_id)
        file = get_object_or_404(File, id=file_id, group=current_group)
    else:
        file = get_object_or_404(File, id=file_id, owner=request.user)
    extension = f".{file.name.split('.')[-1].lower()}"
    content_types = {
        '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
        '.gif': 'image/gif', '.bmp': 'image/bmp', '.txt': 'text/plain; charset=utf-8',
        '.pdf': 'application/pdf', '.html': 'text/html; charset=utf-8', '.htm': 'text/html; charset=utf-8',
        '.mp4': 'video/mp4', '.avi': 'video/x-msvideo', '.wmv': 'video/x-ms-wmv', '.flv': 'video/x-flv', '.webm': 'video/webm',
    }

    content_type = content_types.get(extension)
    if content_type:
        return HttpResponse(file.content, content_type=content_type)
    messages.error(request, "Unsupported file type.")
    return redirect('home_app:folder_list')

def delete_folder(request, group_id=None, folder_id=None):
    if group_id:
        current_group = get_object_or_404(Group, id=group_id)
        folder = get_object_or_404(Folder, id=folder_id, group=current_group)
    else:
        folder = get_object_or_404(Folder, id=folder_id, owner=request.user)
    parent_folder = folder.parent_folder
    folder.delete()
    messages.success(request, 'Folder deleted successfully.', extra_tags="success")
    if folder.parent_folder:
        if group_id:
            return redirect('home_app:group_list_with_id', group_id=group_id, folder_id=folder.parent_folder.id)
        else:
            return redirect('home_app:folder_list_with_id', folder_id=folder.parent_folder.id)
    else:
        if group_id:
            return redirect('home_app:group_list', group_id=group_id)
        else:
            return redirect('home_app:folder_list')




@login_required
def move_folder(request, group_id=None, folder_id=None):
    if group_id:
        current_group = get_object_or_404(Group, id=group_id)
        folder = get_object_or_404(Folder, id=folder_id, group=current_group)
    else:
        current_group = None
        folder = get_object_or_404(Folder, id=folder_id, owner=request.user)
    if request.method == 'POST':
        new_parent_folder_id = request.POST.get('new_parent_folder_id')
        print("C'est ici", new_parent_folder_id)
        if new_parent_folder_id:
            if current_group:
                new_parent_folder = get_object_or_404(Folder, id=new_parent_folder_id, group=current_group)
            else:
                new_parent_folder = get_object_or_404(Folder, id=new_parent_folder_id, owner=request.user)
            folder.parent_folder = new_parent_folder
            folder.save()
            if current_group:
                return redirect('home_app:group_list_with_id', group_id=group_id, folder_id=new_parent_folder.id)
            else:
                return redirect('home_app:folder_list_with_id', folder_id=new_parent_folder.id)
        else:
            messages.error(request, 'Please select a valid parent folder.', extra_tags='danger')
    if current_group:
        folders = Folder.objects.filter(group=current_group).exclude(id=folder.id)
        #folders = Folder.objects.filter(group=current_group)
    else:
        folders = Folder.objects.filter(owner=request.user).exclude(id=folder.id)
        #folders = Folder.objects.filter(owner=request.user)
    return render(request, 'home_app/move_folder.html', {
        'folder': folder,
        'folders': folders,
        'current_group': current_group
    })



# @login_required
# def copy_folder(request, folder_id):
#     folder = get_object_or_404(Folder, id=folder_id)
#     print("on est ici")
#     if request.method == 'POST':
#         new_parent_folder_id = request.POST.get('new_parent_folder_id')
#         new_parent_folder = get_object_or_404(Folder, id=new_parent_folder_id)
#         copy_subfolders_and_files(folder, new_parent_folder)
#         return redirect('home_app:folder_list')
#     folders = Folder.objects.filter(owner=request.user).exclude(id=folder.id)  # Filter by owner and exclude the folder itself
#     return render(request, 'home_app/copy_folder.html', {'folder': folder, 'folders': folders})


@login_required
def copy_folder(request, group_id=None, folder_id=None):
    if group_id:
        current_group = get_object_or_404(Group, id=group_id)
        folder = get_object_or_404(Folder, id=folder_id, group=current_group)
    else:
        current_group = None
        folder = get_object_or_404(Folder, id=folder_id, owner=request.user)

    if request.method == 'POST':
        new_parent_folder_id = request.POST.get('new_parent_folder_id')
        if new_parent_folder_id:
            if current_group:
                new_parent_folder = get_object_or_404(Folder, id=new_parent_folder_id, group=current_group)
            else:
                new_parent_folder = get_object_or_404(Folder, id=new_parent_folder_id, owner=request.user)
                
            size = sum_by_type(request)
            total_size = calculate_total_size(size)
            folder_size = get_folder_total_size(folder)
            if total_size["unformatted"] + folder_size > 100e6:
                messages.error(request, 'Not enough space on your drive.', extra_tags='danger')
                if group_id:
                    return redirect('home_app:copy_folder_group', group_id=group_id, folder_id=folder_id)
                else:
                    return redirect('home_app:copy_folder', folder_id=folder_id)
                
            copy_subfolders_and_files(folder, new_parent_folder)
            
            if current_group:
                return redirect('home_app:group_list_with_id', group_id=group_id, folder_id=new_parent_folder.id)
            else:
                return redirect('home_app:folder_list_with_id', folder_id=new_parent_folder.id)
        else:
            messages.error(request, 'Please select a valid target folder.', extra_tags='danger')

    if current_group:
        folders = Folder.objects.filter(group=current_group).exclude(id=folder.id)
    else:
        folders = Folder.objects.filter(owner=request.user).exclude(id=folder.id)

    return render(request, 'home_app/copy_folder.html', {'folder': folder, 'folders': folders, 'current_group': current_group})

def get_folder_total_size(folder):
    total_size = 0
    for file in folder.files.all():
        total_size += file.size()
    for subfolder in folder.subfolders.all():
        total_size += get_folder_total_size(subfolder)
    return total_size

def copy_subfolders_and_files(source_folder, target_folder):
    for file in source_folder.files.all():
        filename, file_extension = os.path.splitext(file.name)
        new_file = File(
            name=f"{filename}-Copy{file_extension}",
            content=file.content,
            owner=file.owner,
            folder=target_folder,
            group=target_folder.group,
            created_at=file.created_at,
        )
        new_file.save()
    for subfolder in source_folder.subfolders.all():
        new_subfolder = Folder(
            name=f"{subfolder.name} - Copy",
            owner=subfolder.owner,
            group=target_folder.group,
            parent_folder=target_folder,
            created_at=subfolder.created_at,
        )
        new_subfolder.save()
        copy_subfolders_and_files(subfolder, new_subfolder)
        
        
        
        
        
# @login_required
# def move_file(request, file_id):
#     file = get_object_or_404(File, id=file_id)
#     if request.method == 'POST':
#         new_folder_id = request.POST.get('new_folder_id')
#         new_folder = get_object_or_404(Folder, id=new_folder_id, owner=request.user)
#         file.folder = new_folder
#         file.save()
#         return redirect('home_app:folder_list')
#     folders = Folder.objects.filter(owner=request.user)
#     return render(request, 'home_app/move_file.html', {'file': file, 'folders': folders})

@login_required
def move_file(request, group_id=None, file_id=None):
    if group_id:
        current_group = get_object_or_404(Group, id=group_id)
        file = get_object_or_404(File, id=file_id, group=current_group)
    else:
        current_group = None
        file = get_object_or_404(File, id=file_id, owner=request.user)

    if request.method == 'POST':
        new_folder_id = request.POST.get('new_folder_id')
        if new_folder_id:
            if current_group:
                new_folder = get_object_or_404(Folder, id=new_folder_id, group=current_group)
            else:
                new_folder = get_object_or_404(Folder, id=new_folder_id, owner=request.user)
            file.folder = new_folder
            file.save()
            if current_group:
                return redirect('home_app:group_list_with_id', group_id=group_id, folder_id=new_folder.id)
            else:
                return redirect('home_app:folder_list_with_id', folder_id=new_folder.id)
        else:
            messages.error(request, 'Please select a valid target folder.', extra_tags='danger')

    if current_group:
        folders = Folder.objects.filter(group=current_group)
    else:
        folders = Folder.objects.filter(owner=request.user)

    return render(request, 'home_app/move_file.html', {'file': file, 'folders': folders, 'current_group': current_group})


# @login_required
# def copy_file(request, file_id):
#     file = get_object_or_404(File, id=file_id)
#     if request.method == 'POST':
#         new_folder_id = request.POST.get('new_folder_id')
#         new_folder = get_object_or_404(Folder, id=new_folder_id, owner=request.user)
#         filename, file_extension = os.path.splitext(file.name)
#         new_file = File(
#             name=filename + "-Copy" + file_extension,
#             content=file.content,
#             owner=request.user,
#             folder=new_folder,
#             # Add other fields as necessary, excluding read-only fields
#         )
#         new_file.save()
#         return redirect('home_app:folder_list')
#     folders = Folder.objects.filter(owner=request.user)
#     return render(request, 'home_app/copy_file.html', {'file': file, 'folders': folders})



@login_required
def copy_file(request, group_id=None, file_id=None):
    if group_id:
        current_group = get_object_or_404(Group, id=group_id)
        file = get_object_or_404(File, id=file_id, group=current_group)
    else:
        current_group = None
        file = get_object_or_404(File, id=file_id, owner=request.user)

    if request.method == 'POST':
        new_folder_id = request.POST.get('new_folder_id')
        if new_folder_id:
            if current_group:
                new_folder = get_object_or_404(Folder, id=new_folder_id, group=current_group)
            else:
                new_folder = get_object_or_404(Folder, id=new_folder_id, owner=request.user)
            
            size = sum_by_type(request)
            total_size = calculate_total_size(size)
            if total_size["unformatted"] + file.size() > 100e6:
                messages.error(request, 'Not enough space on your drive.', extra_tags='danger')
                if file_id:
                    return redirect('home_app:copy_file', file_id=file_id)
                else:
                    return redirect('home_app:copy_file_group', group_id=group_id, file_id=file_id)
            
            filename, file_extension = os.path.splitext(file.name)
            new_file = File(
                name=f"{filename}-Copy{file_extension}",
                content=file.content,
                owner=request.user,
                folder=new_folder,
                group=current_group,
            )
            new_file.save()
            if current_group:
                return redirect('home_app:group_list_with_id', group_id=group_id, folder_id=new_folder.id)
            else:
                return redirect('home_app:folder_list_with_id', folder_id=new_folder.id)
        else:
            messages.error(request, 'Please select a valid target folder.', extra_tags='danger')

    if current_group:
        folders = Folder.objects.filter(group=current_group)
    else:
        folders = Folder.objects.filter(owner=request.user)

    return render(request, 'home_app/copy_file.html', {'file': file, 'folders': folders, 'current_group': current_group})