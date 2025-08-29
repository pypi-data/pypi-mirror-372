# -*- coding: utf-8 -*-
from iosanita.contenttypes.interfaces.persona import IPersona
from plone.app.content.interfaces import INameFromTitle
from plone.dexterity.content import Container
from zope.interface import implementer


@implementer(IPersona, INameFromTitle)
class Persona(Container):
    """Persona CT"""

    @property
    def title(self):
        """
        Title is set from nome and cognome fields
        """
        nome = getattr(self, "nome", "")
        cognome = getattr(self, "cognome", "")
        titolo_persona = getattr(self, "titolo_persona", "")
        return " ".join([p for p in [titolo_persona, cognome, nome] if p])

    @title.setter
    def title(self, value):
        pass

    # maybe needed when we enable rubrica
    # @property
    # def rubrica_title(self):
    #     if getattr(self, "nome", "") and getattr(self, "cognome", ""):
    #         return "{cognome} {nome}".format(nome=self.nome, cognome=self.cognome)
    #     else:
    #         return ""

    # @property
    # def rubrica_id(self):
    #     return idnormalizer.normalize(self.rubrica_title)
