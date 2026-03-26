from rest_framework.authentication import TokenAuthentication

class QueryParameterTokenAuthentication(TokenAuthentication):
    """
    Custom authentication to allow passing the Token via URL query parameter.
    Example: /api/billing/invoices/1/download_pdf/?token=1234567890abcdef
    """
    def authenticate(self, request):
        token = request.query_params.get('token')
        if token:
            # If token found in URL, authenticate using it
            return self.authenticate_credentials(token)
        
        # Fallback to standard Token authentication (Headers)
        return super().authenticate(request)
