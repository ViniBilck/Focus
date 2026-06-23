import cmd
import sys

from focuser.core import FocuserController


class FocuserTerminal(cmd.Cmd):
    intro = (
        "\n=== Focuser Interactive Terminal ===\nType 'help' or '?' to list commands.\n"
    )
    prompt = "focuser> "

    def __init__(self, port):
        super().__init__()
        try:
            self.focuser = FocuserController(port=port)
        except Exception as e:
            print(f"[Error] Failed to connect to port {port}: {e}")
            sys.exit(1)

    def do_goto(self, arg):
        if not arg:
            print("[Error] You must provide a position. Example: goto 1500")
            return
        try:
            target = int(arg)
            self.focuser.go_to(target)
        except ValueError:
            print("[Error] Invalid position. Please enter integers only.")

    def do_stop(self, arg):
        self.focuser.stop()

    def do_status(self, arg):
        self.focuser.status()

    def do_exit(self, arg):
        print("Closing connection and exiting...")
        self.focuser.close()
        return True

    def do_quit(self, arg):
        return self.do_exit(arg)


def main():
    import sys

    port = sys.argv[1] if len(sys.argv) > 1 else "/dev/ttyUSB0"

    try:
        terminal = FocuserTerminal(port)
        terminal.cmdloop()
    except KeyboardInterrupt:
        print("\nExiting abruptly...")
        terminal.focuser.close()


if __name__ == "__main__":
    main()
