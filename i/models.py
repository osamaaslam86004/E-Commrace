from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from Homepage.models import CustomUser
from ckeditor.fields import RichTextField


class ProductCategory(models.Model):
    product_category_type_choices = (
        ("COMPUTER", "computer"),
        ("ELECTRONICS", "electronics"),
        ("BOOKS", "Books"),
    )
    name = models.CharField(max_length=255, choices=product_category_type_choices)


class ComputerSubCategory(models.Model):
    product_sub_category_type_choices = (
        ("LAPTOP_ACCESSORIES", "laptop accessories"),
        ("COMPUTERS_AND_TABLETS", "computer and tablets"),
        ("TABLETS_REPLACEMENT_PARTS", "tablets replacement parts"),
        ("SERVERS", "servers"),
        ("MONITORS", "monitors"),
    )
    name = models.CharField(
        max_length=255, unique=True, choices=product_sub_category_type_choices
    )
    product_category = models.ForeignKey(
        ProductCategory, on_delete=models.CASCADE, related_name="comp_product_category"
    )


class ComputerAndTablets(models.Model):
    product_sub_sub_category_type_choices = (
        ("LAPTOPS", "laptop"),
        ("TABLETS", "tablets"),
        ("DESKTOP", "desktop"),
    )

    name = models.CharField(
        max_length=255, unique=True, choices=product_sub_sub_category_type_choices
    )
    sub_category = models.ForeignKey(
        ComputerSubCategory,
        on_delete=models.CASCADE,
        related_name="comp_tab_comp_sub_category",
    )

    def __str__(self):
        return self.name


class ComputerAndTabletsBaseClass(models.Model):
    name = models.CharField(max_length=255)
    processor = models.TextField(max_length=255)
    memory = models.TextField(max_length=255)
    storage = models.TextField(max_length=255)
    graphics_card = models.TextField(max_length=255)
    screen_size = models.CharField(max_length=10)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(
                limit_value=1, message="Price must be greater than or equal to 1."
            ),
            MaxValueValidator(
                limit_value=999999.99, message="Price cannot exceed 999999.99."
            ),
        ],
    )

    def __str__(self):
        return self.name


class Laptops(ComputerAndTabletsBaseClass):
    computer_and_tablets_category = models.ForeignKey(
        ComputerAndTablets, on_delete=models.CASCADE, related_name="laptops_comp_tab"
    )

    def __str__(self):
        return self.name


class Tablets(ComputerAndTabletsBaseClass):
    computer_and_tablets_category = models.ForeignKey(
        ComputerAndTablets, on_delete=models.CASCADE, related_name="tablets_comp_tab"
    )

    def __str__(self):
        return self.name


class Desktop(ComputerAndTabletsBaseClass):
    computer_and_tablets_category = models.ForeignKey(
        ComputerAndTablets, on_delete=models.CASCADE, related_name="desktop_comp_tab"
    )
    desktop_id = models.AutoField(primary_key=True, default=0)

    def __str__(self):
        return self.name


class Servers(models.Model):
    name = models.CharField(max_length=255, blank=False)
    model = models.CharField(max_length=255, blank=True)
    cpu = models.CharField(max_length=255, blank=False)
    ram = models.CharField(max_length=255, blank=False)
    os = models.CharField(max_length=255, blank=False)
    cpu_cout = models.PositiveIntegerField(blank=True)
    graphics_card = models.CharField(max_length=255, blank=False)
    hard_disk = models.CharField(max_length=255, blank=False)
    flah_memory_size = models.CharField(max_length=255, blank=True)
    item_dimensions = models.CharField(max_length=255, blank=True)
    item_weight = models.PositiveIntegerField(blank=True)
    no_usb_port_two_zero = models.IntegerField(blank=False)
    no_usb_port_three_zero = models.IntegerField(blank=False)
    storage_controller = models.CharField(max_length=255, blank=True)
    network_controller = models.IntegerField(blank=False)
    power_supply_type = models.CharField(max_length=255, blank=True)
    server_id = models.AutoField(primary_key=True)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(
                limit_value=1, message="Price must be greater than or equal to 1."
            ),
            MaxValueValidator(
                limit_value=999999.99, message="Price cannot exceed 999999.99."
            ),
        ],
    )
    product_category = models.ForeignKey(
        ProductCategory,
        on_delete=models.CASCADE,
        related_name="server_product_category",
    )

    def __str__(self):
        return self.name


