from django import forms
from .models import File, Folder

# class FileForm(forms.ModelForm):
#     class Meta:
#         model = File
#         fields = ['folder']

        

class FolderForm(forms.ModelForm):
    # parent_folder = forms.ModelChoiceField(
    #     queryset=Folder.objects.filter(user=user),
    #     required=False,  # si le champ n'est pas obligatoire
    #     empty_label="Aucun parent"  # optionnellement, ajouter une étiquette vide
    # )
    
    class Meta:
        model = Folder
        fields = ['name']

class MoveFolderForm(forms.Form):
    new_location = forms.ModelChoiceField(queryset=Folder.objects.all(), label="New Location")