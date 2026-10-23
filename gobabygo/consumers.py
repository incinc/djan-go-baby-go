from channels.generic.websocket import AsyncJsonWebsocketConsumer


class EchoConsumer(AsyncJsonWebsocketConsumer):
    """
    Echo/broadcast demo consumer.

    Every message received is fanned out to all connected clients through the
    Redis channel layer (open the landing page in two tabs to see it work).
    The channel layer is also reachable from anywhere else in the app — e.g. a
    Celery task can push to the "broadcast" group with:

        from asgiref.sync import async_to_sync
        from channels.layers import get_channel_layer

        async_to_sync(get_channel_layer().group_send)(
            "broadcast", {"type": "broadcast.message", "message": {"text": "hi"}}
        )
    """

    group = "broadcast"

    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add(self.group, self.channel_name)
        # AuthMiddlewareStack (see app/asgi.py) resolves the Django session
        # cookie, so authenticated users are identified here automatically.
        await self.send_json({"text": f"connected as {self.scope['user']}"})

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group, self.channel_name)

    async def receive_json(self, content):
        await self.channel_layer.group_send(
            self.group, {"type": "broadcast.message", "message": content}
        )

    async def broadcast_message(self, event):
        await self.send_json(event["message"])
