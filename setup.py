from setuptools import setup, find_packages

setup(
    name = "hotdoc_search_extension",
    version = "0.6.5",
    keywords = "client-side search full text hotdoc",
    url='https://github.com/hotdoc/hotdoc_search_extension',
    author_email = 'mathieu.duponchelle@opencreed.com',
    license = 'LGPL',
    description = "An extension for hotdoc that enables full text client-side search",
    author = "Mathieu Duponchelle",
    packages = find_packages(),
    package_data = {
        '': ['stopwords.txt', '*.js', '*.html'],
    },

    entry_points = {'hotdoc.extensions': 'get_extension_classes = hotdoc_search_extension.search_extension:get_extension_classes'},
    install_requires = [
        'lxml',
    ],
)
