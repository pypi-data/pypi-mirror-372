# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from xyz_auth.authentications import add_token_for_user
from xyz_restful.mixins import BatchActionMixin
from xyz_util.statutils import do_rest_stat_action

from . import models, serializers, importers, helper, stats
from rest_framework import viewsets, decorators, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from xyz_restful.decorators import register
import django_filters

__author__ = 'denishuang'


@register()
class TeacherViewSet(viewsets.ModelViewSet):
    queryset = models.Teacher.objects.all()
    serializer_class = serializers.TeacherSerializer
    filterset_fields = {
        'id': ['in', 'exact'],
        'name': ['exact'],
        'user': ['exact']
    }
    search_fields = ('name', 'code')
    ordering_fields = ('name', 'code')

    @decorators.action(['get'], detail=False)
    def stat(self, request):
        return do_rest_stat_action(self, stats.stats_teacher)


    @decorators.action(['post'], detail=False)
    def batch_create_from_tags(self, request):
        tags = request.data['tags']
        ts = helper.create_teachers_by_tags(tags)
        serializer = self.get_serializer(ts, many=True)
        return Response(serializer.data)

@register()
class GradeViewSet(viewsets.ModelViewSet):
    queryset = models.Grade.objects.all()
    serializer_class = serializers.GradeSerializer

    @decorators.action(['post'], detail=False)
    def gen_default(self, request):
        from . import helper
        if not self.get_queryset().exists():
            helper.gen_default_grades()
        return Response({'detail': 'ok'})


@register()
class SessionViewSet(viewsets.ModelViewSet):
    queryset = models.Session.objects.all()
    serializer_class = serializers.SessionSerializer
    search_fields = ('name', 'number')
    filterset_fields = {
        'id': ['in', 'exact'],
        'stage': ['in', 'exact'],
        'end_date': ['gte', 'lte', 'gt', 'lt'],
        'begin_date': ['gte', 'lte', 'gt', 'lt'],
        'year': ['exact', 'gte', 'lte', 'gt', 'lt']
    }

    @decorators.action(['post'], detail=False)
    def gen_default(self, request):
        from . import helper
        if not self.get_queryset().exists():
            helper.gen_default_session(-1)
            helper.gen_default_session(0)
        return Response({'detail': 'ok'})


@register()
class ClassViewSet(viewsets.ModelViewSet):
    queryset = models.Class.objects.all()
    serializer_class = serializers.ClassSerializer
    search_fields = ('name', 'code', 'tags')
    filterset_fields = {
        'id': ['in', 'exact'],
        'name': ['exact', 'endswith', 'in'],
        'code': ['in', 'exact'],
        'stage': ['exact'],
        'major': ['exact'],
        'college': ['exact'],
        'entrance_session': ['in', 'exact'],
        'grade': ['in', 'exact'],
        'primary_teacher': ['exact'],
    }

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.ClassListSerializer
        return super(ClassViewSet, self).get_serializer_class()

    @decorators.action(['get'], detail=False)
    def similar(self, request):
        q = request.query_params.get('q')
        import Levenshtein
        from django.db.models import F
        from xyz_util.modelutils import CharCorrelation
        qset = self.filter_queryset(self.get_queryset()).values('name', a=CharCorrelation([F('name'), q])).filter(
            a__gt=0).order_by('-a').values_list('name', 'a')[:10]
        aa = [(Levenshtein.ratio(n, q), c, n) for n, c in qset]
        aa.sort(reverse=True)
        ss = [c for a, b, c in aa if a > 0.5]
        return Response({'similar': ss})

    @decorators.action(['get'], detail=False)
    def stat(self, request):
        return do_rest_stat_action(self, stats.stats_class)

    @decorators.action(['get'], detail=False)
    def sumary(self, request):
        qset = self.filter_queryset(self.get_queryset())
        dl = []
        dl.append('班级,学生数,课程数,课程'.split(','))
        for c in qset:
            dl.append([c.name, c.students.count(), c.courses.count(),
                       ",".join(list(c.courses.values_list('name', flat=True)))])
        return Response({'data': dl})


@register()
class MajorViewSet(viewsets.ModelViewSet):
    queryset = models.Major.objects.all()
    serializer_class = serializers.MajorSerializer
    search_fields = ('name', 'code')
    filterset_fields = {
        'code': ['exact'],
        'name': ['exact', 'in'],
        'id': ['in', 'exact'],
    }


