import inquirer
from inquirer import themes
from clarity_cli.exceptions import StopCommand
from clarity_cli.outputs import CliOutput

out = CliOutput()


class CliInputs():
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(CliInputs, cls).__new__(cls)
            cls._instance.yes_to_all = False  # Default value
        return cls._instance

    def setup_context(self, ctx):
        self.yes_to_all = ctx.obj.get('yes_to_all', False)

    def ask_for_confirmation(self, confirmation_message, default=True, hard_stop=False):
        if not self.yes_to_all:
            questions = [
                inquirer.Confirm('confirm', message=f"{confirmation_message}", default=default)]

            answers = inquirer.prompt(questions, theme=themes.GreenPassion())
            if not answers:
                out.vprint("Command was canceled")
                raise StopCommand()
            if hard_stop and not answers['confirm']:
                out.vprint("Command was not confirmed")
                raise StopCommand()
            return answers['confirm']
        return True

    def ask_for_input_from_list(self, message, options: list):
        if not self.yes_to_all:
            questions = [inquirer.List('list_input', message=message, choices=options)]
            answers = inquirer.prompt(questions, theme=themes.GreenPassion())
            if not answers or not answers['list_input']:
                out.warning("Command was canceled")
                raise StopCommand()
            return answers.get('list_input')
        else:
            raise StopCommand(f"Yes to all is enabled, please provide all the mandatory inputs - {message}")

    def ask_for_text_input(self, message, default="", optional=False):
        if not self.yes_to_all:
            final_message = f"{message} [Optional]" if optional else message
            questions = [inquirer.Text('text_input', message=final_message, default=default)]
            answers = inquirer.prompt(questions, theme=themes.Default())
            if not optional:
                if not answers or (optional and not answers['text_input']):
                    out.warning("Command was canceled")
                    raise StopCommand()
            else:
                answers = answers if answers else default
            return answers.get('text_input')
        else:
            if default or optional:
                return default
            raise StopCommand(f"Yes to all is enabled, please provide all the mandatory inputs - {message}")

    def ask_for_password_input(self, message):
        if not self.yes_to_all:
            questions = [inquirer.Password('pass_input', message=message)]
            answers = inquirer.prompt(questions, theme=themes.Default())
            if not answers or not answers['pass_input']:
                out.warning("Command was canceled")
                raise StopCommand()
            return answers.get('pass_input')
        else:
            raise StopCommand(f"Yes to all is enabled, please provide all the mandatory inputs - {message}")
