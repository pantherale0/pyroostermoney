# pylint: disable=broad-exception-caught
# pylint: disable=invalid-name
# pylint: disable=too-many-branches
"""CLI interface."""

import logging
import asyncio
from pyroostermoney import RoosterMoney
from pyroostermoney.child.jobs import JobActions

_LOGGER = logging.getLogger(__name__)

async def main():
    """Main executor."""
    logged_in = False
    session: RoosterMoney = None
    selected_child = None
    while logged_in is not True:
        _LOGGER.debug("Login required")
        username = input("Please enter your username: ")
        password = input("Please enter your password: ")
        card_info = input("Collect card information? [Y/n] ")
        try:
            session = RoosterMoney(username, password, remove_card_information=card_info=="n")
            await session.async_login()
            print("Logged in as ", username)
            logged_in = True
        except PermissionError:
            print("Username or password incorrect")

    while logged_in:
        try:
            cmd = input("Enter a command: ").split()
            if cmd[0] == "show_children":
                for child in session.children:
                    print(f"Child {child.first_name}, ID {child.user_id}")
            elif cmd[0] == "select_child":
                if len(cmd) > 0:
                    selected_child = session.get_child_account(int(cmd[1]))
            elif cmd[0] == "print_child":
                print(selected_child.__dict__)
            elif cmd[0] == "create_master_job":
                raw_children = input("Enter child user IDs separated by a comma: ").split(",")
                children = []
                for c in raw_children:
                    children.append(session.get_child_account(int(c)))
                anytime = input("Job can be completed anytime? [Y/n] ") == "Y"
                await session.master_jobs.create_master_job(children,
                                                description=input("Enter job description: "),
                                                title=input("Enter job title: "),
                                                reward_amount=float(input("Enter job amount: ")),
                                                anytime=anytime)
            elif cmd[0] == "print_child_jobs":
                for job in selected_child.jobs:
                    print(f"Title {job.title}, State {job.state}, ID {job.scheduled_job_id}")
            elif cmd[0] == "approve_job":
                job_id = int(cmd[1])
                for job in selected_child.jobs:
                    if job.scheduled_job_id == job_id:
                        await job.job_action(JobActions.APPROVE)
                        break
            elif cmd[0] == "exit":
                break
        except Exception as exc:
            _LOGGER.error(exc)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
