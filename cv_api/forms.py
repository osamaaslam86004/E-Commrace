from django import forms
from cv_api.models import (
    PersonalInfo,
    Overview,
    Education,
    Job,
    JobAccomplishment,
    SkillAndSkillLevel,
    ProgrammingArea,
    Projects,
    Publication,
)


class PersonalInfoForm(forms.ModelForm):
    class Meta:
        model = PersonalInfo
        fields = [
            "first_name",
            "middle_name",
            "last_name",
            "suffix",
            "locality",
            "region",
            "title",
            "email",
            "linkedin",
            "facebook",
            "github",
            "site",
            "twittername",
        ]
        exclude = [
            "id",
            "api_user_id_for_cv",
            "user_id_for_personal_info",
            "api_id_for_cv",
        ]

    def __init__(self, *args, **kwargs):
        super(PersonalInfoForm, self).__init__(*args, **kwargs)
        CHOICES = [("True", "Yes"), ("False", "No")]
        self.fields.update(
            {"condition": forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect)}
        )


class OverviewForm(forms.ModelForm):
    class Meta:
        model = Overview
        fields = ["text"]
        exclude = ["id", "personal_info"]


class EducationfoForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = [
            "name",
            "location",
            "schoolurl",
            "education_start_date",
            "education_end_date",
            "degree",
            "description",
        ]
        widgets = {
            "education_start_date": forms.DateInput(attrs={"type": "date"}),
            "education_end_date": forms.DateInput(attrs={"type": "date"}),
        }


class JobfoForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = "__all__"
        exclude = ["id", "personal_info_job"]
        widgets = {
            "job_start_date": forms.DateInput(attrs={"type": "date"}),
            "job_end_date": forms.DateInput(attrs={"type": "date"}),
        }


class JobAccomplishmentfoForm(forms.ModelForm):
    class Meta:
        model = JobAccomplishment
        fields = "__all__"
        exclude = ["id", "job"]


class SkillAndSkillLevelForm(forms.ModelForm):
    class Meta:
        model = SkillAndSkillLevel
        fields = ["text", "skill_level"]
        exclude = ["id", "personal_info"]
        widgets = {"skill_level": forms.Select(attrs={"class": "form-control"})}


class ProgrammingAreaForm(forms.ModelForm):
    PROGRAMMING_LANGUAGE_CHOICES = [
        ("HTML", "HTML"),
        ("CSS", "CSS"),
        ("JavaScript", "JavaScript"),
        ("TypeScript", "TypeScript"),
        ("React", "React"),
        ("Angular", "Angular"),
        ("Vue.js", "Vue.js"),
        ("JavaScript (Node.js)", "JavaScript (Node.js)"),
        ("Python (Django)", "Python (Django)"),
        ("Python (Flask)", "Python (Flask)"),
        ("Ruby (Ruby on Rails)", "Ruby (Ruby on Rails)"),
        ("Java (Spring)", "Java (Spring)"),
        ("PHP (Laravel)", "PHP (Laravel)"),
        ("C# (ASP.NET)", "C# (ASP.NET)"),
        ("Go (GoLang)", "Go (GoLang)"),
        ("Scala (Play Framework)", "Scala (Play Framework)"),
        ("Elixir (Phoenix)", "Elixir (Phoenix)"),
    ]
    programming_language_name = forms.ChoiceField(
        choices=PROGRAMMING_LANGUAGE_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    class Meta:
        model = ProgrammingArea
        fields = ["programming_area_name", "programming_language_name"]
        exclude = ["id", "personal_info"]
        widgets = {
            "programming_area_name ": forms.Select(attrs={"class": "form-control"}),
        }


class ProjectsForm(forms.ModelForm):
    class Meta:
        model = Projects
        fields = "__all__"
        exclude = ["id", "personal_info"]


class PublicationForm(forms.ModelForm):
    class Meta:
        model = Publication
        fields = "__all__"
        exclude = ["id", "personal_info"]
