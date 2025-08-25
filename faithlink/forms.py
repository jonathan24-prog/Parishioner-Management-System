from django import forms
from .models import Parishioner

class ParishionerForm(forms.ModelForm):
    class Meta:
        model = Parishioner
        fields = ['name', 'contact', 'family_group']

from accounts.models import CustomUser

class ParishionerFormUpdate(forms.ModelForm):
    class Meta:
        model = Parishioner
        fields = [
            'name', 'contact', 'gender', 'marital_status', 'nationality', 
            'address', 'emergency_contact', 'family_group', 'date_approved'
        ]
        widgets = {
            'date_approved': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'gender': forms.Select(choices=Parishioner.GENDER_CHOICES),
            'marital_status': forms.Select(choices=Parishioner.MARITAL_STATUS_CHOICES),
        }

from django import forms
from .models import SacramentRecord

class SacramentRecordForm(forms.ModelForm):
    class Meta:
        model = SacramentRecord
        fields = ['parishioner', 'sacrament', 'place_received', 'officiant', 'notes']

        widgets = {
            'date_received': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_date_received(self):
        date = self.cleaned_data.get('date_received')
        if date and date > forms.datetime.date.today():
            raise forms.ValidationError("Date received cannot be in the future.")
        return date


# donations/forms.py

from django import forms
from .models import Donation

class DonationForm(forms.ModelForm):
    class Meta:
        model = Donation
        fields = [
            'type', 'amount', 'payment_method',
            'item_name', 'quantity', 'item_condition', 'photo',
            'description', 'date', 'anonymous',
            'pickup_requested'
        ]

    def clean(self):
        cleaned_data = super().clean()
        donation_type = cleaned_data.get('type')

        if donation_type == 'money':
            if not cleaned_data.get('amount'):
                self.add_error('amount', "Amount is required for money donations.")
        elif donation_type == 'item':
            if not cleaned_data.get('item_name'):
                self.add_error('item_name', "Item name is required for item donations.")

        return cleaned_data
