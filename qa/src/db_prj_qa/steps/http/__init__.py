from .cats import CatalogServiceSteps


class CatalogServiceHttpSteps(object):
    def __init__(self, base_url):
        self.cats = CatalogServiceSteps(base_url)
