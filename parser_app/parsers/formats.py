"""Списки форматов для парсинга.

`SUPPORTED_FORMATS` — форматы, которые сейчас реально обрабатываются в приложении.
`POTENTIALLY_USEFUL_FORMATS` — полезные кандидаты для будущей поддержки.
"""

SUPPORTED_FORMATS = (
    "pdf",
    "docx",
    "doc",
    "txt",
    "csv",
    "json",
    "md",
    "markdown",
    "tsv",
    "djvu",
    "xls",
    "xlsx",
    "odt",
    "ods",
)

POTENTIALLY_USEFUL_FORMATS = (
    "rtf",
    "epub",
    "html",
    "xml",
    "yaml",
    "ppt",
    "pptx",
    "odg",
    "pages",
    "numbers",
    "eml",
    "msg",
)
