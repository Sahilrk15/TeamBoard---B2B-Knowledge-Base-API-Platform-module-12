from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Count, Q
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from api.models import Company, KBEntry, QueryLog
from api.permissions import IsAdminUser
from api.serializers import (
    KBEntrySerializer,
    KBQuerySerializer,
    LoginSerializer,
    RegisterSerializer,
)


def _issue_access_token(user):
    return str(RefreshToken.for_user(user).access_token)


class RegisterView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user = User.objects.create_user(
            username=data['username'],
            password=data['password'],
            email=data['email'],
        )
        # The post_save signal on User already created the Company row
        # (with a placeholder company_name and a generated api_key).
        # We just fill in the real company_name here.
        company = user.company
        company.company_name = data['company_name']
        company.save()

        access = _issue_access_token(user)

        return Response(
            {
                'username': user.username,
                'company_name': company.company_name,
                'api_key': company.api_key,
                'access': access,
            },
            status=201,
        )


class LoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user = authenticate(
            username=data['username'],
            password=data['password'],
        )
        if user is None:
            return Response(
                {'error': 'Invalid username or password.'},
                status=401,
            )

        company = user.company
        access = _issue_access_token(user)

        return Response(
            {
                'access': access,
                'company_name': company.company_name,
                'api_key': company.api_key,
            },
            status=200,
        )


class KBQueryView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = KBQuerySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        search_term = serializer.validated_data['search']

        company = request.user.company

        with transaction.atomic():
            matches = KBEntry.objects.filter(
                Q(question__icontains=search_term) | Q(answer__icontains=search_term)
            )
            results = list(matches)
            QueryLog.objects.create(
                company=company,
                search_term=search_term,
                results_count=len(results),
            )

        return Response(
            {
                'search': search_term,
                'count': len(results),
                'results': KBEntrySerializer(results, many=True).data,
            },
            status=200,
        )


class UsageSummaryView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        total_queries = QueryLog.objects.aggregate(total=Count('id'))['total']
        active_companies = QueryLog.objects.values('company').distinct().count()
        top_search_terms = list(
            QueryLog.objects.values('search_term')
            .annotate(count=Count('id'))
            .order_by('-count')[:5]
        )

        return Response(
            {
                'total_queries': total_queries,
                'active_companies': active_companies,
                'top_search_terms': top_search_terms,
            },
            status=200,
        )
