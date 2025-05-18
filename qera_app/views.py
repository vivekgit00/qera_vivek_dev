from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from .serializers import Product, Productserializer
from rest_framework import status
from rest_framework.decorators import action


class ProductView(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = Productserializer
    
    @action(detail=False, methods=['post'], url_path='product_qr')
    def check_or_create_product(self, request):
        unique_code = request.data.get('unique_code')

        if unique_code and Product.objects.filter(unique_code=unique_code).exists():
            return Response(
                {"message": "Product with this unique_code already exists."},
                status=status.HTTP_400_BAD_REQUEST
            )

        data = request.data.copy()
        data['activated'] = True  # Ensure 'activated' is set to True

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    