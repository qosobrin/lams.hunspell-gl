# -*- coding:utf-8 -*-

import codecs, pywikibot, re, sys
import galipedia as common


def parseCountryName(name):

    # Valores predeterminados, correctos polo menos para «España».
    categoryNames = [
        u"Barrios de {name}".format(name=name),
        u"Distritos de {name}".format(name=name)
    ]
    outputFileName = u"{filename}.dic".format(filename=name.lower().replace(" ", "-"))

    return categoryNames, outputFileName


def parsePageName(pageName):
    if not invalidPagePattern.match(pageName):
        if " - " in pageName: # Nome en galego e no idioma local. Por exemplo: «Bilbao - Bilbo».
            parts = pageName.split(" - ")
            locationNames.add(parts[0])
        elif "," in pageName: # Datos adicionais para localizar o lugar. Por exemplo: «Durango, País Vasco».
            parts = pageName.split(",")
            locationNames.add(parts[0])
        else:
            locationNames.add(pageName)


def loadLocationsFromCategoryAndSubcategories(category):
    print u"Cargando {name}…".format(name=category.title())
    for subcategory in category.subcategories():
        if validCategoryPattern.match(subcategory.title()):
            loadLocationsFromCategoryAndSubcategories(subcategory)
        elif not invalidCategoryPattern.match(subcategory.title()):
            parsePageName(subcategory.title().split(":")[1])
    for page in category.articles():
        pageName = page.title()
        parsePageName(pageName)


# Lóxica principal:

if len(sys.argv) != 2:
    print "A forma correcta de executar o script é:"
    print "    galipedia-toponimia-zonas.py <estado>"
    print
    print "O estados e continentes que se saben compatíbeis son:"
    print "    España."
    sys.exit()

countryName = sys.argv[1].decode('UTF-8')
categoryNames, outputFileName = parseCountryName(countryName)

nameSuffixes = re.compile(" \([^)]+\)$")

locationNames = set()
galipedia = pywikibot.Site(u"gl", u"wikipedia")
invalidPagePattern = re.compile(u"^(Modelo:|Barrios |Distritos )")
validCategoryPattern = re.compile(u"^Categoría:(Barrios|Distritos) ")
invalidCategoryPattern = re.compile(u"^(Barrios|Distritos) ")

for categoryName in categoryNames:
    loadLocationsFromCategoryAndSubcategories(pywikibot.Category(galipedia, u"Categoría:{}".format(categoryName)))


dicFileContent = ""
for name in sorted(locationNames):
    match = nameSuffixes.search(name)
    if match:
        name = name[:-len(match.group(0))]
    if " " in name: # Se o nome contén espazos, usarase unha sintaxe especial no ficheiro .dic.
        for ngrama in name.split(u" "):
            if ngrama not in common.wordsToIgnore: # N-gramas innecesarios por ser vocabulario galego xeral.
                dicFileContent += u"{ngrama} po:topónimo [n-grama: {name}]\n".format(ngrama=ngrama, name=name)
    else:
        if name not in common.wordsToIgnore:
            dicFileContent += u"{name} po:topónimo\n".format(name=name)

with codecs.open(outputFileName, u"w", u"utf-8") as fileObject:
    fileObject.write(dicFileContent)