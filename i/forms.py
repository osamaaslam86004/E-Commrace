from django import forms
from i.models import Review
from django.core.exceptions import ValidationError

from i.models import (
    ProductCategory,
    ComputerSubCategory,
    Electronics,
    ComputerAndTablets,
    ComputerAndTabletsBaseClass,
    Laptops,
    Tablets,
    Desktop,
    PowerAccessories,
    Adaptors,
    IsolatedTransformers,
    LineConditioners,
    PDUS,
    Servers,
    Monitors,
    LaptopAccessories,
    LaptopBattry,
    ScreenFilters,
    ScreenProtector,
    ChargersAndadaptors,
    LaptopBagsTypes,
    LaptopBags,
    LaptopBagSleeves,
    BagPacks,
    BriefCases,
    HardShellCases,
    MessengerAndShoulderBag,
    TabletsReplacementParts,
    FlexCables,
    LcdDisplayReplacementParts,
    Special_Features,
)


class ProductCategoryForm(forms.ModelForm):
    class Meta:
        model = ProductCategory
        fields = ["name"]


class ComputerSubCategoryForm(forms.ModelForm):
    class Meta:
        model = ComputerSubCategory
        fields = ["name"]


class ComputerAndTabletsForm(forms.ModelForm):
    class Meta:
        model = ComputerAndTablets
        fields = ["name"]

        widgets = {
            "name": forms.Select(attrs={"class": "custom-select"}),
        }

        help_texts = {
            "name": "Select the product sub-sub-category.",
        }


class ComputerAndTabletsBaseClassForm(forms.ModelForm):
    class Meta:
        model = ComputerAndTabletsBaseClass
        fields = "__all__"

    name = forms.CharField(
        label="Product Name",
        widget=forms.TextInput(attrs={"class": "form-control"}),
        error_messages={
            "required": "Product name is required.",
            "max_length": "Product name should not exceed 255 characters.",
        },
    )

    processor = forms.CharField(
        label="Processor",
        widget=forms.TextInput(attrs={"class": "form-control"}),
        error_messages={
            "required": "Processor details are required.",
            "max_length": "Processor details should not exceed 255 characters.",
        },
    )

    memory = forms.CharField(
        label="Memory",
        widget=forms.TextInput(attrs={"class": "form-control"}),
        error_messages={
            "required": "Memory details are required.",
            "max_length": "Memory details should not exceed 255 characters.",
        },
    )

    storage = forms.CharField(
        label="Storage",
        widget=forms.TextInput(attrs={"class": "form-control"}),
        error_messages={
            "required": "Storage details are required.",
            "max_length": "Storage details should not exceed 255 characters.",
        },
    )

    graphics_card = forms.CharField(
        label="Graphics Card",
        widget=forms.TextInput(attrs={"class": "form-control"}),
        error_messages={
            "required": "Graphics card details are required.",
            "max_length": "Graphics card details should not exceed 255 characters.",
        },
    )

    screen_size = forms.CharField(
        label="Screen Size",
        widget=forms.TextInput(attrs={"class": "form-control"}),
        error_messages={
            "required": "Screen size is required.",
            "max_length": "Screen size should not exceed 10 characters.",
        },
    )

    price = forms.DecimalField(
        label="Price (USD)",
        widget=forms.NumberInput(attrs={"class": "form-control"}),
        error_messages={
            "required": "Price is required.",
            "max_digits": "Price cannot have more than 10 digits.",
            "decimal_places": "Price should have a maximum of 2 decimal places.",
            "min_value": "Price must be greater than or equal to 1.",
            "max_value": "Price cannot exceed 999999.99.",
        },
    )


class LaptopsForm(forms.ModelForm):
    class Meta:
        model = Laptops
        fields = ["name"]


class TabletsForm(forms.ModelForm):
    class Meta:
        model = Tablets
        fields = ["name"]


class DesktopForm(forms.ModelForm):
    class Meta:
        model = Desktop
        fields = ["name"]


