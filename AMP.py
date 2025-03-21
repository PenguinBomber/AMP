import ui
import config

if __name__ == '__main__':
    print("Loading Config...")
    config = config.loadConfig()
    print("Starting Application...")
    ui.Application.main()
