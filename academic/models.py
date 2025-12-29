from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


#================== subject model =========================
class Subject(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name="Subject Name"
    )

    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Subject Code"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created On"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Last Updated On"
    )

    def __str__(self):
        return f"{self.name} ({self.code})"



# ================= Session Model ==================
class Session(models.Model):
    """
    Example:
        2024–2025
        2025–2026
    """
    name = models.CharField(max_length=20, unique=True, verbose_name="Academic Session")
    start_date = models.DateField()
    end_date = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    


# ================= Section Model ==================
class Section(models.Model):
    """
    Example:
        Section A
        Section B
        Blue, Red, Science Batch etc.
    """
    name = models.CharField(max_length=50, verbose_name="Section Name")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"
    


#========================== Class Model ======================
class Class(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Class Name"
    )

    class_code = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(99)  # max 2 digits
        ],
        verbose_name="Class Code"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created Date"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Last Updated Date"
    )

    class Meta:
        verbose_name = "Class"
        verbose_name_plural = "Classes"   # Admin menu name will show correctly

    def __str__(self):
        return f"{self.name} ({self.class_code})"
