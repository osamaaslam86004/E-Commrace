import factory
from factory.django import DjangoModelFactory
from faker import Faker
from Homepage.models import CustomUser
from cv_api.models import PersonalInfo, TokensForUser
from faker import Faker
from cv_api.models import (
    PersonalInfo,
    Overview,
    Education,
    Job,
    SkillAndSkillLevel,
    ProgrammingArea,
    Projects,
    Publication,
    JobAccomplishment,
)
from random import choice
from datetime import datetime
from datetime import datetime, timedelta
import random


class CustomUserOnlyFactory(DjangoModelFactory):
    class Meta:
        model = CustomUser

    username = factory.Faker("user_name")
    email = factory.LazyAttribute(lambda _: Faker().unique.email())
    image = factory.Faker("image_url")
    user_google_id = None
    password = factory.PostGenerationMethodCall("set_password", "testpass123")


class PersonalInfoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PersonalInfo

    user_id_for_personal_info = factory.SubFactory(CustomUserOnlyFactory)
    api_user_id_for_cv = factory.Sequence(lambda n: n + 1)  # Generates unique integers
    api_id_of_cv = factory.Sequence(lambda n: n + 1)  # Generates unique integers
    id = factory.Sequence(lambda n: n + 1)
    status = "Active"
    first_name = factory.Faker("first_name")
    middle_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    suffix = factory.Faker("suffix")
    locality = factory.Faker("city")
    region = factory.Faker("state_abbr")
    title = factory.Faker("job")
    email = factory.Faker("email")
    linkedin = factory.Faker("url")
    facebook = factory.Faker("url")
    github = factory.Faker("url")
    site = factory.Faker("url")
    twittername = factory.Faker("user_name")


class TokensForUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TokensForUser

    user = factory.SubFactory(CustomUserOnlyFactory)
    access_token = factory.Faker("sha256")
    refresh_token = factory.Faker("sha256")


class OverviewFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Overview

    personal_info = factory.SubFactory(PersonalInfoFactory)
    text = factory.Faker("text")


class EducationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Education

    personal_info = factory.SubFactory(PersonalInfoFactory)
    name = factory.Faker("word")
    location = factory.Faker("city")
    schoolurl = factory.Faker("url")
    # Generate dates in YYYY-MM-DD format
    education_start_date = factory.LazyFunction(
        lambda: (datetime.now() - timedelta(days=random.randint(1000, 2000)))
        .date()
        .isoformat()
    )
    education_end_date = factory.LazyFunction(
        lambda: (datetime.now() - timedelta(days=random.randint(0, 999)))
        .date()
        .isoformat()
    )
    degree = factory.Faker("word")
    description = factory.Faker("paragraph")


class JobFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Job

    personal_info_job = factory.SubFactory(PersonalInfoFactory)
    company = factory.Faker("company")
    companyurl = factory.Faker("url")
    location = factory.Faker("city")
    title = factory.Faker("job")
    description = factory.Faker("paragraph")
    # Generate dates in YYYY-MM-DD format
    job_start_date = factory.LazyFunction(
        lambda: (datetime.now() - timedelta(days=random.randint(1000, 2000)))
        .date()
        .isoformat()
    )
    job_end_date = factory.LazyFunction(
        lambda: (datetime.now() - timedelta(days=random.randint(0, 999)))
        .date()
        .isoformat()
    )
    is_current = factory.Faker("boolean")
    is_public = factory.Faker("boolean")
    image = ""  # Setting the image field to an empty string          ==> null= False, blank=True
    # image = None  # Setting the image field to None to keep it empty ==> null=True, blank=True
    # image = factory.django.ImageField()


class JobAccomplishmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = JobAccomplishment

    job = factory.SubFactory(JobFactory)
    job_accomplishment = factory.Faker("paragraph")


class SkillAndSkillLevelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SkillAndSkillLevel

    personal_info = factory.SubFactory(PersonalInfoFactory)
    text = factory.Faker("word")
    skill_level = factory.Faker(
        "random_element",
        elements=[choice[0] for choice in SkillAndSkillLevel.SKILL_LEVEL_CHOICES],
    )


class ProgrammingAreaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProgrammingArea

    personal_info = factory.SubFactory(PersonalInfoFactory)
    programming_area_name = factory.Faker(
        "random_element", elements=["FRONTEND", "BACKEND"]
    )

    @factory.lazy_attribute
    def programming_language_name(self):
        if self.programming_area_name == "FRONTEND":
            return choice(ProgrammingArea.FRONTEND_PROGRAMMING_LANGUAGE_CHOICES)[0]
        else:
            return choice(ProgrammingArea.BACKEND_PROGRAMMING_LANGUAGE_CHOICES)[0]


class ProjectsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Projects

    personal_info = factory.SubFactory(PersonalInfoFactory)
    project_name = factory.Faker("word")
    short_description = factory.Faker("paragraph")
    long_description = factory.Faker("paragraph")
    link = factory.Faker("url")


class PublicationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Publication

    personal_info = factory.SubFactory(PersonalInfoFactory)
    title = factory.Faker("sentence")
    authors = factory.Faker("name")
    journal = factory.Faker("word")
    year = factory.Faker("year")
    link = factory.Faker("url")
