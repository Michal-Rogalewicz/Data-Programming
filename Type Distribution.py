import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv('pokemon_data.csv')

print(df.to_string())

def show_type_distribution():
    type_counts = df["Type 1"].value_counts()

    plt.figure()
    type_counts.plot(kind='bar')
    plt.title('Distribution of Pokemon Primary Types')
    plt.xlabel('Type')
    plt.ylabel('Number of Pokemon')
    plt.tight_layout()
    plt.show()

while True:
    print("\n--- Pokedex Menu ---")
    print("1. View Pokémon type distribution")
    print("2. Search for a Pokemon")
    print("2. Exit")

    choice = input("Enter your choice (1 or 2 or 3): ")

    if choice == '1':
        show_type_distribution()
    elif choice == '2':
        search_pokemon()
    elif choice == '3':
        print("\nExiting Pokedex Menu")
        break
    else:
        print("\nInvalid choice. Please try again.")