class ServersForm(forms.ModelForm):
    class Meta:
        model = Servers
        fields = "__all__"
        labels = {
            "name": "Server Name",
            "model": "Model",
            "cpu": "CPU",
            "ram": "RAM",
            "os": "Operating System",
            "cpu_count": "CPU Count",
            "graphics_card": "Graphics Card",
            "hard_disk": "Hard Disk",
            "flash_memory_size": "Flash Memory Size",
            "item_dimensions": "Item Dimensions",
            "item_weight": "Item Weight",
            "no_usb_port_two_zero": "No. of USB Ports (2.0)",
            "no_usb_port_three_zero": "No. of USB Ports (3.0)",
            "storage_controller": "Storage Controller",
            "network_controller": "Network Controller",
            "power_supply_type": "Power Supply Type",
            "price": "Price",
        }
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "model": forms.TextInput(attrs={"class": "form-control"}),
            "cpu": forms.TextInput(attrs={"class": "form-control"}),
            "ram": forms.TextInput(attrs={"class": "form-control"}),
            "os": forms.TextInput(attrs={"class": "form-control"}),
            "cpu_count": forms.NumberInput(attrs={"class": "form-control"}),
            "graphics_card": forms.TextInput(attrs={"class": "form-control"}),
            "hard_disk": forms.TextInput(attrs={"class": "form-control"}),
            "flash_memory_size": forms.TextInput(attrs={"class": "form-control"}),
            "item_dimensions": forms.TextInput(attrs={"class": "form-control"}),
            "item_weight": forms.NumberInput(attrs={"class": "form-control"}),
            "no_usb_port_two_zero": forms.NumberInput(attrs={"class": "form-control"}),
            "no_usb_port_three_zero": forms.NumberInput(
                attrs={"class": "form-control"}
            ),
            "storage_controller": forms.TextInput(attrs={"class": "form-control"}),
            "network_controller": forms.NumberInput(attrs={"class": "form-control"}),
            "power_supply_type": forms.TextInput(attrs={"class": "form-control"}),
            "price": forms.NumberInput(attrs={"class": "form-control"}),
        }
        help_texts = {
            "name": "Enter the name of the server product.",
        }
        error_messages = {
            "price": {
                "min_value": "Price must be greater than or equal to 1.",
                "max_value": "Price cannot exceed 999999.99.",
            },
        }