class Special_Features(models.Model):
    SPECIAL_FEATURES_CHOICES = [
        ("adaptive_sync", "Adaptive Sync"),
        ("anti_glare_screen", "Anti Glare Screen"),
        ("blue_light_filter", "Blue Light Filter"),
        ("built_in_speakers", "Built-In Speakers"),
        ("built_in_webcam", "Built-In Webcam"),
        ("curved", "Curved"),
        ("eye_care", "Eye Care"),
        ("flicker_free", "Flicker-Free"),
        ("frameless", "Frameless"),
        ("height_adjustment", "Height Adjustment"),
        ("high_dynamic_range", "High Dynamic Range"),
        ("lightweight", "Lightweight"),
        ("pivot_adjustment", "Pivot Adjustment"),
        ("portable", "Portable"),
        ("swivel_adjustment", "Swivel Adjustment"),
        ("tilt_adjustment", "Tilt Adjustment"),
        ("touchscreen", "Touchscreen"),
        ("usb_hub", "USB Hub"),
    ]
    name = models.CharField(
        choices=SPECIAL_FEATURES_CHOICES,
        max_length=255,
        unique=True,
        default="Frameless",
    )

    id = models.AutoField(primary_key=True)

    def __str__(self):
        return self.get_name_display()


class Monitors(models.Model):
    image_1 = models.ImageField(upload_to="images/", null=True)
    image_2 = models.ImageField(upload_to="images/", null=True)
    image_3 = models.ImageField(upload_to="images/", null=True)
    is_active = models.BooleanField(default=True)
    name = models.CharField(max_length=255, blank=False)
    brand = models.CharField(max_length=255, blank=True)
    aspect_ratio = models.CharField(max_length=255, blank=False)
    max_display_resolution = models.CharField(max_length=255, blank=False)
    screen_size = models.CharField(max_length=255, blank=False)
    monitor_type = models.CharField(max_length=255, default="HOME_OFFICE")
    refresh_rate = models.CharField(max_length=255, blank=False)
    mounting_type = models.CharField(max_length=255, blank=False)
    item_dimensions = models.CharField(max_length=255, blank=True)
    item_weight = models.PositiveIntegerField()
    voltage = models.IntegerField(blank=False, default=220)
    color = models.CharField(max_length=50, blank=True)
    special_features = models.ManyToManyField(Special_Features)
    hdmi_port = models.FloatField(max_length=255, blank=False, default=2.0)
    built_speakers = models.CharField(max_length=255, blank=True, default="yes")
    monitor_id = models.AutoField(primary_key=True)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=False,
        validators=[
            MinValueValidator(
                limit_value=1, message="Price must be greater than or equal to 1."
            ),
            MaxValueValidator(
                limit_value=999999.99, message="Price cannot exceed 999999.99."
            ),
        ],
    )
    quantity_available = models.PositiveIntegerField(blank=False, default=15)
    restock_threshold = models.PositiveIntegerField(default=9)
    Product_Category = models.ForeignKey(
        ProductCategory,
        on_delete=models.CASCADE,
        related_name="Monitors_Product_Category",
    )
    Computer_SubCategory = models.ForeignKey(
        ComputerSubCategory,
        on_delete=models.CASCADE,
        related_name="Monitors_Computer_Subcategory",
    )
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="monitor_user"
    )

    def __str__(self):
        return f"{self.name}- {self.max_display_resolution} Pixels- {self.mounting_type}- {self.monitor_type}- {self.screen_size}"


class LaptopAccessories(models.Model):
    product_sub__sub_category_type_choices = (
        ("SCREEN_FILTERS", "screen filters"),
        ("SCREEN_PROTECTORS", "screen protectors"),
        ("BATTRIES", "battries"),
        ("BAGS", "bags"),
        ("CHARGERS_AND_ADAPTORS", "chargers and adpators"),
    )

    name = models.CharField(
        max_length=255, unique=True, choices=product_sub__sub_category_type_choices
    )
    product_category = models.ForeignKey(
        ProductCategory,
        on_delete=models.CASCADE,
        related_name="laptop_accessories_product_category",
    )


class ScreenFilters(models.Model):
    name = models.CharField(max_length=255, unique=False)
    Color = models.CharField(
        max_length=50,
    )
    item_dimensions = models.CharField(max_length=50)
    item_weight = models.CharField(max_length=25)
    product_category = models.ForeignKey(
        LaptopAccessories,
        on_delete=models.CASCADE,
        related_name="screen_filters_laptop_accessories",
    )

    def __str__(self):
        return self.name


class ScreenProtector(models.Model):
    name = models.CharField(max_length=255, unique=False)
    screen_surface_description = models.CharField(max_length=255, null=True)
    screen_size = models.CharField(max_length=50)
    material = models.CharField(max_length=255)
    compatible_devices = models.TextField(max_length=255)
    product_category = models.ForeignKey(
        LaptopAccessories,
        on_delete=models.CASCADE,
        related_name="screen_protector_laptop_accessories",
    )

    def __str__(self):
        return self.name


