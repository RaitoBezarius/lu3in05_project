from bataille import Bataille
import argparse

def main():
    parser = argparse.ArgumentParser()

    # some arguments

    bataille = Bataille()
    strategie = charge_strategie(args.strategie)

    while not bataille.victoire:
        cible = strategie.agir(bataille)
        strategie.analyser(bataille, cible, bataille.tirer(cible))

    print(bataille.score)

if __name__ == '__main__':
    main()
