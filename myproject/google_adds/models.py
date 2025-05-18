from django.db import models

class Tenant(models.Model):
    name = models.CharField(max_length=100)
    # store OAuth2 tokens for each tenant
    refresh_token = models.CharField(max_length=255)
    client_id = models.CharField(max_length=255)
    client_secret = models.CharField(max_length=255)
    developer_token = models.CharField(max_length=255)
    login_customer_id = models.CharField(max_length=20)  # Manager account ID

    def __str__(self):
        return self.name
