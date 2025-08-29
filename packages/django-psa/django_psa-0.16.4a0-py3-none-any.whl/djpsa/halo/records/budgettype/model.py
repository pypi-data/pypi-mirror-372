from django.db import models
from model_utils import FieldTracker


class BudgetType(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    default_rate = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Budget Types"

    def __str__(self):
        return str(self.name)


class BudgetTypeTracker(BudgetType):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'halo_budgettype'
