import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async


class ChallengeConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time challenge battles.
    Both players connect to ws/challenge/<challenge_id>/
    and exchange question answers in real time.
    """

    async def connect(self):
        self.challenge_id = self.scope['url_route']['kwargs']['challenge_id']
        self.room_group = f'challenge_{self.challenge_id}'
        self.user = self.scope['user']

        if not self.user.is_authenticated:
            await self.close()
            return

        # Verify user belongs to this challenge
        valid = await self._is_participant()
        if not valid:
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group, self.channel_name)
        await self.accept()

        # Announce player joined
        await self.channel_layer.group_send(self.room_group, {
            'type': 'player_joined',
            'username': self.user.username,
        })

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        event_type = data.get('type')

        if event_type == 'answer_submitted':
            await self.channel_layer.group_send(self.room_group, {
                'type': 'answer_update',
                'username': self.user.username,
                'question_id': data.get('question_id'),
                'is_correct': data.get('is_correct'),
                'score': data.get('score'),
            })

        elif event_type == 'challenge_complete':
            await self.channel_layer.group_send(self.room_group, {
                'type': 'player_finished',
                'username': self.user.username,
                'final_score': data.get('final_score'),
                'correct': data.get('correct'),
            })

    # ─── Group message handlers ───────────────────────────────

    async def player_joined(self, event):
        await self.send(text_data=json.dumps({
            'type': 'player_joined',
            'username': event['username'],
        }))

    async def answer_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'answer_update',
            'username': event['username'],
            'question_id': event['question_id'],
            'is_correct': event['is_correct'],
            'score': event['score'],
        }))

    async def player_finished(self, event):
        await self.send(text_data=json.dumps({
            'type': 'player_finished',
            'username': event['username'],
            'final_score': event['final_score'],
            'correct': event['correct'],
        }))

    # ─── DB helpers ───────────────────────────────────────────

    @database_sync_to_async
    def _is_participant(self):
        from .models import LiveChallenge
        try:
            c = LiveChallenge.objects.get(id=self.challenge_id)
            return self.user in [c.challenger, c.challenged]
        except LiveChallenge.DoesNotExist:
            return False
