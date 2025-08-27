class BaseDataFromOdoo:
    def build(self):
        data = self._get_data()
        return self.DataModel(**data)
