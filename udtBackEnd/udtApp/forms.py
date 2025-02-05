from django import forms

# Definiamo le opzioni per gli enum
MACROMODEL_CHOICES = [
    ('greenshield', 'Greenshield'),
    ('underwood', 'Underwood'),
    ('vanaerde', 'Van Aerde'),
]

CAR_FOLLOWING_MODEL_CHOICES = [
    ('Krauss', 'Krauss'),
    ('IDM', 'IDM'),
    ('W99', 'Wiedemann'),
]

# Opzioni per gli slot orari (solo ore intere da 00 a 24)
TIME_SLOTS = [(i, f"{i}:00") for i in range(0, 25)]  # Da 00 a 24
class ConfigForm(forms.Form):
    macromodel = forms.ChoiceField(choices=MACROMODEL_CHOICES, label="Macromodel")
    car_following_model = forms.ChoiceField(choices=CAR_FOLLOWING_MODEL_CHOICES, label="Car Following Model")
    tau = forms.FloatField(
        label="Tau",
        min_value=0.1, max_value=10, initial=1,
        widget=forms.NumberInput(attrs={'step': '0.1'})
    )

    # Additional parameters (saranno gestiti via JavaScript)
    sigma = forms.FloatField(
        label="Sigma (Krauss)", min_value=0, max_value=1, initial=0.5,
        widget=forms.NumberInput(attrs={'step': '0.1'}), required=False
    )
    sigma_step = forms.FloatField(
        label="Sigma Step (Krauss)", min_value=0.1, initial=1,
        widget=forms.NumberInput(attrs={'step': '0.1'}), required=False
    )

    delta = forms.FloatField(
        label="Delta (IDM)", min_value=1, initial=4,
        widget=forms.NumberInput(attrs={'step': '1'}), required=False
    )
    stepping = forms.FloatField(
        label="Stepping (IDM)", min_value=0.25, initial=0.25,
        widget=forms.NumberInput(attrs={'step': '0.01'}), required=False
    )

    cc1 = forms.FloatField(
        label="CC1 (W99)", min_value=0.1, initial=1.30,
        widget=forms.NumberInput(attrs={'step': '0.1'}), required=False
    )
    cc2 = forms.FloatField(
        label="CC2 (W99)", min_value=0.1, initial=8.0,
        widget=forms.NumberInput(attrs={'step': '0.1'}), required=False
    )

    data = forms.DateField(
        label="Date",
        widget=forms.DateInput(attrs={'type': 'date', 'format': 'yyyy-mm-dd'})
    )

    # Selezione dello slot orario
    start_time = forms.ChoiceField(choices=TIME_SLOTS, label="Starting Time")
    end_time = forms.ChoiceField(choices=TIME_SLOTS, label="Ending Time")
    # Validazione personalizzata: start_time deve essere < end_time
    def clean(self):
        cleaned_data = super().clean()
        start = int(cleaned_data.get("start_time"))
        end = int(cleaned_data.get("end_time"))

        if start >= end:
            raise forms.ValidationError("The start time must be less than the end time.")

        return cleaned_data