@register()
class CollegeViewSet(viewsets.ModelViewSet):
    queryset = models.College.objects.all()
    serializer_class = serializers.CollegeSerializer
    search_fields = ('name', 'code')
    filterset_fields = ('code', 'name',)


@register()
class ClassCourseViewSet(BatchActionMixin, viewsets.ModelViewSet):
    queryset = models.ClassCourse.objects.all()
    serializer_class = serializers.ClassCourseSerializer
    search_fields = ('clazz__name', 'course__name')
    filterset_fields = {
        'id': ['in', 'exact'],
        'clazz': ['exact'],
        'course': ['exact'],
        'teacher': ['exact'],
        'is_active': ['exact'],
        'begin_date': ['range'],
        'end_date': ['range'],
    }

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.ClassCourseListSerializer
        return super(ClassCourseViewSet, self).get_serializer_class()


    @decorators.action(['POST'], detail=False)
    def batch_set_teacher(self, request):
        return self.do_batch_action('teacher', request.data.get('teacher'))

    @decorators.action(['POST'], detail=False)
    def batch_active(self, request):
        return self.do_batch_action('is_active', True)


@register()
class StudentViewSet(BatchActionMixin, viewsets.ModelViewSet):
    queryset = models.Student.objects.all()
    serializer_class = serializers.StudentSerializer
    search_fields = ('name', 'number', 'code')
    filterset_fields = {
        'id': ['in', 'exact'],
        'grade': ['exact'],
        'entrance_session': ['exact'],
        # 'class': ['exact', 'in'],
        'number': ['exact', 'in'],
        'is_active': ['exact'],
        'is_bind': ['exact'],
        'is_formal': ['exact'],
        'stage': ['exact'],
        'class__id': ['exact', 'in'],
        'class__college': ['exact'],
        'class__major': ['exact'],
        'class__tags': ['exact', 'in'],
        'class__entrance_session': ['exact', 'in'],
        'user': ['exact', 'in'],
        'create_time': ['range']
    }
    ordering_fields = ('name', 'number', 'create_time', 'grade')

    def get_permissions(self):
        if self.action in ['binding', 'trial_application']:
            return [IsAuthenticated()]
        return super(StudentViewSet, self).get_permissions()

    @decorators.action(['post'], detail=False)
    def pre_import(self, request):
        importer = importers.StudentImporter()
        data = importer.clean(importer.get_excel_data(request.data['file']))
        return Response(data)

    @decorators.action(['post'], detail=False)
    def post_import(self, request):
        importer = importers.StudentImporter()
        student, created = importer.import_one(request.data)
        return Response(self.get_serializer(instance=student).data,
                        status=created and status.HTTP_201_CREATED or status.HTTP_200_OK)

    @decorators.action(['POST'], detail=False)
    def batch_active(self, request):
        return self.do_batch_action('is_active', True)

    @decorators.action(['POST'], detail=False, permission_classes=[IsAuthenticated])
    def trial_application(self, request):
        helper.apply_to_be_student(request.user, request.data)
        return Response({'detail': 'ok'})

    @decorators.action(['post'], detail=False, permission_classes=[IsAuthenticated])
    def binding(self, request):
        serializer = serializers.StudentBindingSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            schools = serializer.save()
            data = serializer.data
            data['schools'] = schools
            add_token_for_user(data, request.user)
            return Response(data)
        else:
            return Response({'detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @decorators.action(['POST'], detail=False)
    def batch_unbind(self, request):
        return self.do_batch_action(helper.unbind)

    @decorators.action(['POST'], detail=False)
    def batch_reset_password(self, request):
        return self.do_batch_action(helper.reset_password)

    @decorators.action(['post'], detail=False)
    def unbind(self, request):
        helper.unbind(self.get_object())
        return Response({'info': 'success'})

    @decorators.action(['get'], detail=False)
    def stat(self, request):
        return do_rest_stat_action(self, stats.stats_student)

    @decorators.action(['POST'], detail=False)
    def register_informal(self, request):
        helper.create_informal_student(request.user)
        return Response({'detail': 'success'}, status=status.HTTP_201_CREATED)
