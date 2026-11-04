from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework.test import APIClient

from instruments.models import (
    InstrumentCategory,
    Instrument,
    InstrumentRequest,
    InstrumentRequestEvent,
)


class TransactionRollbackTest(TestCase):
    def test_approve_rollback_when_history_creation_fails(self):
        User = get_user_model()

        # Создаём сотрудника и обычного пользователя
        staff = User.objects.create_user(
            username="staff_test",
            password="test12345",
            is_staff=True,
        )

        owner = User.objects.create_user(
            username="owner_test",
            password="test12345",
        )

        # Создаём категорию и инструмент
        category = InstrumentCategory.objects.create(
            name="Тестовая категория"
        )

        instrument = Instrument.objects.create(
            name="Тестовая гитара",
            description="Тестовый инструмент",
            category=category,
            total_quantity=5,
            available_quantity=5,
        )

        # Создаём новую заявку на 2 инструмента
        request = InstrumentRequest.objects.create(
            instrument=instrument,
            owner=owner,
            quantity=2,
            status="new",
        )

        # Сохраняем начальное состояние истории
        InstrumentRequestEvent.objects.create(
            request=request,
            initiator=owner,
            action="created",
            comment="Заявка создана",
        )

        events_before = InstrumentRequestEvent.objects.filter(
            request=request
        ).count()

        # Авторизуемся как сотрудник
        client = APIClient()
        client.force_authenticate(user=staff)
        client.raise_request_exception = False

        # Искусственно вызываем ошибку при записи события в историю
        with patch(
            "instruments.views.InstrumentRequestEvent.objects.create",
            side_effect=Exception("Ошибка записи истории"),
        ):
            response = client.post(
                f"/api/instrument-requests/{request.id}/approve/"
            )

        # Проверяем, что API вернул ошибку
        self.assertEqual(response.status_code, 500)

        # Обновляем данные из базы
        instrument.refresh_from_db()
        request.refresh_from_db()

        # Проверяем, что остаток не уменьшился
        self.assertEqual(instrument.available_quantity, 5)

        # Проверяем, что заявка осталась новой
        self.assertEqual(request.status, "new")

        # Проверяем, что новая запись в истории не появилась
        events_after = InstrumentRequestEvent.objects.filter(
            request=request
        ).count()

        self.assertEqual(events_after, events_before)
