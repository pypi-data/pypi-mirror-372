from django.contrib import admin
from django.contrib.admin.utils import quote
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.utils.http import urlencode


class RecentTabularInline(admin.TabularInline):
    model = None
    fk_name = None
    extra = 0
    can_delete = False
    show_change_link = True
    maximum_number_of_related_rows_to_display = 5
    template = "admin/edit_inline/recent_tabular.html"

    def get_formset(self, request, obj=None, **kwargs):
        base_formset_class = super().get_formset(request, obj, **kwargs)
        limit_for_number_of_rows_to_display = self.maximum_number_of_related_rows_to_display
        inline_admin_instance = self

        class LimitedRecentInlineFormSet(base_formset_class):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

                parent_object_for_formset = self.instance
                foreign_key_field_name_resolved_by_formset = base_formset_class.fk.name

                # Expose the display limit to templates/JS via data attribute
                self.template_limit_for_number_of_rows_to_display = limit_for_number_of_rows_to_display

                content_type_for_related_model = ContentType.objects.get_for_model(inline_admin_instance.model)
                admin_changelist_url_name = (
                    f"admin:{content_type_for_related_model.app_label}_{content_type_for_related_model.model}_changelist"
                )
                base_url_for_related_changelist = reverse(admin_changelist_url_name)

                if parent_object_for_formset and getattr(parent_object_for_formset, "pk", None):
                    query_dict_for_foreign_key_filter = {
                        f"{foreign_key_field_name_resolved_by_formset}__id__exact": quote(parent_object_for_formset.pk),
                    }
                    self.template_filtered_changelist_url_for_parent_object = (
                        f"{base_url_for_related_changelist}?{urlencode(query_dict_for_foreign_key_filter)}"
                    )
                    related_manager_accessor_name = base_formset_class.fk.remote_field.get_accessor_name()
                    related_manager_for_parent_object = getattr(
                        parent_object_for_formset,
                        related_manager_accessor_name,
                    )
                    self.template_total_count_of_all_related_rows_for_parent_object = related_manager_for_parent_object.count()
                else:
                    self.template_filtered_changelist_url_for_parent_object = ""
                    self.template_total_count_of_all_related_rows_for_parent_object = 0

            def get_queryset(self):
                queryset_already_filtered_by_foreign_key = super().get_queryset()
                return queryset_already_filtered_by_foreign_key[:limit_for_number_of_rows_to_display]

        return LimitedRecentInlineFormSet

    class Media:
        js = ("admin/js/viewall_inlines.js",)
