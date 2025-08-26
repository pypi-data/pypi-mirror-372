from .view_sets import DatasetViewSet


def register_drf_views(router):
    router.register(r"datasets", DatasetViewSet)


urlpatterns: list = []
