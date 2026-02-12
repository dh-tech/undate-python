#!/usr/bin/env python

from babel.dates import get_month_names


languages = {
    "rw": "Kinyarwanda",
    "lg": "Ganda",
    "ti": "Tigrinya",
    "fr": "French",
    "en": "English",
}
# for locale_code in ["fr_FR", "de_DE", "rw_rw", "ti_ET", "lg_UG"]:


def main():
    for lang, name in languages.items():
        print(f"\n###  {name} (`{lang}`)")
        for width in ["abbreviated", "wide"]:
            print(
                f"- {width}: " + ", ".join(get_month_names(width, locale=lang).values())
            )


if __name__ == "__main__":
    main()
