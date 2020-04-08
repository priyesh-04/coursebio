from rest_framework import serializers
from .models import Category, Course

class CategoryModelSerializer(serializers.ModelSerializer):
		
	class Meta:
		model = Category
		fields = [
			'id',
			'image_url',
			'icon_name',
			'title',
			'slug',
			'timestamp',
			'updated',
		]


class CourseModelSerializer(serializers.ModelSerializer):
		
	class Meta:
		model = Course
		fields = [
			'id',
			'category',
			'subcategory',
			'provider',
			'image_url',
			'video_url',
			'title',
			'description',
			'author',
			'duration',
			'trial',
			'price',
			'level',
			'rating',
			'is_free',
			'certificate',
			'course_url',
			'popular',
			'slug',
			'timestamp',
			'updated',
		]
