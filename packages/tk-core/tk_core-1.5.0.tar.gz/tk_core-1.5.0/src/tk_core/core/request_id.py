class PostInitMetaclass(type):
    # https://stackoverflow.com/questions/795190/how-to-perform-common-post-initialization-tasks-in-inherited-classes
    def __call__(cls, *args, **kwargs):  # noqa
        obj = type.__call__(cls, *args, **kwargs)
        # __make_id__ is defined in the base_requests.py file
        if kwargs.get("disable_post_init", False):
            return obj
        obj.__post_init__()
        return obj
