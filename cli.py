"""CLI interface."""

import logging
import asyncio
from pyroostermoney import RoosterMoney

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
            if len(cmd) < 4:
                print("Not enough parameters, 4 required, got ", len(cmd))
            else:
                raw_children = input("Enter child user IDs separated by a comma: ").split(",")
                children = []
                for c in raw_children:
                    children.append(session.get_child_account(int(c)))
                await session.create_master_job(children, cmd[1], cmd[2], cmd[3], float(cmd[4]))
        elif cmd[0] == "exit":
            break


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