class LaptopBattry(models.Model):
    compatible_for_laptop_model = models.TextField(max_length=255, unique=False)
    battery_cell_composition = models.CharField(max_length=255)
    voltage = models.CharField(max_length=255)
    product_category = models.ForeignKey(
        LaptopAccessories,
        on_delete=models.CASCADE,
        related_name="laptop_battry_laptop_accessories",
    )

    def __str__(self):
        return self.name


class ChargersAndadaptors(models.Model):
    compatible_devices = models.TextField(max_length=255, unique=False, blank=False)
    compatible_phone_models = models.TextField(
        max_length=255, unique=False, blank=False
    )
    color = models.CharField(max_length=25, blank=True)
    voltage = models.CharField(max_length=255, blank=False)
    watts = models.CharField(max_length=255, blank=False)
    connectivity_technology = models.CharField(max_length=255, blank=False)
    connector_type = models.CharField(max_length=255, blank=False)
    product_category = models.ForeignKey(
        LaptopAccessories,
        on_delete=models.CASCADE,
        related_name="charger_laptop_accessories",
    )

    def __str__(self):
        return self.name


class LaptopBags(models.Model):
    product_sub__sub_category_type_choices = (
        ("SLEEVES_BAGS", "Sleeves Bags"),
        ("BRIEFCASE", "Briefcase"),
        ("MESSENGER_AND_SHOULDER_BAGS", "Messenger and shoulder Bags"),
        ("BAGPACKS", "Bagpacks"),
        ("HARDSHELL", "Hardshell"),
    )

    name = models.CharField(
        max_length=255, unique=True, choices=product_sub__sub_category_type_choices
    )
    slug = models.SlugField(unique=False, blank=True, editable=False)
    product_category = models.ForeignKey(
        LaptopAccessories,
        on_delete=models.CASCADE,
        related_name="laptop_bags_laptop_accessories",
    )

    def __str__(self):
        return self.name


class LaptopBagsTypes(models.Model):
    name = models.CharField(max_length=255, unique=False)
    Color = models.CharField(max_length=50, blank=True)
    item_dimensions = models.CharField(max_length=50, blank=True)
    item_weight = models.CharField(max_length=25, blank=True)
    size = models.CharField(max_length=50, blank=True)
    material = models.CharField(max_length=25, blank=True)

    def __str__(self):
        return self.name


class LaptopBagSleeves(models.Model):
    form_factor = models.CharField(max_length=50, blank=True)
    shell_type = models.CharField(max_length=25, blank=True)
    compatible_devices = models.TextField(max_length=255, unique=False, blank=False)
    laptop_accessories = models.ForeignKey(
        LaptopAccessories,
        on_delete=models.CASCADE,
        related_name="laptop_bag_sleeves_laptop_accessories",
    )
    laptop_bag_types = models.OneToOneField(
        LaptopBagsTypes,
        on_delete=models.CASCADE,
        related_name="laptop_bag_sleeves_laptop_bag_type",
    )

    def __str__(self):
        return self.form_factor


class BagPacks(models.Model):
    total_capacity = models.CharField(max_length=25, blank=False)
    laptop_accessories = models.ForeignKey(
        LaptopAccessories,
        on_delete=models.CASCADE,
        related_name="laptop_bag_paks_laptop_accessories",
    )
    laptop_bag_types = models.OneToOneField(
        LaptopBagsTypes,
        on_delete=models.CASCADE,
        related_name="laptop_bag_packs_laptop_bag_type",
    )

    def __str__(self):
        return self.form_total_capacity


class BriefCases(models.Model):
    total_capacity = models.CharField(max_length=25, blank=False)
    no_of_compartments = models.PositiveIntegerField()
    laptop_accessories = models.ForeignKey(
        LaptopAccessories,
        on_delete=models.CASCADE,
        related_name="brief_cases_laptop_accessories",
    )
    laptop_bag_types = models.OneToOneField(
        LaptopBagsTypes,
        on_delete=models.CASCADE,
        related_name="laptop_cases_laptop_bag_type",
    )

    def __str__(self):
        return self.no_of_compartments


