import time
import datetime
import difflib
import os
import re
import matplotlib.pyplot as plt

this_path = os.path.dirname(__file__)
PYTIST = "PYTIST: "

test_strings = [
    'abcdefghijklmnopqrstuvwxyz',
    'abc def ghi jkl mno pqrs tuv wxyz',
    'The quick brown fox jumped over the lazy dogs.',
    "Pack my box with five dozen liquor jugs.",
    "How quickly daft jumping zebras vex.",
    "Crazy Frederick bought many very exquisite opal jewels.",
    "Mary had a little lamb, it's fleece was white as snow.",
    "Every action has an equal and opposite reaction.",
    "import matplotlib.pyplot as plt",
    "for idx, item in enumerate(collection):",
]

def main_screen():
    print(
        "I am Pytist, a game made in Python."
        "I will help you improve your typing speed and accuracy.\n\n"
        "Menu\n----\n\n"
        "1. Create player profile.\n"
        "2. Login Player.\n"
        "3. Begin game level 1.\n"
        "4. Show results.\n"
        "5. Game mode 2.\n"
        "6. Show tips for improvement.\n"
        "7. Exit.\n")
    choice = int(input("Enter your choice: "))
    print()
    return choice

def show_tips():
    print(
        f"{PYTIST}Here are some tips for improvement:\n\n"
        "- Use two or three primary fingers from both hands for letters.\n"
        "- Use either thumb for SPACEBAR.\n"
        "- Use right hand ring finger for ENTER.\n"
        "- Use right middle finger for BACKSPACE.\n"
        "- Use either pinky or ring finger for SHIFT.\n"
        "- Use left ring finger for TAB.\n"
        "- Use left hand pinky and thumb for CTRL and ALT respectively.\n"
        "- Find good position to anchor wrists just below keyboard to reach all keys.\n"
        "- These are not hard and fast rules. Discover your own rules.\n\n"
    )
    input("Press ENTER to continue.")

class Player:
    """Handle data input output for a player."""
    def __init__(self, name=None):
        self.player = name

    def __str__(self):
        return self.player

    @classmethod
    def create_player(cls, playername):
        """Create new player and data file."""
        f = open(os.path.join(this_path, playername + '.tpl'), 'w')
        f.close()
        return cls(playername)

    def write_data(self, idx, string, inp_str, time_taken):
        """Write data for each trial into file."""
        with open(os.path.join(this_path, self.player + '.tpl'), 'a') as f:
            f.write(f"{idx}<>{string}<>{inp_str}<>{time_taken}<>{datetime.datetime.today()}\n")

    def get_data(self):
        """Get all collected data for a player."""
        data = []
        with open(os.path.join(this_path, self.player + '.tpl'), 'r') as f:
            for line in f:
                row = line.strip('\n').split('<>')
                row[0] = int(row[0])
                row[3] = float(row[3])
                row[4] = datetime.datetime.strptime(row[4], '%Y-%m-%d %H:%M:%S.%f')
                data.append(row)
        return data

    @staticmethod
    def available_players():
        """Get list of available players."""
        return [pl_file.strip('.tpl') for pl_file in os.listdir(this_path) if '.tpl' in pl_file]

    @staticmethod
    def exists(playername):
        """Check if a player name exists."""
        return os.path.exists(os.path.join(this_path, playername + '.tpl'))

    def analyse_and_plot(self):
        """Generate performance graphs for a player."""
        data = self.get_data()
        if not data:
            print(f"{PYTIST}There's no data to analyse. Please play the game to get performance data.")
            return None

        player_perf = {
            'day': [],
            'chars_per_sec': [],
            'words_per_min': [],
            'miss_ratio': [],
            'accuracy': [],
        }
        for idx in range(0, len(data), 10):
            day = data[idx][4].timestamp() / (60 * 60 * 24)
            player_perf['day'].append(day)
            group = data[idx:idx + 10]
            total_chars = [len(row[1]) for row in group if row[1] == row[2]]
            total_words = [sum(map(bool,
                                   re.split('; |, |\(|\.| ', row[1])))
                           for row in group if row[1] == row[2] and row[0] != 0]

            times = [row[3] for row in group if row[1] == row[2]]
            misses = sum([1 for row in group if row[1] != row[2]])
            player_perf['chars_per_sec'].append(sum(total_chars) / sum(times) if times else 0)
            player_perf['words_per_min'].append(sum(total_words) / sum(times) * 60 if times else 0)
            player_perf['miss_ratio'].append(misses / 10)
            accuracy = [difflib.SequenceMatcher(None, row[1], row[2]).ratio() for row in group if row[1] != row[2]]
            player_perf['accuracy'].append(sum(accuracy) / misses if misses != 0 else 1)

        plt.style.use('bmh')
        plt.suptitle(f"Performance report for {self.player}")
        plt.subplot(131)
        plt.plot_date(player_perf['day'], player_perf['chars_per_sec'], '-o')
        plt.xlabel('Date time')
        plt.ylabel('Characters per sec')
        plt.xticks(rotation=45)
        plt.subplot(132)
        plt.plot_date(player_perf['day'], player_perf['words_per_min'], '-o')
        plt.xticks(rotation=45)
        plt.xlabel('Date time')
        plt.ylabel('Word per min')
        plt.subplot(133)
        plt.plot_date(player_perf['day'], player_perf['accuracy'], '-o')
        plt.plot_date(player_perf['day'], player_perf['miss_ratio'], '-o')
        plt.xticks(rotation=45)
        plt.xlabel('Date time')
        plt.ylabel('Ratio')
        plt.legend(['accuracy', 'miss ratio'])
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.show()

