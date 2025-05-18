import google.ads.google_ads.client
from django.shortcuts import redirect, render
from django.conf import settings
from .models import Tenant
from django.http import JsonResponse
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# OAuth2 config - replace these with your own from Google Cloud Console
CLIENT_ID = 'YOUR_CLIENT_ID'
CLIENT_SECRET = 'YOUR_CLIENT_SECRET'
DEVELOPER_TOKEN = 'YOUR_DEVELOPER_TOKEN'
REDIRECT_URI = 'http://localhost:8000/google_ads/oauth2callback'

SCOPES = ['https://www.googleapis.com/auth/adwords']

def oauth2_start(request):
    from google_auth_oauthlib.flow import Flow
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "redirect_uris": [REDIRECT_URI],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        },
        scopes=SCOPES,
    )
    flow.redirect_uri = REDIRECT_URI

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    request.session['state'] = state
    return redirect(authorization_url)


def oauth2_callback(request):
    from google_auth_oauthlib.flow import Flow
    state = request.session['state']

    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "redirect_uris": [REDIRECT_URI],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        },
        scopes=SCOPES,
        state=state
    )
    flow.redirect_uri = REDIRECT_URI

    authorization_response = request.build_absolute_uri()
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials

    # Save tokens to DB for tenant - for demo, create new tenant
    tenant = Tenant.objects.create(
        name="Tenant 1",
        refresh_token=credentials.refresh_token,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        developer_token=DEVELOPER_TOKEN,
        login_customer_id='INSERT_MANAGER_ACCOUNT_ID',  # your test manager ID
    )
    return JsonResponse({"message": "OAuth success, tenant created", "tenant_id": tenant.id})

def get_campaigns(request, tenant_id):
    tenant = Tenant.objects.get(id=tenant_id)

    # Load credentials
    credentials = Credentials(
        None,
        refresh_token=tenant.refresh_token,
        client_id=tenant.client_id,
        client_secret=tenant.client_secret,
        token_uri='https://oauth2.googleapis.com/token',
        scopes=SCOPES
    )

    # Create google ads client
    google_ads_client = google.ads.google_ads.client.GoogleAdsClient.load_from_dict({
        "developer_token": tenant.developer_token,
        "refresh_token": tenant.refresh_token,
        "client_id": tenant.client_id,
        "client_secret": tenant.client_secret,
        "login_customer_id": tenant.login_customer_id,
        "use_proto_plus": True,
    })

    ga_service = google_ads_client.get_service("GoogleAdsService")

    query = """
        SELECT campaign.id, campaign.name
        FROM campaign
        WHERE campaign.status = 'ENABLED'
        ORDER BY campaign.id
    """

    response = ga_service.search(tenant.login_customer_id, query=query)

    campaigns = []
    for row in response:
        campaigns.append({
            "id": row.campaign.id,
            "name": row.campaign.name,
        })

    return JsonResponse({"campaigns": campaigns})
