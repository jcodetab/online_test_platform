from django.urls import path, include
from rest_framework import permissions
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.authtoken.views import obtain_auth_token
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from django.views.generic import TemplateView
from .views import GroupViewSet, GroupMembershipViewSet, ChatMessageViewSet
from . import views
from .views import (
    dashboard, save_result, UserCreateAPIView,
    RegisterAPIView, LoginAPIView, UploadFileTestsAPIView,
    universal_callback, create_click_payment_view,  create_payme_payment_view, create_manual_ordinary_test, upload_case_test_view, EncryptAPIView, DecryptAPIView, GetTestDetailsView,
    UserViewSet, TestViewSet, QuestionViewSet,
    OptionViewSet, TestCompletionViewSet, UserTestViewSet,
    ProfileViewSet, ChoiceViewSet, AnswerViewSet, AuthViewSet,
    UserAnswerViewSet, TaskViewSet, ResultListAPIView,
    TopicViewSet, SubjectViewSet, PaymentViewSet,
    GroupViewSet, GroupMembershipViewSet, OlympiadParticipantViewSet,
    evaluate_test, 
    ResumeTestView,  
    CompleteTestView, SubmitAnswerView, FinishTestView, ClosedTestViewSet, CaseTestViewSet, ClosedTestSessionViewSet,  OlympiadGroupListCreateView, ChangePasswordViewSet, CheckTestAPIView, UnifiedTestListAPIView,
    OlympiadParticipantViewSet,
    JoinOlympiadGroupView,
    RestoreTestView, TestQueueListView, KazusTestCreateAPIView, OlympiadGroupRetrieveView, MyTestsListAPIView, CaseTestsListAPIView, ClosedTestsListAPIView, DashboardStatsAPIView,
    test_create_page, payment_page, api_change_password, 
    olympiad_page, group_page,  current_user,finish_olympiad, group_participants_view,  profile_page, logout_view, get_test_json
)



