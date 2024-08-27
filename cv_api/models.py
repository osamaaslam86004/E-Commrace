from django.db import models
from datetime import time, date
from Homepage.models import CustomUser

# Create your models here.
class PersonalInfo(models.Model):

    user_id_for_personal_info = models.ForeignKey(CustomUser, null = True, on_delete = models.CASCADE)
    api_user_id_for_cv = models.IntegerField(null=True, blank=False)
    api_id_of_cv = models.IntegerField( blank=True, null = True)
    status = models.CharField(max_length=25, null=True, blank=True)
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=255)
    middle_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    suffix = models.CharField(max_length=255, blank=True, help_text="e.g. PhD")
    locality = models.CharField(max_length=255, help_text="e.g. city such as Boston", blank=True)
    region = models.CharField(max_length=255, help_text="e.g. MA or Italy", blank=True)
    title = models.CharField(max_length=255, help_text="e.g. Developer", blank=True)
    email = models.EmailField(blank=True)
    linkedin = models.URLField(blank=True)
    facebook = models.URLField(blank=True)
    github = models.URLField(blank=True)
    site = models.URLField(blank=True)
    twittername = models.CharField(max_length=100, blank=True)

    def full_name(self):
        return " ".join([self.first_name, self.middle_name, self.last_name])

    def __str__(self):
        return self.full_name()


class TokensForUser(models.Model):
    user = models.OneToOneField(CustomUser, null = True, on_delete = models.CASCADE,
                                    related_name = "tokens_for_user")
    access_token = models.CharField(max_length=1000, blank=False , null= True)
    refresh_token = models.CharField(max_length=1000, blank=False , null= True)




class Overview(models.Model):

    personal_info = models.OneToOneField(
        PersonalInfo, on_delete=models.CASCADE, null=True, related_name="overview"
    )
    id = models.AutoField(primary_key=True)
    text = models.TextField()

    class Meta:
        verbose_name_plural = "02. Overview"

    def __str__(self):
        return self.text[0:40] + "..."


class Education(models.Model):
    personal_info = models.ForeignKey(
        PersonalInfo, on_delete=models.CASCADE, null=True, related_name="education"
    )
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=250)
    location = models.CharField(max_length=250,blank=True)
    schoolurl = models.URLField("School URL", blank=True)
    education_start_date = models.DateField(null=True)
    education_end_date = models.DateField(null=True)
    degree = models.TextField(blank=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "03. Education"
        ordering = ["-education_end_date", "id"]

    def edu_date_range(self):
        return " - ".join(
            ["(", self.formatted_start_date(), self.formatted_end_date(), ")"]
        )

    def full_start_date(self):
        return self.start_date.strftime("%Y-%m-%d")

    def full_end_date(self):
        if self.end_date == None:
            return time.strftime("%Y-%m-%d", time.localtime())
        else:
            return self.end_date.strftime("%Y-%m-%d")

    def formatted_start_date(self):
        return self.start_date.strftime("%b %Y")

    def formatted_end_date(self):
        if self.end_date == None:
            return "Present"
        else:
            return self.end_date.strftime("%b %Y")

    def __str__(self):
        return self.name


class Job(models.Model):
    personal_info_job = models.OneToOneField(
        PersonalInfo, on_delete=models.CASCADE, null=True, related_name="job"
    )
    id = models.AutoField(primary_key=True)
    company = models.CharField(max_length=250)
    companyurl = models.URLField("Company URL", blank=True)
    location = models.CharField(max_length=250, blank=True)
    title = models.CharField(max_length=250, blank=True)
    description = models.TextField(blank=True)
    job_start_date = models.DateField( null=True)
    job_end_date = models.DateField( null=True)
    is_current = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)
    image = models.CharField(
        max_length=250,
        blank=True,
        help_text="path to company image, local or otherwise",
    )

    class Meta:
        db_table = "jobs"
        verbose_name_plural = "04. Jobs"
        ordering = ["-job_end_date", "id"]

    def job_date_range(self):
        return " - ".join(
            ["(", self.formatted_start_date(), self.formatted_end_date(), ")"]
        )

    def full_start_date(self):
        if self.start_date is None:
            return None
        return self.start_date.strftime("%Y-%m-%d")

    def full_end_date(self):
        if self.is_current is True:
            return time.strftime("%Y-%m-%d", time.localtime())
        else:
            return self.end_date.strftime("%Y-%m-%d")

    def formatted_start_date(self):
        if self.start_date is None:
            return None
        return self.start_date.strftime("%b %Y")

    def formatted_end_date(self):
        if self.is_current == True or self.end_date is None:
            return "Present"
        else:
            return self.end_date.strftime("%b %Y")

    def __str__(self):
        return self.company


