# rattingtax/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from solo.models import SingletonModel  # jeśli używasz ustawień globalnych

class Corporation(models.Model):
    corporation_id = models.BigIntegerField(unique=True)
    name = models.CharField(max_length=128)
    ticker = models.CharField(max_length=16, blank=True)
    logo_url = models.URLField(blank=True)

    class Meta:
        default_permissions = ()  # <— wyłączamy add/change/delete/view
        permissions = [
            ("basic_access", "Can use ratting tax module"),
            ("view_all", "Can view all corporations in RattingTax"),
        ]

    def __str__(self):
        return f"{self.name} [{self.ticker}]" if self.ticker else self.name


class TaxConfig(models.Model):
    corp = models.OneToOneField(Corporation, on_delete=models.CASCADE, related_name="tax_cfg")
    corp_tax_rate_percent = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)

    class Meta:
        default_permissions = ()  # <—

    def __str__(self):
        return f"{self.corp} (corp {self.corp_tax_rate_percent}%)"


class CorpMonthStat(models.Model):
    corp = models.ForeignKey(Corporation, on_delete=models.CASCADE, related_name="month_stats")
    year = models.PositiveIntegerField()
    month = models.PositiveIntegerField()
    corp_bounty_tax_amount = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    closed = models.BooleanField(default=False, help_text="When true, month is frozen and not recalculated.")


    class Meta:
        default_permissions = ()
        unique_together = ("corp", "year", "month")
        ordering = ["-year", "-month"]

    def __str__(self):
        return f"{self.corp} {self.year}-{self.month:02d}: {self.corp_bounty_tax_amount}"


class CorpTokenLink(models.Model):
    corp = models.OneToOneField(Corporation, on_delete=models.CASCADE, related_name="token_link")
    character_id = models.BigIntegerField()
    character_name = models.CharField(max_length=128)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        default_permissions = ()

    def __str__(self):
        return f"{self.corp} via {self.character_name}"


# (opcjonalnie) globalne ustawienia — jeśli masz klasę ustawień:
class AllianceSettings(SingletonModel):
    alliance_rate_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    flat_tax_reduction = models.BigIntegerField(default=0)

    class Meta:
        verbose_name = "Alliance Settings"
        default_permissions = ()

    def __str__(self):
        return "Alliance Settings"
