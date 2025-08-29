Changelog
=========


1.0.8 (2025-08-29)
------------------

- Blocco search / variante table - aggiunte le proprietà dei campi nella colonna nel serializer
  [mamico]
- get_taxonomy_vocab non si rompe se non è presente la tassonomia richiesta.
  [cekk]
- Base implementation for CSV/PDF export of tabular data
  [cekk] [mamico]
- Implementation for CSV/PDF export for search block
  [mamico]

1.0.7 (2025-06-18)
------------------

- Struttura CT: return related people as backreferences if flag is enabled in controlpanel. Re-added new "personale_correlato" field to link Persona cts manually.
  [daniele]

1.0.6 (2025-05-29)
------------------

- Remove dependency with auslfe.farmacie.
  [cekk]

1.0.5 (2025-04-22)
------------------

- Install collective.volto.formblocks.
  [cekk]
- Temporary disabled tests because there is a private dependency: auslfe.farmacie.
  [cekk]
- Fixed help label id. Added missing trnslation for related items.
  [daniele]
- Enable kitconcept.seo for plone site.
  [cekk]

1.0.4 (2024-11-22)
------------------

- Add Subject_bando index.
  [cekk]


1.0.3 (2024-11-20)
------------------

- geolocation metadata return None if not set and not an empty dict.
  [cekk]

1.0.2 (2024-11-20)
------------------

- Add NewsItem summary serializer, to return always metadata infos about tipologia_notizia and tipologia_notizia_metadata.
  [cekk]


1.0.1 (2024-11-19)
------------------

- Fix package name.
  [daniele]


1.0.0 (2024-11-19)
------------------

- Initial release.
  [daniele]
