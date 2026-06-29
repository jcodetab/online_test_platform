import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.apps import apps
from django.utils import timezone
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model


User = get_user_model()


class OlympiadProgressConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            self.group_id = self.scope["url_route"]["kwargs"]["group_id"]
            self.room_group_name = f"olympiad_{self.group_id}"

            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()
            await self._send_json({"ok": True, "message": f"Olimpiada {self.group_id} ga ulanildi"})
        except Exception as e:
            
            await self._send_json({"ok": False, "error": f"connect_failed: {str(e)}"})
            await self.close()

    async def disconnect(self, close_code):
        try:
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        except Exception:
            pass  

    async def receive(self, text_data):
        
        try:
            data = json.loads(text_data or "{}")
        except Exception:
            await self._send_json({"ok": False, "error": "Notog‘ri JSON format"})
            return

        
        if data.get("type") == "ping":
            await self._send_json({"ok": True, "type": "pong"})
            return

        
        try:
            OlympiadGroup = apps.get_model("amaliyot", "OlympiadGroup")
            OlympiadParticipant = apps.get_model("amaliyot", "OlympiadParticipant")
        except Exception as e:
            await self._send_json({"ok": False, "error": f"Model topilmadi: {str(e)}"})
            return

        
        group = await self._get_group_with_test(OlympiadGroup, self.group_id)
        if not group:
            await self._send_json({"ok": False, "error": f"Group (id={self.group_id}) topilmadi"})
            return

        
        now = timezone.now()
        start_time = getattr(group.test, "start_time", None)
        end_time = getattr(group.test, "end_time", None)
        
        if start_time and now < start_time:
            await self._send_json({"ok": False, "error": "Olimpiada hali boshlanmagan"})
            return
        if end_time and now > end_time:
            await self._send_json({"ok": False, "error": "Olimpiada yakunlangan"})
            return

        
        user_id = data.get("user_id")
        if not user_id:
            await self._send_json({"ok": False, "error": "user_id majburiy"})
            return

        user_exists = await self._user_exists(user_id)
        if not user_exists:
            await self._send_json({"ok": False, "error": f"Foydalanuvchi (id={user_id}) topilmadi"})
            return

        
        correct = int(data.get("correct", 0) or 0)
        wrong = int(data.get("wrong", 0) or 0)
        finished = bool(data.get("finished", False))

        updated = await self._update_participant(
            OlympiadParticipant, user_id, self.group_id, correct, wrong, finished
        )
        if not updated["ok"]:
            await self._send_json(updated)
            return

        
        progress = await self._get_group_progress(OlympiadGroup, OlympiadParticipant, self.group_id)

        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "progress_update",
                "data": {"ok": True, "progress": progress},
            },
        )

    async def progress_update(self, event):
        await self._send_json(event["data"])

    
    async def _send_json(self, payload: dict):
        await self.send(text_data=json.dumps(payload, default=str))

    @sync_to_async
    def _get_group_with_test(self, OlympiadGroup, group_id: int):
        return (
            OlympiadGroup.objects.select_related("test")
            .filter(id=group_id)
            .first()
        )

    @sync_to_async
    def _user_exists(self, user_id: int) -> bool:
        return User.objects.filter(id=user_id).exists()

    @sync_to_async
    def _update_participant(self, OlympiadParticipant, user_id: int, group_id: int, correct: int, wrong: int, finished: bool):
        try:
            obj, created = OlympiadParticipant.objects.get_or_create(
                user_id=user_id,
                group_id=group_id,
                defaults={
                    "correct_answers": correct,
                    "wrong_answers": wrong,
                    "finished": finished,
                    "last_activity": timezone.now(),
                    "score": correct,
                },
            )
            if not created:
                
                OlympiadParticipant.objects.filter(pk=obj.pk).update(
                    correct_answers=correct,
                    wrong_answers=wrong,
                    finished=finished,
                    last_activity=timezone.now(),
                    score=correct,
                )
            return {"ok": True}
        except Exception as e:
            
            return {"ok": False, "error": f"participant_update_failed: {str(e)}"}

    @sync_to_async
    def _get_group_progress(self, OlympiadGroup, OlympiadParticipant, group_id: int):
        group = OlympiadGroup.objects.select_related("test").get(id=group_id)
        total_questions = getattr(group.test, "total_questions", 0)

        participants = (
            OlympiadParticipant.objects.filter(group_id=group_id)
            .select_related("user")
            .all()
        )

        result = []
        for p in participants:
            remaining = (
                total_questions - (p.correct_answers + p.wrong_answers)
                if total_questions else None
            )
            result.append({
                "username": getattr(p.user, "username", None),
                "correct": p.correct_answers,
                "wrong": p.wrong_answers,
                "remaining": remaining if remaining is not None else "Noma’lum",
                "finished": p.finished,
                "score": p.score,
                "last_activity": p.last_activity.strftime("%H:%M:%S") if getattr(p, "last_activity", None) else None,
            })

        finished_users = [r for r in participants if r.finished]
        first_finished = None
        if finished_users:
            finished_users.sort(key=lambda x: x.last_activity or timezone.make_aware(timezone.datetime.min))
            first_finished = getattr(finished_users[0].user, "username", None)

        return {
            "participants": result,
            "first_finished": first_finished,
        }







