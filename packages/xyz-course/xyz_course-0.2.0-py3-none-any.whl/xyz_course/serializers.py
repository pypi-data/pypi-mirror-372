# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals

from xyz_restful.mixins import IDAndStrFieldSerializerMixin
from xyz_util.datautils import auto_code
from rest_framework import serializers

from . import models


class CourseSerializer(IDAndStrFieldSerializerMixin, serializers.ModelSerializer):
    category_name = serializers.CharField(source="category", read_only=True)
    class Meta:
        model = models.Course
        fields = '__all__'

    def validate_code(self, value):
        if value is None:
            value = auto_code(self.validated_data['name'])
        return value


class CourseNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Course
        fields = ('name',)


class CourseOutlineSerializer(serializers.ModelSerializer):
    outline_list = serializers.ListField(read_only=True)
    class Meta:
        model = models.Course
        fields = ('id', 'name', 'outline_list')



class CategorySerializer(IDAndStrFieldSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = '__all__'


class ChapterSerializer(IDAndStrFieldSerializerMixin, serializers.ModelSerializer):
    course_name = serializers.CharField(source="course", read_only=True)
    class Meta:
        model = models.Chapter
        exclude = ('order_num',)


class PassSerializer(IDAndStrFieldSerializerMixin, serializers.ModelSerializer):
    course_name = serializers.CharField(source="course.name", read_only=True)
    user_name = serializers.CharField(source="user.get_full_name", read_only=True)
    class Meta:
        model = models.Pass
        exclude = ()