class HardShellCases(models.Model):
    capatible_devices = models.TextField(max_length=255, blank=False)
    form_factor = models.CharField(max_length=50, blank=False)
    shell_type = models.CharField(max_length=50, blank=False)
    laptop_accessories = models.ForeignKey(
        LaptopAccessories,
        on_delete=models.CASCADE,
        related_name="hard_shell_cases_laptop_accessories",
    )
    laptop_bag_types = models.OneToOneField(
        LaptopBagsTypes,
        on_delete=models.CASCADE,
        related_name="hard_shell_cases_laptop_bag_type",
    )

    def __str__(self):
        return self.capatible_devices


class MessengerAndShoulderBag(models.Model):
    special_feature = models.CharField(max_length=255, blank=False)
    laptop_accessories = models.ForeignKey(
        LaptopAccessories,
        on_delete=models.CASCADE,
        related_name="messenger_and_shoulder_bag_laptop_accessories",
    )
    laptop_bag_types = models.OneToOneField(
        LaptopBagsTypes,
        on_delete=models.CASCADE,
        related_name="messenger_and_shoulder_bag_laptop_bag_type",
    )

    def __str__(self):
        return self.special_feature


class TabletsReplacementParts(models.Model):
    product_sub_category_type_choices = (
        ("FLEX_CABLES", "flex cables"),
        ("LCD_DISPLAYS", "Lcd displays"),
    )

    name = models.CharField(
        max_length=255, unique=True, choices=product_sub_category_type_choices
    )
    product_category = models.ForeignKey(
        ProductCategory,
        on_delete=models.CASCADE,
        related_name="tab_replace_product_category",
    )
    ComputerSubCategory = models.ForeignKey(
        ComputerSubCategory,
        on_delete=models.CASCADE,
        related_name="tab_replace_computersubcategory",
    )

    def __str__(self):
        return self.name


class FlexCables(models.Model):
    flex_cables_type_choices = (
        ("MOBILES", "flex cables"),
        ("CAMERA", "Lcd displays"),
        ("DRONE", "drone"),
        ("TABLETS", "tablets"),
    )

    cable_type = models.CharField(
        max_length=255, unique=True, choices=flex_cables_type_choices
    )
    device_name = models.CharField(max_length=255, unique=False)
    brand_name = models.CharField(max_length=150, unique=False, blank=False)
    flex_cable_for_replacement_part = models.CharField(max_length=255, blank=False)
    flex_cables_id = models.AutoField(primary_key=True)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(
                limit_value=1, message="Price must be greater than or equal to 1."
            ),
            MaxValueValidator(
                limit_value=999999.99, message="Price cannot exceed 999999.99."
            ),
        ],
    )
    product_category = models.OneToOneField(
        TabletsReplacementParts,
        on_delete=models.CASCADE,
        related_name="cable_type_table_replacement_parts",
    )

    def __str__(self):
        return self.cable_type


class LcdDisplayReplacementParts(models.Model):
    brand = models.CharField(max_length=255, blank=False)
    compatibility = models.TextField(max_length=255, blank=True)
    product_model_name = models.TextField(max_length=255, blank=True)
    item_weight = models.PositiveIntegerField()
    item_dimensions = models.CharField(max_length=255, blank=True)
    screen_size = models.FloatField(blank=True)
    color = models.CharField(max_length=25, blank=True)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(
                limit_value=1, message="Price must be greater than or equal to 1."
            ),
            MaxValueValidator(
                limit_value=999999.99, message="Price cannot exceed 999999.99."
            ),
        ],
    )
    product_category = models.OneToOneField(
        TabletsReplacementParts,
        on_delete=models.CASCADE,
        related_name="full_lcd_display_table_replacement_parts",
    )

    def __str__(self):
        return self.compatibility


class Electronics(models.Model):
    product_category_type_choices = (("POWER_ACCESSORIES", "power accessories"),)

    name = models.CharField(
        max_length=255, unique=True, choices=product_category_type_choices
    )
    product_category = models.ForeignKey(
        ProductCategory,
        on_delete=models.CASCADE,
        related_name="electronics_product_category",
    )


class PowerAccessories(models.Model):
    product_category_type_choices = (
        ("ADAPTORS", "Adaptors"),
        ("ISOLATED TRANSFORMERS", "Isolated transformers"),
        ("PDUS", "PDUs"),
        ("LINE CONDITIONERS", "line conditoners"),
    )

    name = models.CharField(
        max_length=255, unique=True, choices=product_category_type_choices
    )
    PowerAccessories_id = models.AutoField(primary_key=True)
    product_category = models.ForeignKey(
        Electronics,
        on_delete=models.CASCADE,
        related_name="power_accessories_electronics",
    )


