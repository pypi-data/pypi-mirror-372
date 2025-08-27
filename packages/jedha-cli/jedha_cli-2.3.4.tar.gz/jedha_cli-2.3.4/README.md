# Jedha CLI

Practice your Cybersecurity skills with Jedha CLI.

You can launch our labs directly from your terminal.

## Requirements

- Python 3.10+
- Docker
- Docker Compose
- AMD64 CPU (preferably, otherwise some labs may not work)

**This CLI is build to be used on [Kali Linux](https://www.kali.org/) priorly** and AMD64 architecture.

It may work on other Linux distributions, but we don't support them. Also it may work on Windows and MacOS but we don't support them either.

## Installation

Be sure you meet all the requirements before installing the CLI. Then use [`pipx`](https://github.com/pypa/pipx):

```bash
pipx install jedha-cli
pipx ensurepath
```

You are good to go!

## Usage

Check the help command to see the available commands:

```bash
$ jedha-cli --help                                                            
 Usage: python -m src.main [OPTIONS] COMMAND [ARGS]...                                    
                                                                                          
 A CLI to manage the labs for Cybersecurity Bootcamp at Jedha (https://jedha.co).         
 ⠀⠀⠀⠀⠀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀                                                                      
 ⠀⠀⠀⠀⣠⣧⠷⠆⠀⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀                                                                      
 ⠀⠀⣐⣢⣤⢖⠒⠪⣭⣶⣿⣦⠀⠀⠀⠀⠀⠀⠀                                                                      
 ⠀⢸⣿⣿⣿⣌⠀⢀⣿⠁⢹⣿⡇⠀⠀⠀⠀⠀⠀                                                                      
 ⠀⢸⣿⣿⣿⣿⣿⡿⠿⢖⡪⠅⢂⠀⠀⠀⠀⠀⠀                                                                      
 ⠀⠀⢀⣔⣒⣒⣂⣈⣉⣄⠀⠺⣿⠿⣦⡀⠀⠀⠀                                                                      
 ⠀⡴⠛⣉⣀⡈⠙⠻⣿⣿⣷⣦⣄⠀⠛⠻⠦⠀⠀                                                                      
 ⡸⠁⢾⣿⣿⣁⣤⡀⠹⣿⣿⣿⣿⣿⣷⣶⣶⣤⠀                                                                      
 ⡇⣷⣿⣿⣿⣿⣿⡇⠀⣿⣿⣿⣿⣿⣿⡿⠿⣿⡀                                                                      
 ⡇⢿⣿⣿⣿⣟⠛⠃⠀⣿⣿⣿⡿⠋⠁⣀⣀⡀⠃                                                                      
 ⢻⡌⠀⠿⠿⠿⠃⠀⣼⣿⣿⠟⠀⣠⣄⣿⣿⡣⠀                                                                      
 ⠈⢿⣶⣤⣤⣤⣴⣾⣿⣿⡏⠀⣼⣿⣿⣿⡿⠁⠀                                                                      
 ⠀⠀⠙⢿⣿⣿⣿⣿⣿⣿⠀⠀⣩⣿⡿⠋⠀⠀⠀                                                                      
 ⠀⠀⠀⠀⠈⠙⠛⠿⠿⠿⠇⠀⠉⠁⠀⠀⠀⠀⠀                                                                      
                                                                                          
╭─ Options ──────────────────────────────────────────────────────────────────────────────╮
│ --install-completion          Install completion for the current shell.                │
│ --show-completion             Show completion for the current shell, to copy it or     │
│                               customize the installation.                              │
│ --help                        Show this message and exit.                              │
╰────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ─────────────────────────────────────────────────────────────────────────────╮
│ dl       Download (but not start) one or more lab(s) environment.                      │
│ list     List all the labs available.                                                  │
│ remove   Remove definitively a specific lab environment. Do it to free your disk       │
│          space.                                                                        │
│ restart  Restart a lab.                                                                │
│ start    Start a specific lab environment.                                             │
│ status   Show the running labs. If a lab name is provided, it will show the status of  │
│          that lab.                                                                     │
│ stop     Stop and clean up a specific lab environment.                                 │
╰────────────────────────────────────────────────────────────────────────────────────────╯
                                                                                          
 Made with ❤️ by the Jedha Bootcamp Team
```
