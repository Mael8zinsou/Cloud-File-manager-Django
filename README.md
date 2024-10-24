A Cloud Drive application (similar to Google Drive and OneDrive) using Django. To make the project simpler, the files will be stored on the server. The base folder of each user will be his login.

The tool can also work on local storage in replacement of File Explorer.

For example, if there are two users "foo" and "bar" that have uploaded some files, the file structure on the server will be simialr to this one:

    base_server_folder
        foo
            file1.txt
            images
                eiffel tower.png
        bar
            bread recipe.pdf
            2024
                python lecture.pfg