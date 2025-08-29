.. This README is meant for consumption by humans and pypi. Pypi can render rst files so please do not use Sphinx features.
   If you want to learn more about writing documentation, please check out: http://docs.plone.org/about/documentation_styleguide.html
   This text does not appear on pypi or github. It is a comment.

================
pas.plugins.imio
================

Install local or remote connector to Imio authentic (SSO).


Features
--------

- Override Plone login page
- Connect with SSO
- Disabled edition of username and e-mail
- Connect with JWT


.. image:: https://github.com/IMIO/pas.plugins.imio/workflows/Tests/badge.svg
    :target: https://github.com/IMIO/pas.plugins.imio/actions?query=workflow%3ATests
    :alt: CI Status

.. image:: https://coveralls.io/repos/github/IMIO/pas.plugins.imio/badge.svg?branch=master
    :target: https://coveralls.io/github/IMIO/pas.plugins.imio?branch=master
    :alt: Coveralls


Installation
------------

You need libffi-dev and openssl-dev packages installed (`sudo apt install libffi-dev openssl-dev`)
Install pas.plugins.imio by adding it to your buildout::

    [buildout]

    ...

    eggs =
        pas.plugins.imio

And then running ``bin/buildout``

After your instance is up, you can now install pas.plugins.imio from addons page.


Usage
-----

To update list of users, go to one of this view :

- /@@add-authentic-users?type=usagers
- /@@add-authentic-users?type=agents


To login with an user registred into Plone/Zope instead of pas plugin use this view :

- Plone 4: ${portal_url}/login_form
- Plone 5.2+: ${portal_url}/zope_login

You can also use plone default view for login with zope admin: aq_parent/@@plone-root-login


How to use JWT
--------------

First, add an Openid Connect client to Authentic with these options:

- Processus d’autorisation : mot de passe du propriétaire de ressource
- Politique des identifiants : identifiant unique
- Portée de cession par crédentiels du propriétaire de la ressource : openid
- Algorithme de signature IDToken : RSA
- Oidc claims : userid | django_user_identifier | openid

Second, you can ask Authentic to get a JWT

Python code example::

    import requests

    url = "http://agents.localhost/idp/oidc/token/"
    payload = {
        "grant_type": "password",
        "client_id": "client-id-plone5-app",
        "client_secret": "client-secret-plone5-app",
        "username": "jdoe",
        "password": "jdoe",
        "scope": ["openid"],
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }

    response = requests.post(url, headers=headers, data=payload).json()
    id_token = response.get("id_token")

Finally, you can request Plone with bearer header::

    import requests

    url = "http://localhost:8081/imio/test-1/"
    headers = {
        "Accept": "application/json",
        "Authorization": "Bearer {0}".format(id_token),
    }

    response = requests.get(url, headers=headers)

Translations
------------

This product has been translated into

- English
- French


Contribute
----------

- Issue Tracker: https://github.com/IMIO/pas.plugins.imio/issues
- Source Code: https://github.com/IMIO/pas.plugins.imio


License
-------

The project is licensed under the GPLv2.
