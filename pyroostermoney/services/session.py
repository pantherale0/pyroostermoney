"""Session manager."""
import datetime
from pyroostermoney.services.api import RequestsHandler

class SessionManager():
    """Manages the core session."""
    def __init__(self, login_manager) -> None:
        login = login_manager.login()
        self.session = login_manager.session
        self.requests: RequestsHandler = RequestsHandler(login_manager.session)

        self.family_id = login.familyId
        self.children = login.children

    def _update(self) -> None:
        """Requests a full update."""
        account_info = self.requests.account_info()
        self.children = account_info.children
        self.family_id = account_info.familyId

    def get_child(self, user_id: int) -> object:
        """Gets information for a given child."""
        self._update()
        x = [p for p in self.children if p.userId == user_id]
        if len(x) != 1:
            raise LookupError(f"{user_id} not found.")
        return x[0]

    def get_child_active_allowance_period(self, user_id: int):
        """Returns the current active allowance period."""
        d = self.requests.get_child_allowance_periods(user_id)
        x = [p for p in d if datetime.datetime.strptime(p.startDate, "%Y-%m-%d").date() <= datetime.date.today() <= datetime.datetime.strptime(p.endDate, "%Y-%m-%d").date()]
        if len(x) != 1:
            raise LookupError("No allowance period found")
        return x[0]
    