from django.contrib import admin
from .models import Product, Review, Comment, Report, UserProfile


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display  = ("id", "name", "category", "elo_score")
    list_filter   = ("category",)
    search_fields = ("name",)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display  = ("id", "user", "product_a", "product_b",
                     "preferred_product", "status", "allow_comments")
    list_filter   = ("status", "allow_comments", "product_a__category")
    search_fields = ("user__username", "product_a__name", "product_b__name")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "review", "user", "created_at")
    search_fields = ("review__id", "user__username", "text")


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display  = ("id", "review", "reporter", "status", "created_at")
    list_filter   = ("status",)
    search_fields = ("review__id", "reporter__username")


@admin.register(UserProfile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "is_admin")
    list_editable = ("is_admin",)
