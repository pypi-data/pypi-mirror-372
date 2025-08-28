from sqlalchemy.orm import aliased

def get_field(model, field_name, query):
    if "." not in field_name:
        return query,getattr(model, field_name)

    path_parts = field_name.split(".")
    current_model = model
    current_alias = None
    alias_map = {}

    for i, part in enumerate(path_parts[:-1]):
        path_key = ".".join(path_parts[:i+1])
        relationship_attr = getattr(current_model, part)

        if path_key in alias_map:
            aliased_model = alias_map[path_key]
        else:
            aliased_model = aliased(relationship_attr.property.mapper.class_)
            alias_map[path_key] = aliased_model

            if current_alias is None:
                query = query.join(aliased_model, relationship_attr)
            else:
                query = query.join(aliased_model, getattr(current_alias, part))

        current_model = relationship_attr.property.mapper.class_
        current_alias = aliased_model

    return query,getattr(current_alias, path_parts[-1])
