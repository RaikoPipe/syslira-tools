CP_COLUMNS = {
    "title",
    "abstractNote",
    "date",
    "proceedingsTitle",
    "conferenceName",
    "place",
    "volume",
    "pages",
    "series",
    "language",
    "DOI",
    "ISBN",
    "shortTitle",
    "url",
    "accessDate",
    "archive",
    "archiveLocation",
    "libraryCatalog",
    "callNumber",
    "rights",
    "extra",
    "creators",
}

AR_COLUMNS = {
    "title",
    "abstractNote",
    "publicationTitle",
    "volume",
    "issue",
    "pages",
    "date",
    "series",
    "seriesTitle",
    "seriesText",
    "journalAbbreviation",
    "language",
    "DOI",
    "ISSN",
    "shortTitle",
    "url",
    "accessDate",
    "archive",
    "archiveLocation",
    "libraryCatalog",
    "callNumber",
    "rights",
    "extra",
    "creators",
}

EXTRA_COLUMNS = {
    "id",
    "scopusId",
    "citedByCount",
    "zoteroKey",
    "fulltext",
    "subType",
    "tags",
    "relations",
    "collections",
    "itemType"
}

UNION_COLUMNS = AR_COLUMNS.union(CP_COLUMNS).union(EXTRA_COLUMNS)

LIBRARY_COLUMNS = CP_COLUMNS.union(AR_COLUMNS).union(EXTRA_COLUMNS)

IDENTIFIER_TYPES = ["DOI", "ISBN", "PMID", "ArXiv", "DBLP", "MAG", "CorpusId"]

ITEMTYPE_MAP = {

}