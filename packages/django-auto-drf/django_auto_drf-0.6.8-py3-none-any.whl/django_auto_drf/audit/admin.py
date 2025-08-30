
from django.contrib import admin, messages
from django.contrib.auth.models import Group
from django.urls import path, reverse
from django.shortcuts import render, redirect
from django import forms
from django.db import transaction

from .models import MissingPermission

class GroupSelectForm(forms.Form):
    group = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        required=True,
        label="Gruppo di destinazione",
        help_text="Il permesso negato verrà aggiunto a questo gruppo."
    )

@admin.register(MissingPermission)
class MissingPermissionAdmin(admin.ModelAdmin):
    list_display = ("user", "permission", "hits", "last_seen")
    list_filter = ("permission__content_type__app_label", "permission__codename")
    search_fields = ("user__username", "user__email", "permission__codename", "note")
    readonly_fields = ("user", "permission", "hits", "first_seen", "last_seen", "note")

    actions = [
        "grant_permission_to_user",
        "clear_notes",
        "assign_permissions_to_group",
    ]

    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False

    @admin.action(description="Concedi questo permesso all’utente (ATTENZIONE)")
    def grant_permission_to_user(self, request, queryset):
        updated = 0
        with transaction.atomic():
            for rec in queryset:
                rec.user.user_permissions.add(rec.permission)
                updated += 1
        if updated:
            self.message_user(request, f"Assegnati {updated} permessi agli utenti selezionati.", level=messages.SUCCESS)
        else:
            self.message_user(request, "Nessun permesso assegnato.", level=messages.WARNING)

    @admin.action(description="Pulisci la nota")
    def clear_notes(self, request, queryset):
        queryset.update(note="")
        self.message_user(request, "Note pulite.", level=messages.INFO)

    @admin.action(description="Aggiungi questo permesso a un Gruppo…")
    def assign_permissions_to_group(self, request, queryset):
        ids = ",".join(str(pk) for pk in queryset.values_list("pk", flat=True))
        url = f"{reverse('admin:audit_missingpermission_assign_to_group')}?ids={ids}"
        return redirect(url)

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                "assign-to-group/",
                self.admin_site.admin_view(self.assign_to_group_view),
                name="audit_missingpermission_assign_to_group",
            ),
        ]
        return custom + urls

    def assign_to_group_view(self, request):
        ids_param = request.GET.get("ids") if request.method == "GET" else request.POST.get("ids")
        if not ids_param:
            self.message_user(request, "Nessun elemento selezionato.", level=messages.WARNING)
            return redirect("admin:audit_missingpermission_changelist")

        try:
            ids = [int(x) for x in ids_param.split(",") if x.strip()]
        except ValueError:
            self.message_user(request, "Lista ID non valida.", level=messages.ERROR)
            return redirect("admin:audit_missingpermission_changelist")

        qs = MissingPermission.objects.filter(pk__in=ids)

        if request.method == "POST":
            form = GroupSelectForm(request.POST)
            if form.is_valid():
                group = form.cleaned_data["group"]
                with transaction.atomic():
                    count_added = 0
                    for rec in qs.select_related("permission"):
                        group.permissions.add(rec.permission)
                        count_added += 1
                self.message_user(
                    request,
                    f"Assegnati {count_added} permessi al gruppo “{group.name}”.",
                    level=messages.SUCCESS,
                )
                return redirect("admin:audit_missingpermission_changelist")
        else:
            form = GroupSelectForm()

        context = {
            **self.admin_site.each_context(request),
            "title": "Aggiungi permessi selezionati a un Gruppo",
            "form": form,
            "ids": ids_param,
            "queryset": qs,
        }
        return render(request, "admin/audit_assign_to_group.html", context)