class SpecialFeaturesForm(forms.ModelForm):
    choose_special_features = forms.MultipleChoiceField(
        choices=Special_Features.SPECIAL_FEATURES_CHOICES,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Special_Features
        fields = ["choose_special_features"]


class MonitorsForm(forms.ModelForm):
    monitor_type_choices = [
        ("GAMING_MONITOR", "Gaming Monitor"),
        ("CARE_MONITOR", "Care Monitor"),
        ("HOME_OFFICE", "Home Office"),
    ]

    monitor_type = forms.ChoiceField(
        choices=monitor_type_choices,
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Monitor Type",
        help_text="Select the type of monitor.",
    )

    mounting_type_choices = [
        ("WALL_MOUNT", "Wall Mount"),
        ("DESK_MOUNT", "Desk Mount"),
    ]

    mounting_type = forms.ChoiceField(
        choices=mounting_type_choices,
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Mounting Type",
        help_text="Select the Mounting-type.",
    )

    max_display_resolution_choices = [
        ("1280x1024", "1280 x 1024"),
        ("1680x1050", "1680 x 1050"),
        ("1920x1080", "1920 x 1080"),
        ("1920x1200", "1920 x 1200"),
        ("2560x1080", "2560 x 1080"),
        ("2560x1440", "2560 x 1440"),
        ("3440x1440", "3440 x 1440"),
        ("3840x2160", "3840 x 2160"),
        ("800x600", "800 x 600"),
    ]

    max_display_resolution = forms.ChoiceField(
        choices=max_display_resolution_choices,
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Max. Display Resolution",
        help_text="Select the Maximum Display Resolution.",
    )

    refresh_rate_choices = [
        (240, "240 Hz"),
        (165, "165 Hz"),
        (160, "160 Hz"),
        (144, "144 Hz"),
        (120, "120 Hz"),
        (100, "100 Hz"),
        (75, "75 Hz"),
        (60, "60 Hz"),
    ]

    refresh_rate = forms.ChoiceField(
        choices=refresh_rate_choices,
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Refresh Rate",
        help_text="Select the Refresh Rate",
    )

    brand_choices = [
        ("SAMSUNG", "Samsung"),
        ("LG", "LG"),
        ("ASUS", "ASUS"),
        ("acer", "Acer"),
        ("Dell", "Dell"),
        ("ViewSonic", "ViewSonic"),
        ("msi", "MSI"),
        ("Spectre", "SPECTRE"),
    ]
    brand = forms.ChoiceField(
        choices=brand_choices,
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Brand Name",
        help_text="Select the Brand",
    )

    is_active = forms.TypedChoiceField(
        coerce=lambda x: x == "True",
        choices=[(True, "Active"), (False, "In Active")],
        widget=forms.RadioSelect(),
        required=False,
        initial=True,
        label="Choose the status of the book",
    )

    choose_special_features = forms.ModelMultipleChoiceField(
        queryset=Special_Features.objects.all(),
        widget=forms.CheckboxSelectMultiple(
            attrs={"class": "special-features-checkbox"}
        ),
    )

    class Meta:
        model = Monitors
        fields = [
            "name",
            "image_1",
            "image_2",
            "image_3",
            "is_active",
            "brand",
            "aspect_ratio",
            "max_display_resolution",
            "screen_size",
            "monitor_type",
            "refresh_rate",
            "mounting_type",
            "item_dimensions",
            "item_weight",
            "voltage",
            "color",
            "hdmi_port",
            "built_speakers",
            "price",
            "quantity_available",
            "choose_special_features",
        ]
        exclude = ["restock_threshold", "special_features"]
        labels = {
            "name": "Monitor Name",
            "aspect_ratio": "Aspect Ratio",
            "screen_size": "Screen Size",
            "item_dimensions": "Item Dimensions",
            "item_weight": "Item Weight",
            "voltage": "Voltage",
            "color": "Color",
            "hdmi_port": "HDMI Port",
            "built_speakers": "Built-in Speakers",
            "price": "Price",
            "quantity_available": "Quantity Available",
        }
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "aspect_ratio": forms.TextInput(attrs={"class": "form-control"}),
            "screen_size": forms.TextInput(attrs={"class": "form-control"}),
            "item_dimensions": forms.TextInput(attrs={"class": "form-control"}),
            "item_weight": forms.NumberInput(attrs={"class": "form-control"}),
            "voltage": forms.NumberInput(attrs={"class": "form-control"}),
            "color": forms.TextInput(attrs={"class": "form-control"}),
            "hdmi_port_": forms.NumberInput(attrs={"class": "form-control"}),
            "built_speakers": forms.TextInput(attrs={"class": "form-control"}),
            "price": forms.NumberInput(attrs={"class": "form-control"}),
            "quantity_available": forms.NumberInput(attrs={"class": "form-control"}),
        }
        help_texts = {
            "name": "Enter the name of the monitor product.",
        }
        error_messages = {
            "price": {
                "min_value": "Price must be greater than or equal to 1.",
                "max_value": "Price cannot exceed 999999.99.",
            },
        }

    # Do not comment this method : Not null contraint error will arise
    def clean_item_weight(self):
        item_weight = self.cleaned_data.get("item_weight")
        if item_weight < 0 or item_weight > 2147483647:
            raise forms.ValidationError(
                "Item weight must greater than 0 and less than 2147483647."
            )
        return item_weight

    def clean_price(self):
        price = self.cleaned_data.get("price")
        if price <= 0 or price > 9999999999:
            raise forms.ValidationError(
                "Item weight must greater than 0 and less than 9999999999."
            )
        return price

    # def clean_iamge_1(self):
    #     image_1 = self.cleaned_data.get("image_1")
    #     if image_1 is None:
    #         return image_1
    #     return image_1

    # def clean_iamge_2(self):
    #     image_2 = self.cleaned_data.get("image_2")
    #     if image_2 is None:
    #         return image_2
    #     return image_2

    # def clean_iamge_3(self):
    #     image_3 = self.cleaned_data.get("image_3")
    #     if image_3 is None:
    #         return image_3
    #     return image_3


class LaptopAccessoriesForm(forms.ModelForm):
    class Meta:
        model = LaptopAccessories
        fields = ["name"]
        labels = {
            "name": "Accessory Name",
        }
        widgets = {
            "name": forms.Select(attrs={"class": "form-control"}),
        }
        help_texts = {
            "name": "Select the type of laptop accessory.",
        }
        error_messages = {
            "name": {
                "unique": "This accessory already exists.",
            },
        }


