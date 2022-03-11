from django.contrib import admin
from django.utils import timezone
from django.db.models import Count
from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter
from rangefilter.filter import DateTimeRangeFilter

from django_summernote.admin import SummernoteModelAdmin

from main.models import Blog, Comment, Category


class CommentInline(admin.TabularInline):

    model = Comment
    fields = ('text', 'is_active')
    extra = 1
    classes = ('collapse',)


class BlogAdmin(SummernoteModelAdmin):

    list_display = ('title', 'date_created', 'last_modified',
                    'is_draft', 'days_since_creation', 'no_of_comments')
    list_filter = (
        'is_draft',
        ('date_created', DateTimeRangeFilter),
    )
    search_fields = ('title', )
    list_per_page = 50
    actions = ('set_blogs_to_published',)
    date_hierarchy = 'date_created'

    # fields = (('title', 'slug'), 'body', 'is_draft')
    fieldsets = (
        (None, {
            'fields': (('title', 'slug'), 'body'),
        }),
        ('Advanced options', {
            'fields': ('is_draft', 'categories'),
            'description': 'Options to configure blog creation',
            'classes': ('collapse')
        }),
    )

    summernote_fields = ('body',)
    inlines = (CommentInline, )
    filter_horizontal = ('categories',)

    prepopulated_fields = {'slug': ('title',)}
    ordering = ('title', '-date_created',)

    def days_since_creation(self, blog):
        diff = timezone.now() - blog.date_created
        return diff.days

    days_since_creation.short_description = 'Days Active'

    def get_queryset(self, request):

        queryset = super().get_queryset(request)
        queryset = queryset.annotate(comments_count=Count('comments'))
        return queryset

    def no_of_comments(self, blog):
        return blog.comments_count

    no_of_comments.admin_order_field = 'comments_count'

    def get_ordering(self, request):
        if request.user.is_superuser:
            return ('title', '-date_created')
        return ('title',)

    def set_blogs_to_published(self, request, queryset):

        count = queryset.update(is_draft=False)
        self.message_user(
            request, 'The selected blogs have been published.'.format(count))
    set_blogs_to_published.short_description = 'Mark selected blogs as published'


class CommentAdmin(admin.ModelAdmin):

    list_display = ('blog', 'text', 'date_created', 'is_active')
    list_editable = ('is_active',)
    list_filter = (
        ('blog', RelatedDropdownFilter),
    )


admin.site.register(Blog, BlogAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Category)
