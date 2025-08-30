from drf_spectacular.extensions import OpenApiSerializerExtension


class CustomDataSchema(OpenApiSerializerExtension):

    target_class = "smoothglue.authentication.serializers.PlatformUserSerializer"

    def map_serializer(self, auto_schema, direction):
        # pylint: disable=import-outside-toplevel
        # pylint: disable=no-name-in-module
        from smoothglue.authentication.serializers import UserDataSerializer

        # pylint: disable=inherit-non-class
        class Fixed(self.target_class):

            data = UserDataSerializer()

        return auto_schema._map_serializer(Fixed, direction)