class ScreenFiltersForm(forms.ModelForm):
    class Meta:
        model = ScreenFilters
        fields = [
            "name",
            "Color",
            "item_dimensions",
            "item_weight",
        ]
        labels = {
            "name": "Name",
            "Color": "Color",
            "item_dimensions": "Item Dimensions",
            "item_weight": "Item Weight",
        }
        widgets = {
            "Color": forms.TextInput(attrs={"placeholder": "Enter color..."}),
            "item_dimensions": forms.TextInput(
                attrs={"placeholder": "Enter dimensions..."}
            ),
            "item_weight": forms.TextInput(attrs={"placeholder": "Enter weight..."}),
        }
        help_texts = {
            "Color": "Enter the color of the screen filter.",
            "item_dimensions": "Specify the dimensions of the screen filter item.",
            "item_weight": "Enter the weight of the screen filter item in kilograms.",
        }


class ScreenProtectorForm(forms.ModelForm):
    class Meta:
        model = ScreenProtector
        fields = [
            "name",
            "screen_surface_description",
            "screen_size",
            "material",
            "compatible_devices",
        ]
        labels = {
            "name": "Name",
            "screen_surface_description": "Screen Surface Description",
            "screen_size": "Screen Size",
            "material": "Material",
            "compatible_devices": "Compatible Devices",
        }
        widgets = {
            "screen_surface_description": forms.TextInput(
                attrs={"placeholder": "Enter description..."}
            ),
            "screen_size": forms.TextInput(attrs={"placeholder": "Enter size..."}),
            "material": forms.TextInput(attrs={"placeholder": "Enter material..."}),
        }
        help_texts = {
            "screen_surface_description": "Describe the surface of the screen protector.",
            "screen_size": "Specify the size of the screen protector in inches.",
            "material": "Specify the material used for the screen protector.",
            "compatible_devices": "List compatible devices for this screen protector.",
        }

    def validate_special_features(value):
        if len(value) > 7:
            raise ValidationError("Select up to 7 choices.")


class LaptopBattryForm(forms.ModelForm):
    class Meta:
        model = LaptopBattry
        fields = [
            "compatible_for_laptop_model",
            "battery_cell_composition",
            "voltage",
        ]
        labels = {
            "compatible_for_laptop_model": "Compatible for Laptop Model",
            "battery_cell_composition": "Battery Cell Composition",
            "voltage": "Voltage",
        }
        widgets = {
            "compatible_for_laptop_model": forms.TextInput(
                attrs={"placeholder": "Enter compatible laptop models..."}
            ),
            "battery_cell_composition": forms.TextInput(
                attrs={"placeholder": "Enter battery cell composition..."}
            ),
            "voltage": forms.TextInput(attrs={"placeholder": "Enter voltage..."}),
        }
        help_texts = {
            "compatible_for_laptop_model": "List laptop models that this battery is compatible with.",
            "battery_cell_composition": "Describe the composition of the battery cells.",
            "voltage": "Specify the voltage of the battery.",
        }


class ChargersAndadaptorsForm(forms.ModelForm):
    class Meta:
        model = ChargersAndadaptors
        fields = [
            "compatible_devices",
            "compatible_phone_models",
            "color",
            "voltage",
            "watts",
            "connectivity_technology",
            "connector_type",
        ]
        labels = {
            "compatible_devices": "Compatible Devices",
            "compatible_phone_models": "Compatible Phone Models",
            "color": "Color",
            "voltage": "Voltage",
            "watts": "Watts",
            "connectivity_technology": "Connectivity Technology",
            "connector_type": "Connector Type",
        }
        widgets = {
            "compatible_devices": forms.TextInput(
                attrs={"placeholder": "Enter compatible devices..."}
            ),
            "compatible_phone_models": forms.TextInput(
                attrs={"placeholder": "Enter compatible phone models..."}
            ),
            "color": forms.TextInput(attrs={"placeholder": "Enter color..."}),
            "voltage": forms.TextInput(attrs={"placeholder": "Enter voltage..."}),
            "watts": forms.TextInput(attrs={"placeholder": "Enter watts..."}),
            "connectivity_technology": forms.TextInput(
                attrs={"placeholder": "Enter connectivity technology..."}
            ),
            "connector_type": forms.TextInput(
                attrs={"placeholder": "Enter connector type..."}
            ),
        }
        help_texts = {
            "compatible_devices": "List compatible devices for this charger or adaptor.",
            "compatible_phone_models": "List compatible phone models for this charger or adaptor.",
            "color": "Specify the color of the charger or adaptor.",
            "voltage": "Specify the voltage of the charger or adaptor.",
            "watts": "Specify the power rating in watts.",
            "connectivity_technology": "Describe the technology used for connectivity.",
            "connector_type": "Specify the type of connector used.",
        }


