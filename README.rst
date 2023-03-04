Revolution
==========

Software for the Blue Sky Solar Racing Gen 12 electrical system 

**Setup virtual environment**
-----------------------------
``python -m venv venv``

Linux:: 

    source venv/bin/activate

Windows CMD:: 

    venv\Scripts\activate

**Install requirements:** 
-------------------------
``pip install -r requirements.txt``


**How to work with static type checking:**
------------------------------------------
``mypy --strict revolution``

flake8 pep 8 conformity check:: 

    flake8 revolution

**unit testing:**
-----------------
``python -m unittest``

**Deployment to PyPI**
----------------------

deployment to PyPI (step 0):: 

    replace all occurrences of version and update

deployment to PyPI (step 1):: 

    python -m build

deployment to PyPI (step 2):: 

    twine upload dist/*

**Docker**
----------

Build dockerfile into image:: 
    
    cd <directory_containing_dockerfile>

    docker build --tag <image_name>:<tag> .
    
    Ex: docker build --tag blueskysolarracing/revolution:0.0.0.dev1 .


deployment to docker:: 

    docker push <image_name>:<tag>

    Ex: docker push blueskysolarracing/revolution:0.0.0.dev1
    
Run docker container with persisted data between file system and container::

    cd <revolution_repo_path>
    
    docker run --name <container_name> -v ${pwd}/revolution:/usr/local/lib/python3.10/site-packages/revolution <image_name>:<tag>
    
Explore a running container. This command runs a new process inside a running container and lets you visit the file system::
    
    docker exec -t -i <container_name> /bin/bash

**git tag**
-----------

add git tag:: 
    
    git tag <tag>

    Ex: sgit tag 0.0.0.dev1
