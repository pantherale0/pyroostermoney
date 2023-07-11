"""Session manager."""
from .requests import RequestsHandler
import datetime

class SessionManager():
    def __init__(self, loginManager) -> None:
        r = loginManager.login()
        self.session = loginManager.session
        self.requests: RequestsHandler = RequestsHandler(loginManager.session)

        self.familyId = r.familyId
        self.children = r.children

    def _update(self) -> None:
        d = self.requests.account_info()
        self.children = d.children
        self.familyId = d.familyId

    def get_child(self, userId: int) -> object:
        self._update()
        x = [p for p in self.children if p.userId == userId]
        if len(x) != 1:
            raise LookupError(f"{userId} not found.")
        return x[0]

    def get_child_active_allowance_period(self, userId: int):
        d = self.requests.get_child_allowance_periods(userId)
        x = [p for p in d if datetime.datetime.strptime(p.startDate, "%Y-%m-%d").date() <= datetime.date.today() <= datetime.datetime.strptime(p.endDate, "%Y-%m-%d").date()]
        if len(x) != 1:
            raise LookupError("No allowance period found")
        return x[0]
    