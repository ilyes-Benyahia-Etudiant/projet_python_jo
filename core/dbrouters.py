class OffresRouter:
    """
    Route toutes les opérations du modèle Offre vers la base 'supabase'.
    """
    app_label = "users"
    model_names = {"Offre"}

    def _is_offre(self, model):
        return model._meta.app_label == self.app_label and model.__name__ in self.model_names

    def db_for_read(self, model, **hints):
        return "supabase" if self._is_offre(model) else None

    def db_for_write(self, model, **hints):
        return "supabase" if self._is_offre(model) else None

    def allow_relation(self, obj1, obj2, **hints):
        # Relations autorisées si l'une des deux est dans 'supabase'
        if self._is_offre(obj1.__class__) or self._is_offre(obj2.__class__):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # Comme managed=False, Django ne migrera pas 'offres' de toute façon.
        # On bloque toute migration de 'Offre' ailleurs par sécurité.
        if app_label == "users" and model_name == "offre":
            return db == "supabase"
        return None