class LaptopBagsForm(forms.ModelForm):
    class Meta:
        model = LaptopBags
        fields = ["name"]
        labels = {
            "name": "Name",
            # 'slug': 'Slug',
        }
        # widgets = {
        # 'slug': forms.TextInput(attrs={'placeholder': 'Automatically generated'}),
        # }
        help_texts = {
            "name": "Select the type of laptop bag from the available options.",
            # 'slug': 'A slug will be automatically generated.',
        }


class LaptopBagsTypesForm(forms.ModelForm):
    class Meta:
        model = LaptopBagsTypes
        fields = [
            "name",
            "Color",
            "item_dimensions",
            "item_weight",
            "size",
            "material",
        ]
        labels = {
            "name": "Name",
            "Color": "Color",
            "item_dimensions": "Item Dimensions",
            "item_weight": "Item Weight",
            "size": "Size",
            "material": "Material",
        }
        widgets = {
            "Color": forms.TextInput(attrs={"placeholder": "Enter color..."}),
            "item_dimensions": forms.TextInput(
                attrs={"placeholder": "Enter dimensions..."}
            ),
            "item_weight": forms.TextInput(attrs={"placeholder": "Enter weight..."}),
            "size": forms.TextInput(attrs={"placeholder": "Enter size..."}),
            "material": forms.TextInput(attrs={"placeholder": "Enter material..."}),
        }
        help_texts = {
            "Color": "Specify the color of the laptop bag.",
            "item_dimensions": "Specify the dimensions of the laptop bag item.",
            "item_weight": "Enter the weight of the laptop bag item in kilograms.",
            "size": "Specify the size of the laptop bag.",
            "material": "Specify the material used for the laptop bag.",
        }


class LaptopBagSleevesForm(forms.ModelForm):
    class Meta:
        model = LaptopBagSleeves
        fields = [
            "form_factor",
            "shell_type",
            "compatible_devices",
        ]
        labels = {
            "form_factor": "Form Factor",
            "shell_type": "Shell Type",
            "compatible_devices": "Compatible Devices",
        }
        widgets = {
            "form_factor": forms.TextInput(
                attrs={"placeholder": "Enter form factor..."}
            ),
            "shell_type": forms.TextInput(attrs={"placeholder": "Enter shell type..."}),
            "compatible_devices": forms.Textarea(
                attrs={"placeholder": "Enter compatible devices..."}
            ),
        }
        help_texts = {
            "form_factor": "Specify the form factor of the laptop bag sleeve.",
            "shell_type": "Specify the type of shell used.",
            "compatible_devices": "List compatible devices for this laptop bag sleeve.",
        }


class BagPacksForm(forms.ModelForm):
    class Meta:
        model = BagPacks
        fields = [
            "total_capacity",
        ]
        labels = {
            "total_capacity": "Total Capacity",
        }
        widgets = {
            "total_capacity": forms.TextInput(
                attrs={"placeholder": "Enter total capacity..."}
            ),
        }
        help_texts = {
            "total_capacity": "Specify the total capacity of the bag pack.",
        }


class BriefCasesForm(forms.ModelForm):
    class Meta:
        model = BriefCases
        fields = [
            "total_capacity",
            "no_of_compartments",
        ]
        labels = {
            "total_capacity": "Total Capacity",
            "no_of_compartments": "Number of Compartments",
        }
        widgets = {
            "total_capacity": forms.TextInput(
                attrs={"placeholder": "Enter total capacity..."}
            ),
        }
        help_texts = {
            "total_capacity": "Specify the total capacity of the briefcase.",
            "no_of_compartments": "Enter the number of compartments in the briefcase.",
        }


class HardShellCasesForm(forms.ModelForm):
    class Meta:
        model = HardShellCases
        fields = [
            "capatible_devices",
            "form_factor",
            "shell_type",
        ]
        labels = {
            "capatible_devices": "Compatible Devices",
            "form_factor": "Form Factor",
            "shell_type": "Shell Type",
        }
        widgets = {
            "capatible_devices": forms.Textarea(
                attrs={"placeholder": "Enter compatible devices..."}
            ),
            "form_factor": forms.TextInput(
                attrs={"placeholder": "Enter form factor..."}
            ),
            "shell_type": forms.TextInput(attrs={"placeholder": "Enter shell type..."}),
        }
        help_texts = {
            "capatible_devices": "List compatible devices for this hardshell case.",
            "form_factor": "Specify the form factor of the hardshell case.",
            "shell_type": "Specify the type of shell used.",
        }