class Adaptors(models.Model):
    connectivity_technology = models.CharField(max_length=50, blank=True)
    connector_type = models.CharField(max_length=255, blank=True)
    compatible_devices = models.TextField(max_length=255, blank=True)
    product_description = models.TextField(max_length=1000, blank=True)
    name = models.CharField(max_length=255, unique=False)
    adaptors_id = models.AutoField(primary_key=True)
    product_category = models.ForeignKey(
        PowerAccessories,
        on_delete=models.CASCADE,
        related_name="adaptors_power_accessories",
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(
                limit_value=1, message="Price must be greater than or equal to 1."
            ),
            MaxValueValidator(
                limit_value=999999.99, message="Price cannot exceed 999999.99."
            ),
        ],
    )


class IsolatedTransformers(models.Model):
    power_source = models.CharField(max_length=50, blank=True)
    current_ratings = models.CharField(max_length=15, blank=True)
    frequency = models.CharField(max_length=15, blank=True)
    product_description = models.TextField(max_length=1000, blank=True)
    name = models.CharField(max_length=255, unique=False)
    isolated_transformers_id = models.AutoField(primary_key=True)
    product_category = models.ForeignKey(
        PowerAccessories,
        on_delete=models.CASCADE,
        related_name="isolated_transformers_power_accessories",
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(
                limit_value=1, message="Price must be greater than or equal to 1."
            ),
            MaxValueValidator(
                limit_value=999999.99, message="Price cannot exceed 999999.99."
            ),
        ],
    )


class LineConditioners(models.Model):
    voltage_ratings = models.CharField(max_length=50, blank=True)
    current_ratings = models.CharField(max_length=15, blank=True)
    battery_cell_composition = models.CharField(max_length=25, blank=True)
    product_description = models.TextField(max_length=1000, blank=True)
    name = models.CharField(max_length=255, unique=False)
    line_conditioners_id = models.AutoField(primary_key=True)
    product_category = models.ForeignKey(
        PowerAccessories,
        on_delete=models.CASCADE,
        related_name="line_conditioners_power_accessories",
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(
                limit_value=1, message="Price must be greater than or equal to 1."
            ),
            MaxValueValidator(
                limit_value=999999.99, message="Price cannot exceed 999999.99."
            ),
        ],
    )


class PDUS(models.Model):
    outlets = (
        ("6", "6"),
        ("8", "8"),
        ("14", "14"),
        ("16", "16"),
        ("20", "20"),
        ("24", "24"),
        ("28", "28"),
        ("30", "30"),
        ("32", "32"),
        ("36", "36"),
        ("38", "38"),
        ("48", "48"),
    )

    size = (
        ("15", "15"),
        ("20", "20"),
        ("30", "30"),
        ("20A/240V", "20A/240V"),
        ("30A/240V", "30A/240V"),
        ("32A/240V", "32A/240V"),
        ("16A/240V", "16A/240V"),
    )

    pdu_config = (
        ("STANDARD", "standard"),
        ("SURGE_PROTECTION", "surge_protection"),
        (
            "CONTROLLABLE_OUTLETS/NETWORKING_CARD",
            "Controllable_Outlets/Networking_Card",
        ),
        ("CONTROLLABLE_OUTLETS/DUAL_LOAD_BOOK", "Controllable_Outlets/Dual Load Banks"),
    )

    style = models.CharField(max_length=50, choices=outlets)
    size = models.CharField(max_length=15, choices=size)
    configuration = models.CharField(max_length=50, choices=pdu_config)
    product_description = models.TextField(max_length=1000, blank=True)
    name = models.CharField(max_length=255, unique=False)
    pdu_id = models.AutoField(primary_key=True)
    product_category = models.ForeignKey(
        PowerAccessories, on_delete=models.CASCADE, related_name="pdu_power_accessories"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(
                limit_value=1, message="Price must be greater than or equal to 1."
            ),
            MaxValueValidator(
                limit_value=999999.99, message="Price cannot exceed 999999.99."
            ),
        ],
    )


class Review(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="user_review", null=True
    )
    product = models.ForeignKey(
        Monitors, on_delete=models.CASCADE, related_name="product_review"
    )
    rating = models.DecimalField(max_digits=2, decimal_places=1)
    status = models.BooleanField(default="1", null=True)
    text = RichTextField()
    image_1 = models.ImageField(
        upload_to="images/",
        null=True,
        default="https://res.cloudinary.com/dh8vfw5u0/image/upload/v1702231959/rmpi4l8wsz4pdc6azeyr.ico",
    )

    image_2 = models.ImageField(
        upload_to="images/",
        null=True,
        default="https://res.cloudinary.com/dh8vfw5u0/image/upload/v1702231959/rmpi4l8wsz4pdc6azeyr.ico",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name} Review"