def capture_single_trial(string):
    """Single string input timing and result."""
    print(f"{PYTIST} GO!")
    start = time.time()
    inp_str = input()
    stop = time.time()
    time_taken = stop-start
    score = difflib.SequenceMatcher(None, string, inp_str)
    if score.ratio() == 1:
        print(f"{PYTIST}PERFECTLY DONE!")
        print(f"{PYTIST}You took {time_taken:.2f} s.")
    else:
        print(f"{PYTIST}You'll get it next time :)")
        print(f"Accuracy = {score.ratio()*100:.2f} %")
        print(f'Target string: {string}\nYou entered  : {inp_str}\n')
        print(f'{PYTIST}Here are the corrections:')
        for tag, i1, i2, j1, j2 in score.get_opcodes():
            print('{:7}   a[{}:{}] --> b[{}:{}] {!r:>8} --> {!r}'.format(
                tag, i1, i2, j1, j2, string[i1:i2], inp_str[j1:j2])
                 )
        print()
    return inp_str, time_taken

if __name__ == '__main__':

    current_player = Player()  # Init None player

    while True:  # Main event loop

        if current_player.player:  # if player logged in
            print(f"{PYTIST}Hello {current_player}. Ready to begin?")

        choice = main_screen()  # display choices menu
        print('-' * 50)

        if choice >= 7:                  # Exit game
            print(f"{PYTIST}Bye! Hope you had fun. See you soon.")
            break

        if choice == 6:
            show_tips()

        elif choice == 1:               # New Player
            newplayername = input("Enter new player name: ")
            if Player.exists(newplayername):
                print(f"\n{PYTIST}Player name already exists. Login or create different player.\n")
            else:
                current_player = Player.create_player(newplayername)

        elif choice == 2:                # Log in player
            avail_players = Player.available_players()

            if len(avail_players) == 0:
                print(f'\n{PYTIST}Please add new player.')
                continue

            print("Existing players:\n")
            for num, name in enumerate(avail_players):
                print(f"{num+1}. {name}")
            try:
                pl_choice = int(input("\nEnter player number: "))
            except ValueError:  # handle non integer input
                print(f"{PYTIST}Invalid input!")
                continue
            print()

            if pl_choice < 1 or pl_choice > len(avail_players):  # Handle input out of range
                print(f"\n{PYTIST}Bad choice! Try again...\n")
            else:
                current_player = Player(avail_players[pl_choice-1])  # Login success

        elif choice == 3:                  # Game loop
            if not current_player.player:
                print(f"\n{PYTIST}Please log in player to collect data.\n")
                continue

            print(
                f"{PYTIST}Each round has 10 strings that you will have to type.\n"
                f"{PYTIST}I will show you the string, you will have to press ENTER to begin typing.\n"
            )
            for idx, test_str in enumerate(test_strings):  # Main game logic
                print(f"{PYTIST}{len(test_strings)-idx} more to go. The string you have to type is\n\n{test_str}")
                input("Press ENTER key to begin typing.")
                input_str, time_taken = capture_single_trial(test_str)
                current_player.write_data(idx, test_str, input_str, time_taken)

            print(f"{PYTIST}Round over! You can relax. I saved your data.")
            print(f"{PYTIST}You can see you performance over time in the analysis section.\n")

        elif choice == 4:                              # Analyse
            if not current_player.player:
                print(f"{PYTIST}Please log in player to get data.")
                continue
            print(f"\n{PYTIST}You need to increase the blue plots, and reduce the red.\n")
            current_player.analyse_and_plot()

        else:                      # Game mode 2
            print(f"\n{PYTIST}Still working on it. Do you have some ideas?\n")

