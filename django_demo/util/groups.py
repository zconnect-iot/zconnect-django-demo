def get_parental_chain(obj):
    """ Given an object with a parent attribute return a set of the id's in the
    parental chain above that object """
    parental_objs = {obj.id}
    while obj.parent:
        obj = obj.parent
        parental_objs.add(obj.id)
    return parental_objs
