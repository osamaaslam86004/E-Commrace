import django_filters
from i.models import Monitors, Special_Features
from i.forms import MonitorsForm
from django.db.models import Q
from django import forms


class MonitorsFilter(django_filters.FilterSet):
    monitor_type = django_filters.ChoiceFilter(
        choices=MonitorsForm.monitor_type_choices
    )
    mounting_type = django_filters.ChoiceFilter(
        choices=MonitorsForm.mounting_type_choices
    )
    max_display_resolution = django_filters.ChoiceFilter(
        choices=MonitorsForm.max_display_resolution_choices
    )
    refresh_rate = django_filters.ChoiceFilter(
        choices=MonitorsForm.refresh_rate_choices
    )
    brand = django_filters.ChoiceFilter(choices=MonitorsForm.brand_choices)
    special_features = django_filters.ModelMultipleChoiceFilter(
        field_name="special_features__id",  # Filter by IDs instead of objects
        to_field_name="id",  # Use primary key (ID) for filtering
        queryset=Special_Features.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        conjoined=True,  # when set to False, the filter applies an OR operation. Setting conjoined=True
        #    is useful when you want to narrow down results based on multiple selections,
        #    ensuring that the queryset only includes items that meet all the specified
        #    criteria. By default it is True
    )

    class Meta:
        model = Monitors
        fields = {
            "monitor_type": ["exact"],
            "mounting_type": ["exact"],
            "max_display_resolution": ["exact"],
            "refresh_rate": ["exact"],
            "brand": ["exact"],
            "special_features": ["exact"],
        }

    def filter_queryset(self, queryset):
        special_features = self.form.cleaned_data.get("special_features")

        q_objects = Q()

        if special_features:
            # Extract IDs from Special_Features objects
            special_feature_ids = [sf.id for sf in special_features]
            q_objects |= Q(special_features__id__in=special_feature_ids)

        # Apply other filters similarly
        for name, value in self.form.cleaned_data.items():
            if value and name != "special_features":
                q_objects |= Q(**{f"{name}__exact": value})

        return queryset.filter(q_objects)


"""
#######################################################################################
 This will work if special_features=django_filter.Charfilter(
                                        field_name = special_features__name,
                                        lookup_expr = 'icontains')
###########################################################################################
    def filter_queryset(self, queryset):
        special_features = self.form.cleaned_data.get('special_features')

        q_objects_icontains = Q()
        q_objects_exact = Q()

        if special_features:
            q_objects_icontains |= Q(special_features__name__icontains=special_features)

        # Apply other filters similarly
        for name, value in self.form.cleaned_data.items():
            if value and name != 'special_features':
                q_objects_exact &= Q(**{f"{name}__exact": value})

        return queryset.filter(q_objects_icontains | q_objects_exact)

"""
