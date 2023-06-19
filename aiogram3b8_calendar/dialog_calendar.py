import calendar
from datetime import datetime

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder


# setting callback_data prefix and parts
class CalendarCallback(CallbackData, prefix='dialog_calendar'):
    act: str
    year: int
    month: int
    day: int

ignore_callback = CalendarCallback(act="IGNORE", year=-1, month=-1, day=-1).pack()  # for buttons with no answer


class DialogCalendar:
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    def __init__(self, year: int = datetime.now().year, month: int = datetime.now().month):
        self.year = year
        self.month = month

    async def start_calendar(
        self,
        year: int = datetime.now().year
    ) -> InlineKeyboardMarkup:
        inline_kb = InlineKeyboardBuilder()
        
        # first row - years
        years = []
        for value in range(year - 2, year + 3):
            years.append(InlineKeyboardButton(
                text=value,
                callback_data=CalendarCallback(act="SET-YEAR", year=value, month=-1, day=-1).pack()
            ))
        inline_kb.row(*years, width=5)
        # nav buttons
        inline_kb.row(
            InlineKeyboardButton(
                text='<<',
                callback_data=CalendarCallback(act="PREV-YEARS", year=year, month=-1, day=-1).pack()
            ),
            InlineKeyboardButton(
                text='>>',
                callback_data=CalendarCallback(act="NEXT-YEARS", year=year, month=-1, day=-1).pack()
            ),
            width=2
        )

        return inline_kb.as_markup()

    async def _get_month_kb(self, year: int):
        inline_kb = InlineKeyboardBuilder()
        
        # first row with year button
        inline_kb.row(
            InlineKeyboardButton(text=" ", callback_data=ignore_callback),
            InlineKeyboardButton(
                text=year,
                callback_data=CalendarCallback(act="START", year=year, month=-1, day=-1).pack()
            ),
            InlineKeyboardButton(text=" ", callback_data=ignore_callback)
        )
        # two rows with 6 months buttons
        months_1 = []
        for month in self.months[0:6]:
            months_1.append(InlineKeyboardButton(
                text=month,
                callback_data=CalendarCallback(act="SET-MONTH", year=year, month=self.months.index(month)+1, day=-1).pack()
            ))
        inline_kb.row(*months_1, width=6)
        months_2 = []
        for month in self.months[6:12]:
            months_2.append(InlineKeyboardButton(
                text=month,
                callback_data=CalendarCallback(act="SET-MONTH", year=year, month=self.months.index(month)+1, day=-1).pack()
            ))
        inline_kb.row(*months_2, width=6)
        return inline_kb.as_markup()

    async def _get_days_kb(self, year: int, month: int):
        inline_kb = InlineKeyboardBuilder()
        
        inline_kb.row(
            InlineKeyboardButton(
                text=year,
                callback_data=CalendarCallback(act="START", year=year, month=-1, day=-1).pack()
            ),
            InlineKeyboardButton(
                text=self.months[month - 1],
                callback_data=CalendarCallback(act="SET-YEAR", year=year, month=-1, day=-1).pack()
            ),
        )
        days = []
        for day in ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]:
            days.append(InlineKeyboardButton(text=day, callback_data=ignore_callback))
        inline_kb.row(*days, width=7)
        month_calendar = calendar.monthcalendar(year, month)
        for week in month_calendar:
            days = []
            for day in week:
                if (day == 0):
                    days.append(InlineKeyboardButton(text=" ", callback_data=ignore_callback))
                    continue
                days.append(InlineKeyboardButton(
                    text=str(day), callback_data=CalendarCallback(act="SET-DAY", year=year, month=month, day=day).pack()
                ))
            inline_kb.row(*days, width=7)
        return inline_kb.as_markup()

    async def process_selection(self, query: CallbackQuery, data: CalendarCallback) -> tuple:
        return_data = (False, None)
        if data.act == "IGNORE":
            await query.answer(cache_time=60)
        if data.act == "SET-YEAR":
            await query.message.edit_reply_markup(reply_markup=await self._get_month_kb(int(data.year)))
        if data.act == "PREV-YEARS":
            new_year = int(data.year) - 5
            await query.message.edit_reply_markup(reply_markup=await self.start_calendar(new_year))
        if data.act == "NEXT-YEARS":
            new_year = int(data.year) + 5
            await query.message.edit_reply_markup(reply_markup=await self.start_calendar(new_year))
        if data.act == "START":
            await query.message.edit_reply_markup(reply_markup=await self.start_calendar(int(data.year)))
        if data.act == "SET-MONTH":
            await query.message.edit_reply_markup(reply_markup=await self._get_days_kb(int(data.year), int(data.month)))
        if data.act == "SET-DAY":
            await query.message.delete_reply_markup()   # removing inline keyboard
            return_data = True, datetime(int(data.year), int(data.month), int(data.day))
        return return_data