class JobAccomplishment(models.Model):
    id = models.AutoField(primary_key=True)
    job_accomplishment = models.TextField()
    job = models.OneToOneField(
        Job, on_delete=models.CASCADE, related_name="accomplishment"
    )

    class Meta:
        verbose_name_plural = "05. Job Accomplishments"
        db_table = "jobaccomplishment"
        ordering = ["id"]

    def __str__(self):
        return " - ".join([self.job.company, self.description[0:50] + "..."])


class SkillAndSkillLevel(models.Model):
    SKILL_LEVEL_CHOICES = (
        ("Beginner", "Beginner"),
        ("Intermediate", "Intermediate"),
        ("Advanced", "Advanced"),
        ("Expert", "Expert"),
    )
    personal_info = models.ForeignKey(
        PersonalInfo, on_delete=models.CASCADE, null=True, related_name="skill"
    )
    id = models.AutoField(primary_key=True)
    text = models.TextField()
    skill_level = models.CharField(
        max_length=25, null=True, choices=SKILL_LEVEL_CHOICES
    )

    class Meta:
        verbose_name_plural = "07. Skills"
        ordering = ["id"]

    def __str__(self):
        return " - ".join([self.skill_level, self.text])


class ProgrammingArea(models.Model):
    PROGRAMMING_AREA_CHOICES = (
        ("FRONTEND", "Frontend"),
        ("BACKEND", "Backend"),
    )

    FRONTEND_PROGRAMMING_LANGUAGE_CHOICES = [
        ("HTML", "HTML"),
        ("CSS", "CSS"),
        ("JavaScript", "JavaScript"),
        ("TypeScript", "TypeScript"),
        ("React", "React"),
        ("Angular", "Angular"),
        ("Vue.js", "Vue.js"),
    ]

    BACKEND_PROGRAMMING_LANGUAGE_CHOICES = [
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

    personal_info = models.ForeignKey(
        PersonalInfo,
        on_delete=models.CASCADE,
        null=True,
        related_name="programming_area",
    )
    id = models.AutoField(primary_key=True)
    programming_area_name = models.CharField(
        max_length=25, choices=PROGRAMMING_AREA_CHOICES, null=True
    )
    programming_language_name = models.CharField(max_length=25, null=True)

    class Meta:
        verbose_name_plural = "08. Programming areas"
        ordering = ["programming_area_name"]

    def __str__(self):
        return f"{self.programming_area_name} - {self.programming_language_name}"


class Projects(models.Model):
    personal_info = models.ForeignKey(
        PersonalInfo,
        on_delete=models.CASCADE,
        null=True,
        related_name="projects",
    )
    id = models.AutoField(primary_key=True)
    project_name = models.CharField(max_length=255)
    short_description = models.TextField(
        blank=True, help_text="Text shown in project list"
    )
    long_description = models.TextField(
        blank=True, help_text="Text shown in modals appearing when clicking on images"
    )
    link = models.URLField(blank=True)

    def save(self, *args, **kwargs):
        if not self.long_description:
            self.long_description = self.short_description
        super(Projects, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "12. Projects"

    def __str__(self):
        return " - ".join(
            [self.project_name, self.link, self.short_description[0:50] + "..."]
        )



class Publication(models.Model):
    personal_info = models.ForeignKey(
        PersonalInfo,
        on_delete=models.CASCADE,
        null=True,
        related_name="publications",
    )
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=250)
    authors = models.TextField(blank=True)
    journal = models.CharField(max_length=150, blank=True)
    year = models.IntegerField(default=date.today().year, blank= True)
    link = models.URLField("Publication URL", blank=True)

    class Meta:
        verbose_name_plural = "14. Publications"
        ordering = ["-year"]

    def __str__(self):
        return " - ".join(
            [str(self.id), str(self.year), str(self.order), self.journal[0:10] + "..."]
        )

