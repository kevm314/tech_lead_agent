from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    Language,
)

# Full list of support languages
#[print(e.value) for e in Language]
for lang in Language:
    # You can also see the separators used for a given language
    splits = RecursiveCharacterTextSplitter.get_separators_for_language(lang)
    print(f"{lang.value}: {splits}")