schema_view = get_schema_view(
    openapi.Info(
        title="Django API Documentation",
        default_version='v1',
        description="Bu API Django loyihasi uchun hujjatlar",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'tests', TestViewSet, basename='tests')
router.register(r'questions', QuestionViewSet, basename='questions')
router.register(r'subjects', SubjectViewSet, basename='subjects')
router.register(r'topics', TopicViewSet, basename='topics')
router.register(r'options', OptionViewSet, basename='options')
router.register(r'payments', PaymentViewSet, basename='payments')
router.register(r'test-completions', TestCompletionViewSet, basename='test-completions')
router.register(r'user-tests', UserTestViewSet, basename='user-tests')
router.register(r'profile', ProfileViewSet, basename='profile')
router.register(r'change-password', ChangePasswordViewSet, basename='change-password')
router.register(r'choices', ChoiceViewSet, basename='choices')
router.register(r'answers', AnswerViewSet, basename='answers')
router.register(r'user-answers', UserAnswerViewSet, basename='user-answers')
router.register(r'tasks', TaskViewSet, basename='tasks')
router.register(r'memberships', GroupMembershipViewSet, basename='memberships')
router.register(r'participants', OlympiadParticipantViewSet, basename='participants')
router.register(r'closed-tests', ClosedTestViewSet, basename='closed-tests')
router.register(r'case-tests', CaseTestViewSet, basename='case-test')
router.register(r'closed-test-sessions', ClosedTestSessionViewSet, basename='closed-test-sessions')
router.register(r'groups', GroupViewSet, basename='group')
router.register('auth', AuthViewSet, basename='auth')



groups_router = NestedDefaultRouter(router, r'groups', lookup='group')
groups_router.register(r'messages', ChatMessageViewSet, basename='group-messages')
groups_router.register(r'participants', OlympiadParticipantViewSet, basename='group-participants')


urlpatterns = [

    path('api/start-test/', views.start_test, name='api_start_test'),
    path('api/save-answer/', views.api_save_answer, name='api_save_answer'),
    path('api/test/finish/', FinishTestView.as_view(), name='finish-test'),


    path('api/dashboard/stats/', DashboardStatsAPIView.as_view(), name='dashboard-stats'),



    path('api/evaluate-test/', evaluate_test, name='evaluate_test'),
    path('api/all-tests/', UnifiedTestListAPIView.as_view(), name='all_tests'),


    path('search-library/', views.search_tests_page, name='search_tests_page'),
    path('', views.home, name='home'),
    path('dashboard/', dashboard, name='dashboard'),
    path('api/get-questions/<int:test_id>/', views.api_get_questions, name='api_get_questions'),
    path('api/check-test/', views.api_check_test, name='api_check_test'),



    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('courses/', views.courses, name='courses'),
    path('team/', views.team, name='team'),
    path('testimonial/', views.testimonial, name='testimonial'),
 

    path('register/', views.register_page, name='register'),
    path('api/register/', RegisterAPIView.as_view(), name='api-register'),
    path('login/', views.login_page, name='login'),
    path('api/login/', LoginAPIView.as_view(), name='api-login'),
    path('logout/', logout_view, name='logout'),
    path('api/users/', UserCreateAPIView.as_view(), name='user-create'),

    path('profile/edit/', views.profile_edit_view, name='profile_edit_page'),
    path("profile/", profile_page, name="profile-page"),
    path('api/profile/me/', views.api_me_profile, name='api_me_profile'),
    path('change-password/', views.change_password_page, name='change-password'),
    path('api/change-password/', api_change_password, name='api_change-password'),



    
    path('api-token-auth/', obtain_auth_token),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    
    path('tests/', views.tests_view, name='tests'),
    path('tests/<int:test_id>/', views.test_detail_view, name='test_detail'),
    path('tests/create/', test_create_page, name='test-create'),
    path('test/start/<int:test_id>/', views.test_start, name='test_start'),
    path('api/results/', ResultListAPIView.as_view(), name='results-list'),
    path('kazus-tests/', views.kazus_tests_view, name='kazus_tests'),
    path('api/kazus-tests/', KazusTestCreateAPIView.as_view(), name='kazus-tests'),
    path('kazus-tests/upload-file-tests/', UploadFileTestsAPIView.as_view(), name='upload-file-tests'),
    path('ranking/', views.ranking_view, name='ranking'),
    path('closed_tests/', views.closed_tests_view, name='closed_tests'),
    path('api/closed-tests/<int:test_id>/start/', views.start_closed_test, name='start_closed_test'),
    path('api/closed-tests/<int:test_id>/submit/', views.submit_closed_test, name='submit_closed_test'),
    path('my-closed-tests/', views.my_closed_tests_page, name='my_closed_tests'),

    
    path('api/save-closed-answer/', views.api_save_closed_answer, name='save_closed_answer'),
    path('closed-tests/', views.get_closed_tests, name='get_closed_tests'),
    path('test/<int:test_id>/', views.take_test, name='take_test'),

    
    path('api/queue/', TestQueueListView.as_view(), name='queue-list'),
    path('resume-test/<int:session_id>/', ResumeTestView.as_view()),
    path('complete-test/<int:session_id>/', CompleteTestView.as_view()),
    path('api/test/submit-answer/', SubmitAnswerView.as_view(), name='submit-answer'),
    path('api/test/<int:test_id>/restore/', RestoreTestView.as_view(), name='restore-test'),

    
   
    path('save-result/', save_result, name='save-result'),

   
    path('api/create-click-payment/', create_click_payment_view, name='create_click_payment'),
    path('click/prepare/', views.click_prepare, name='click_prepare'),
    path('click/complete/', views.click_complete, name='click_complete'),
    path('api/create-payme-payment/', create_payme_payment_view, name='create_payme_payment'),
    path("api/payment/callback/", universal_callback, name="universal-callback"),

    
    path('test/<int:test_id>/payment/', payment_page, name='payment_page'),
    

    path('api/encrypt/', EncryptAPIView.as_view(), name='encrypt'),
    path('api/decrypt/', DecryptAPIView.as_view(), name='decrypt'),


    path('api/auth/me/', current_user, name='current-user'),
    path('group/', group_page, name='group-page'),
    path('groups/join/<uuid:token>/', GroupViewSet.as_view({'post': 'join_by_token'}), name='group-join-by-token'),
       path(
        'groups/<int:group_pk>/messages/',
        ChatMessageViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='group-messages'
    ),
    
    path("api/olympiads/groups/", OlympiadGroupListCreateView.as_view(), name="groups"),
    path("api/olympiads/groups/<int:group_id>/join/", JoinOlympiadGroupView.as_view(), name="join-group"),
    path("api/olympiads/groups/<int:pk>/", OlympiadGroupRetrieveView.as_view(), name="group-detail"),
    path("api/olympiads/groups/<int:group_id>/participants/", group_participants_view, name="group-participants"),


    path('api/olympiads/questions/', views.add_olympiad_question, name='add_olympiad_question'),
    path("api/olympiads/<int:group_id>/start/", views.start_olympiad, name="start-olympiad"),
    path("api/olympiads/<int:group_id>/leaderboard/", views.leaderboard_view, name="leaderboard"),
    path("api/olympiads/<int:group_id>/submit/", views.olympiad_submit_answer, name="olympiad-submit-answer"),
    path("api/olympiads/<int:group_id>/finish/", finish_olympiad, name="finish-olympiad"),

    path("olympiad/", olympiad_page, name="olympiad-page"),


    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),



    path('api/my-tests/', views.MyTestsAPIView.as_view(), name='my_tests_api'),
    path('my-tests/', TemplateView.as_view(template_name='test/my_tests.html'), name='my_tests_page'),

    path('api/test-list/', views.api_test_list, name='api_test_list'),
    path('api/case-test/<int:test_id>/start/', views.start_case_test, name='start_case_test'),

    path('api/create_manual_closed_test/', views.create_manual_closed_test, name='api_create_manual_closed_test'),
    
    path('api/closed-tests/<int:pk>/', ClosedTestViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'}), name='closed-test-detail'),
    path('api/create-closed-test/', views.upload_closed_test, name='create-closed-test'),
 
    path('api/questions/<int:test_id>/', views.api_get_questions, name='api_get_questions'),
    path('api/closed-questions/<int:test_id>/', views.api_get_questions, name='api_get_closed_questions'),



    path('api/my-tests/', MyTestsListAPIView.as_view(), name='my-tests'),
    path('api/case-tests/', CaseTestsListAPIView.as_view(), name='case-tests'),
    path('api/closed-tests/', ClosedTestsListAPIView.as_view(), name='closed-tests'),



    path('api/my-tests/<int:test_id>/', views.api_get_questions, name='get_test_questions'),
    path('api/closed-tests/<int:pk>/json/', views.get_test_json, name='closed-test-detail'),
    path('api/my-tests/<int:test_id>/json/', views.download_my_test_json, name='my-test-detail'),
    path('api/case-tests/<int:test_id>/json/', views.download_my_test_json, name='case-test-detail'),

    path('api/get-test-details/', GetTestDetailsView.as_view(), name='get_test_details'),

    path('create_manual_ordinary_test/', create_manual_ordinary_test, name='create-manual-test'),

    path('api/upload-case-test/', views.ManualTestAPIView.as_view(), name='upload_case_test_api'),
    path('api/upload-test-file/', views.upload_test_file, name='upload-test-file'),
    path('api/upload-case-test/', views.upload_case_test_view, name='upload_case_test'),


    path('api/get-test-json/<int:pk>/', get_test_json, name='get_test_json'),

    
    path('api/upload-file-tests/', views.UploadFileTestsAPIView.as_view(), name='upload-file-tests'),
    path('api/manual-tests/', views.ManualTestAPIView.as_view(), name='manual-tests'),
    path('api/check-test/<int:pk>/', CheckTestAPIView.as_view(), name='check-test'),


    path('api/get-tests/', views.api_get_tests, name='api_get_tests'),


    path('api/', include(router.urls)), 
    path('api/', include(groups_router.urls)),


]








