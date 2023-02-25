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

    python -m build (edited) 

deployment to PyPI (step 2):: 

    twine upload dist/* (edited) 

**Docker**
----------

deployment to docker:: 

    docker build --tag blueskysolarracing/revolution:0.0.0.dev1 .

deployment to docker:: 

    docker push blueskysolarracing/revolution:0.0.0.dev1

**git tag**
-----------

add git tag:: 

    git tag 0.0.0.dev1
