from django.db import models
from django.contrib.auth.models import User
from auth_app.models import Group
import os

# Create your models here.


class Folder(models.Model):
    name = models.CharField(max_length=255)
    group = models.ForeignKey(Group, null=True, on_delete=models.CASCADE, related_name='folders')
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    parent_folder = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='subfolders') # related name est utilisé pour spécifier le nom de l'attribut qui sera utilisé pour accéder aux objets liés dans l'autre sens de la relation
    created_at = models.DateTimeField(auto_now_add=True)
    #updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
        

class File(models.Model):
    name = models.CharField(max_length=255)
    group = models.ForeignKey(Group, null=True, on_delete=models.CASCADE, related_name='files')
    content = models.BinaryField(null=True, blank=True)  # New field to store file content in the database
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    folder = models.ForeignKey(Folder, null=True, on_delete=models.CASCADE, related_name='files')
    created_at = models.DateTimeField(auto_now_add=True)
    #updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    def size(self):
        return len(self.content)

    @property
    def formatted_size(self):
        size = self.size()
        for unit in ['Octets', 'Ko', 'Mo']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
            
    @property
    def extension_file(self):
        filename, file_extension = os.path.splitext(self.name)
        return file_extension
    
    