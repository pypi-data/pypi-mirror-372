from typing import Literal, TYPE_CHECKING
from cardlink.types import Item, Bill, Currency, CreatedBill, PaymentMethod
from cardlink.types.BillTypes import BillTypes
from cardlink.methods.base import CardLinkBaseMethod

if TYPE_CHECKING:
    import cardlink


class createBill:
    """bill/create method"""
    class createBillMethod(CardLinkBaseMethod):
        amount: float | int
        shop_id: str | None = None
        order_id: str | None = None
        description: str | None = None
        type: Literal['normal', 'multi'] = 'normal'
        currency_in: Literal['RUB', 'USD', 'EUR'] = 'RUB'
        custom: str | None = None
        payer_pays_commission: bool | None = None
        payer_email: str | None = None
        name: str | None = None
        ttl: int | None = None
        success_url: str | None = None
        fail_url: str | None = None
        payment_method: Literal["BANK_CARD", "SBP"] = "SBP"
        request_fields_email: bool = False
        request_fields_phone: bool = False
        request_fields_name: bool = False
        request_fields_comment: bool = False
        items: list[Item] | None = None

        __api_method__ = "bill/create"
        __return_type__ = CreatedBill
        __request_type__ = "POST"

        def model_dump(self, *args, **kwargs):
            data = super().model_dump(*args, **kwargs)

            data["request_fields"] = {
                "email": data.pop("request_fields_email", None),
                "phone": data.pop("request_fields_phone", None),
                "name": data.pop("request_fields_name", None),
                "comment": data.pop("request_fields_comment", None),
            }

            return data

    async def create_bill(
            self: "cardlink.CardLink",
            amount: float | int,
            order_id: str | None = None,
            description: str | None = None,
            type: BillTypes | str = 'normal',
            currency_in: Currency | str = 'RUB',
            custom: str | None = None,
            payer_pays_commission: bool | None = None,
            payer_email: str | None = None,
            name: str | None = None,
            ttl: int | None = None,
            success_url: str | None = None,
            fail_url: str | None = None,
            payment_method: PaymentMethod | str = "SBP",
            request_fields_email: bool = False,
            request_fields_phone: bool = False,
            request_fields_name: bool = False,
            request_fields_comment: bool = False,
            items: list[Item] | None = None
    ) -> Bill:
        """
        Создать счет на оплату
        Для того чтобы провести оплату необходимо создать счет. Если тип счета многоразовый, то по одному счету можно произвести несколько платежей. Домен в shop_url должен совпадать с доментом success_url и fail_url.

        :param amount: Сумма счета на оплату
        :param order_id: *Optional*. Уникальный идентификатор заказа. Будет возвращен в postback
        :param description: *Optional*. Описание платежа
        :param type: *Optional*. Тип платежа. Одноразовый или многоразовый. Если выбран одноразовый, то второй раз оплатить не получится
        :param currency_in: *Optional*. Валюта, в которой оплачивается счет. Если не передана, то используется валюта магазина. Если shop_id не определен, то используется RUB
        :param custom: *Optional*. Произвольное поле. Будет возвращено в postback
        :param payer_pays_commission: *Optional*. Параметр, который указывает на то, кто будет оплачивать комиссию за входящий платёж
        :param payer_email: *Optional*. Параметр, который заполняет email клиента на платёжной странице
        :param name: *Optional*. Название ссылки. Укажите, за что принимаете средства. Этот текст будет отображен в платежной форме
        :param ttl: *Optional*. Время жизни счета на оплату в секундах
        :param success_url: *Optional*. Страница успешной оплаты
        :param fail_url: *Optional*. Страница неуспешной оплаты
        :param payment_method: *Optional*. Способ оплаты. Если указан этот параметр, то при переходе на платежную форму этот способ оплаты будет выбран автоматически, без возможности выбора другого способ оплаты
        :param request_fields_email: *Optional*. Обязательный запрос электронной почты у плательщика
        :param request_fields_phone: *Optional*. Обязательный запрос номера телефона у плательщика
        :param request_fields_name: *Optional*. Обязательный запрос ФИО у плательщика
        :param request_fields_comment: *Optional*. Обязательный запрос комментария у плательщика
        :param items: *Optional*. Список товаров

        :return: :class:`Bill` object
        """

        params = locals()
        if params['payer_pays_commission']:
            params['payer_pays_commission'] = int(params['payer_pays_commission'])

        params['shop_id'] = self._shop_id

        created_bill: CreatedBill = await self(self.createBillMethod(**params))

        bill: Bill = await self.get_bill_status(id=created_bill.bill_id)
        bill.link_url = created_bill.link_url
        bill.link_page_url = created_bill.link_page_url

        return bill
