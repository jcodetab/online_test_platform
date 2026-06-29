from celery import shared_task
from django.utils import timezone
from .models import TestSession
from .utils import evaluate_test



@shared_task
def auto_evaluate_expired_tests():
    """
    Muddati o'tgan test sessionlarini avtomatik baholaydi.
    """
    now = timezone.now()

    
    expired_sessions = TestSession.objects.filter(
        is_finished=False,
        queue__expected_end_time__lt=now
    )

    evaluated_count = 0

    for session in expired_sessions:
        try:
            evaluate_test(session)
            evaluated_count += 1
        except Exception as e:
            
            print(f"Session {session.id} baholashda xatolik: {e}")

    return f"{evaluated_count} ta test avtomatik baholandi."