class MessengerAndShoulderBagForm(forms.ModelForm):
    class Meta:
        model = MessengerAndShoulderBag
        fields = [
            "special_feature",
        ]
        labels = {
            "special_feature": "Special Feature",
        }
        widgets = {
            "special_feature": forms.TextInput(
                attrs={"placeholder": "Enter special feature..."}
            ),
        }
        help_texts = {
            "special_feature": "Specify the special features of the messenger or shoulder bag.",
        }


class TabletsReplacementPartsForm(forms.ModelForm):
    class Meta:
        model = TabletsReplacementParts
        fields = ["name"]
        labels = {
            "name": "Name",
        }
        help_texts = {
            "name": "Select the type of tablet replacement parts from the available options.",
        }


class FlexCablesForm(forms.ModelForm):
    class Meta:
        model = FlexCables
        fields = [
            "cable_type",
            "device_name",
            "brand_name",
            "flex_cable_for_replacement_part",
            "price",
        ]
        labels = {
            "cable_type": "Cable Type",
            "device_name": "Device Name",
            "brand_name": "Brand Name",
            "flex_cable_for_replacement_part": "Flex Cable for Replacement Part",
            "price": "Price",
        }
        widgets = {
            "device_name": forms.TextInput(
                attrs={"placeholder": "Enter device name..."}
            ),
            "flex_cable_for_replacement_part": forms.TextInput(
                attrs={"placeholder": "Enter flex cable for replacement part..."}
            ),
        }
        help_texts = {
            "cable_type": "Select the type of flex cable.",
            "device_name": "Enter the name of the device for which this flex cable is used.",
            "brand_name": "Specify the brand name.",
            "flex_cable_for_replacement_part": "Specify the compatible part for replacement.",
            "price": "Enter the price of the flex cable.",
        }


class LcdDisplayReplacementPartsForm(forms.ModelForm):
    class Meta:
        model = LcdDisplayReplacementParts
        fields = [
            "brand",
            "compatibility",
            "product_model_name",
            "item_weight",
            "item_dimensions",
            "screen_size",
            "color",
            "price",
        ]
        labels = {
            "brand": "Brand",
            "compatibility": "Compatibility",
            "product_model_name": "Product Model Name",
            "item_weight": "Item Weight",
            "item_dimensions": "Item Dimensions",
            "screen_size": "Screen Size",
            "color": "Color",
            "price": "Price",
        }
        widgets = {
            "compatibility": forms.Textarea(
                attrs={"placeholder": "Enter compatibility..."}
            ),
            "product_model_name": forms.Textarea(
                attrs={"placeholder": "Enter product model name..."}
            ),
        }
        help_texts = {
            "brand": "Specify the brand of the LCD display replacement part.",
            "compatibility": "List the compatible devices for this replacement part.",
            "product_model_name": "Specify the supported product model names.",
            "item_weight": "Enter the item weight.",
            "item_dimensions": "Specify the item dimensions.",
            "screen_size": "Specify the screen size.",
            "color": "Specify the color of the replacement part.",
            "price": "Enter the price of the replacement part.",
        }


class ElectronicsForm(forms.ModelForm):
    class Meta:
        model = Electronics
        fields = ["name"]


class PowerAccessoriesForm(forms.ModelForm):
    class Meta:
        model = PowerAccessories
        fields = ["name"]
        labels = {
            "name": "Power Accessories",
        }
        help_texts = {
            "name": "Choose the power accessory.",
        }


class AdaptorsForm(forms.ModelForm):
    class Meta:
        model = Adaptors
        fields = [
            "connectivity_technology",
            "connector_type",
            "compatible_devices",
            "product_description",
            "name",
            "price",
        ]
        labels = {
            "connectivity_technology": "Connectivity Technology",
            "connector_type": "Connector Type",
            "compatible_devices": "Compatible Devices",
            "product_description": "Product Description",
            "name": "Product Name",
            "price": "Product Price",
        }
        widgets = {
            "connectivity_technology": forms.TextInput(attrs={"class": "form-control"}),
            "connector_type": forms.TextInput(attrs={"class": "form-control"}),
            "compatible_devices": forms.Textarea(attrs={"class": "form-control"}),
            "product_description": forms.Textarea(attrs={"class": "form-control"}),
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "price": forms.NumberInput(attrs={"class": "form-control"}),
        }
        help_texts = {
            "name": "Enter the name of the adaptors product.",
        }
        error_messages = {
            "price": {
                "min_value": "Price must be greater than or equal to 1.",
                "max_value": "Price cannot exceed 999999.99.",
            },
        }


