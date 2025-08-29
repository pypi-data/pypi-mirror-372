from django.db import models
from model_utils import FieldTracker

# This is not a real record in Halo, but created for the purpose
# of easily storing and processing budget data. Uses the Ticket
# API to get a tickets budget data instead of having its own.


class BudgetData(models.Model):
    ticket = models.ForeignKey(
        'Ticket', on_delete=models.CASCADE)
    budget_type = models.ForeignKey(
        'BudgetType', on_delete=models.CASCADE, blank=True, null=True)
    hours = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True)
    rate = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True)
    money = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True)
    estimated_hours = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True)
    estimated_money = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True)
    actual_hours = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True)
    actual_money = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True)
    scheduled_hours = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True)
    scheduled_value = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True)
    toschedule_hours = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True)
    toschedule_value = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True)
    remaining_hours = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True)
    remaining_value = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Budget Data"


class BudgetDataTracker(BudgetData):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'halo_budgetdata'
