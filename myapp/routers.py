class DatabaseRouter:
    """
    Router to control database operations for different models
    """
    
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'myapp':
            if model.__name__ in ['Product', 'ProductAnalytics']:
                return 'products_db'
        return 'default'

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'myapp':
            if model.__name__ in ['Product', 'ProductAnalytics']:
                return 'products_db'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        db_set = {'default', 'products_db'}
        if obj1._state.db in db_set and obj2._state.db in db_set:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'myapp':
            if model_name in ['product', 'productanalytics']:
                return db == 'products_db'
            else:
                return db == 'default'
        return None