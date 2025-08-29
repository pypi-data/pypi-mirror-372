.. This README is meant for consumption by humans and PyPI. PyPI can render rst files so please do not use Sphinx features.
   If you want to learn more about writing documentation, please check out: http://docs.plone.org/about/documentation_styleguide.html
   This text does not appear on PyPI or github. It is a comment.

.. image:: https://github.com/collective/iosanita.contenttypes/actions/workflows/plone-package.yml/badge.svg
    :target: https://github.com/collective/iosanita.contenttypes/actions/workflows/plone-package.yml

.. image:: https://coveralls.io/repos/github/collective/iosanita.contenttypes/badge.svg?branch=main
    :target: https://coveralls.io/github/collective/iosanita.contenttypes?branch=main
    :alt: Coveralls

.. image:: https://codecov.io/gh/collective/iosanita.contenttypes/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/collective/iosanita.contenttypes

.. image:: https://img.shields.io/pypi/v/iosanita.contenttypes.svg
    :target: https://pypi.python.org/pypi/iosanita.contenttypes/
    :alt: Latest Version

.. image:: https://img.shields.io/pypi/status/iosanita.contenttypes.svg
    :target: https://pypi.python.org/pypi/iosanita.contenttypes
    :alt: Egg Status

.. image:: https://img.shields.io/pypi/pyversions/iosanita.contenttypes.svg?style=plastic   :alt: Supported - Python Versions

.. image:: https://img.shields.io/pypi/l/iosanita.contenttypes.svg
    :target: https://pypi.python.org/pypi/iosanita.contenttypes/
    :alt: License


=======================
IO-Sanita content-types
=======================

Gestione dei content-type di Io-Sanita

Correlazioni tra content-type
=============================

Unità Organizzative
-------------------

Alcuni content-type tipo Servizio o Struttura, hanno una correlazione con le Unità organizzative.

Da un'Unità organizzativa, è possibile sapere quali contenuti la correlano facendo una ricerca in catalogo sull'indice **uo_correlata**.

Ad esempio::

    > http://localhost:8080/Plone/++api++/@search?uo_correlata_uid=xxx


Dove xxx è l'uid di una Unità organizzativa.

Questa chiamata ritorna tutti i contenuti del sito che correlano quell'Unità Organizzativa.
Essendo una ricerca, il risultato è paginato a 25 di default, ma si può aumentare con determinati parametri.

Si può anche filtrare per un determinato tipo di contenuto, aggiungendo alla query per esempio: *&portal_type=Servizio*.


Strutture
---------

Alcuni content-type tipo Servizio o Struttura, hanno una correlazione con le Strutture.

Da una Struttura, è possibile sapere quali contenuti la correlano facendo una ricerca in catalogo sull'indice **struttura_correlata**.

Ad esempio::

    > http://localhost:8080/Plone/++api++/@search?struttura_correlata_uid=xxx


Dove xxx è l'uid di una Struttura.

Questa chiamata ritorna tutti i contenuti del sito che correlano quella Struttura.
Essendo una ricerca, il risultato è paginato a 25 di default, ma si può aumentare con determinati parametri.

Si può anche filtrare per un determinato tipo di contenuto, aggiungendo alla query per esempio: *&portal_type=Servizio*.

Expander view-extra-data
========================

E' un expander che aggiunge dei dati extra alla serializzazione di un content-type.

A seconda del tipo di contenuto, possono esserci dei dati differenti, a seconda di quello che serve al frontend.

back-references
---------------

Lista delle back-references dei vari contenuti suddivise per tipo di contenuto.

Questo expander ritorna però solamente al massimo 25 elementi.
Se il contenuto ne ha di più, c'è da usare il metodo indicato sopra, e fare una chiamata a parte con la ricerca e la paginazione.

Bando
-----

Per i bandi, ci sono due info aggiuntive:

- approfondimenti
- stato_bando


Migrazione da vecchi siti
=========================

C'è un'interfaccia (*IoSanitaMigrationMarker*) che se implementata dalla REQUEST, disattiva alcuni eventi/verifiche di sicurezza
sui content-type appena creati.

Questo serve per esempio in fase di migrazione. Basta applicare l'interfaccia alla request nella procedura di import::

    from iosanita.contenttypes.interfaces import IoSanitaMigrationMarker

    ...
    alsoProvides(self.request, IoSanitaMigrationMarker)


Installazione
=============

Per installare iosanita.contenttypes bisogna per prima cosa aggiungerlo al buildout::

    [buildout]

    ...

    eggs =
        iosanita.contenttypes


e poi lanciare il buildout con ``bin/buildout``.

Successivamente va installato dal pannello di controllo di Plone.


Contribuisci
============

- Issue Tracker: https://github.com/redturtle/iosanita.contenttypes/issues
- Codice sorgente: https://github.com/redturtle/iosanita.contenttypes


Licenza
=======

Questo progetto è rilasciato con licenza GPLv2.

Autori
======

Questo progetto è stato sviluppato da **RedTurtle Technology**.

.. image:: https://avatars1.githubusercontent.com/u/1087171?s=100&v=4
   :alt: RedTurtle Technology Site
   :target: http://www.redturtle.it/
