from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import *
from .serializers import *

class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def create(self, request, *args, **kwargs):
        user = request.user
        role = user.role

        # CU role인 경우 Customer 객체 생성
        if role == 'CU':
            customer_data = {'user': user.id, 'username': request.data.get('username')}
            customer_serializer = CustomerSerializer(data=customer_data)
            if customer_serializer.is_valid():
                customer_serializer.save()
                serializer = self.get_serializer(user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(customer_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # CO role인 경우 Company 객체 생성
        elif role == 'CO':
            company_data = {'user': user.id, 'username': request.data.get('username'), 'category': request.data.get('category')}
            company_serializer = CompanySerializer(data=company_data)
            if company_serializer.is_valid():
                company = company_serializer.save()

                # Company 객체와 연결된 AccountInformation 객체 생성
                account_data = {'company': company.id, 'username': request.data.get('username'), 'bankName': request.data.get('bankName'), 'accountNumber': request.data.get('accountNumber')}
                account_serializer = AccountInformationSerializer(data=account_data)
                if account_serializer.is_valid():
                    account_serializer.save()
                    serializer = self.get_serializer(user)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    # AccountInformation 생성 실패시 Company 객체 삭제
                    company.delete()
                    return Response(account_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(company_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Invalid role.'}, status=status.HTTP_400_BAD_REQUEST)