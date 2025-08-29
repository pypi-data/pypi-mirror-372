from lseg_analytics.common._utils import main_object_repr


class ResourceBase:
    def __repr__(self):
        return main_object_repr(self)