class IsolatedTransformersForm(forms.ModelForm):
    class Meta:
        model = IsolatedTransformers
        fields = [
            "power_source",
            "current_ratings",
            "frequency",
            "product_description",
            "name",
            "price",
        ]
        labels = {
            "power_source": "Power Source",
            "current_ratings": "Current Ratings",
            "frequency": "Frequency",
            "product_description": "Product Description",
            "name": "Product Name",
            "price": "Product Price",
        }
        widgets = {
            "power_source": forms.TextInput(attrs={"class": "form-control"}),
            "current_ratings": forms.TextInput(attrs={"class": "form-control"}),
            "frequency": forms.TextInput(attrs={"class": "form-control"}),
            "product_description": forms.Textarea(attrs={"class": "form-control"}),
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "price": forms.NumberInput(attrs={"class": "form-control"}),
        }
        help_texts = {
            "name": "Enter the name of the isolated transformer product.",
        }
        error_messages = {
            "price": {
                "min_value": "Price must be greater than or equal to 1.",
                "max_value": "Price cannot exceed 999999.99.",
            },
        }


class LineConditionersForm(forms.ModelForm):
    class Meta:
        model = LineConditioners
        fields = [
            "voltage_ratings",
            "current_ratings",
            "battery_cell_composition",
            "product_description",
            "name",
            "price",
        ]
        labels = {
            "voltage_ratings": "Voltage Ratings",
            "current_ratings": "Current Ratings",
            "battery_cell_composition": "Battery Cell Composition",
            "product_description": "Product Description",
            "name": "Product Name",
            "price": "Product Price",
        }
        widgets = {
            "voltage_ratings": forms.TextInput(attrs={"class": "form-control"}),
            "current_ratings": forms.TextInput(attrs={"class": "form-control"}),
            "battery_cell_composition": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "product_description": forms.Textarea(attrs={"class": "form-control"}),
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "price": forms.NumberInput(attrs={"class": "form-control"}),
        }
        help_texts = {
            "name": "Enter the name of the line conditioner product.",
        }
        error_messages = {
            "price": {
                "min_value": "Price must be greater than or equal to 1.",
                "max_value": "Price cannot exceed 999999.99.",
            },
        }


class PDUsForm(forms.ModelForm):
    class Meta:
        model = PDUS
        fields = [
            "style",
            "size",
            "configuration",
            "product_description",
            "name",
            "price",
        ]
        labels = {
            "style": "Style",
            "size": "Size",
            "configuration": "Configuration",
            "product_description": "Product Description",
            "name": "Product Name",
            "price": "Product Price",
        }
        widgets = {
            "style": forms.Select(attrs={"class": "form-control"}),
            "size": forms.Select(attrs={"class": "form-control"}),
            "configuration": forms.Select(attrs={"class": "form-control"}),
            "product_description": forms.Textarea(attrs={"class": "form-control"}),
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "price": forms.NumberInput(attrs={"class": "form-control"}),
        }
        help_texts = {
            "name": "Enter the name of the PDU product.",
        }
        error_messages = {
            "price": {
                "min_value": "Price must be greater than or equal to 1.",
                "max_value": "Price cannot exceed 999999.99.",
            },
        }


# Define a custom star rating field
class StarRatingField(forms.FloatField):
    widget = forms.RadioSelect(
        choices=(
            (0.5, "0.5"),
            (1.0, "1"),
            (1.5, "1.5"),
            (2.0, "2"),
            (2.5, "2.5"),
            (3.0, "3"),
            (3.5, "3.5"),
            (4.0, "4"),
            (4.5, "4.5"),
            (5.0, "5"),
        )
    )


# Create the ReviewForm using the custom star rating field


class ReviewForm(forms.ModelForm):
    rating = StarRatingField()

    class Meta:
        model = Review
        fields = ["rating", "image_1", "image_2", "text"]
