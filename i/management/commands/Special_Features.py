
from django.core.management.base import BaseCommand
from i.models import Special_Features

class Command(BaseCommand):
    help = 'Populate Special_Features model with predefined choices'

    def handle(self, *args, **options):
        SPECIAL_FEATURES_CHOICES = [
        ('adaptive_sync', 'Adaptive Sync'),
        ('anti_glare_screen', 'Anti Glare Screen'),
        ('blue_light_filter', 'Blue Light Filter'),
        ('built_in_speakers', 'Built-In Speakers'),
        ('built_in_webcam', 'Built-In Webcam'),
        ('curved', 'Curved'),
        ('eye_care', 'Eye Care'),
        ('flicker_free', 'Flicker-Free'),
        ('frameless', 'Frameless'),
        ('height_adjustment', 'Height Adjustment'),
        ('high_dynamic_range', 'High Dynamic Range'),
        ('lightweight', 'Lightweight'),
        ('pivot_adjustment', 'Pivot Adjustment'),
        ('portable', 'Portable'),
        ('swivel_adjustment', 'Swivel Adjustment'),
        ('tilt_adjustment', 'Tilt Adjustment'),
        ('touchscreen', 'Touchscreen'),
        ('usb_hub', 'USB Hub'),
    ]

        for choice in SPECIAL_FEATURES_CHOICES:
            name, _ = Special_Features.objects.get_or_create(name=choice[0])
            name.save()

        self.stdout.write(self.style.SUCCESS('Special Features populated successfully'))
