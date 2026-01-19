import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv('pokemon_data.csv')

print(df.to_string())


def search_pokemon():
    name = input("Enter Pokemon name: ").strip().lower()

    result = df[df["Name"].str.lower() == name]

    if result.empty:
        print("\nNo Pokemon with that name found.")
        return

    pokemon = result.iloc[0]

    print("\nPokémon Details")
    print("----------------")
    print(f"Name: {pokemon['Name']}")
    print(f"Type 1: {pokemon['Type 1']}")
    print(f"Type 2: {pokemon['Type 2']}")
    print(f"Generation: {pokemon['Generation']}")
    print(f"HP: {pokemon['HP']}")
    print(f"Attack: {pokemon['Attack']}")
    print(f"Defense: {pokemon['Defense']}")

    types = []
    if pd.notna(pokemon['Type 1']):
        types.append(pokemon['Type 1'])
    if pd.notna(pokemon['Type 2']):
        types.append(pokemon['Type 2'])

    sizes = [100 / len(types)] * len(types)

    plt.figure()
    plt.pie(sizes, labels=types, autopct='%1.0f%%')
    plt.title(f"Type Distribution for {pokemon['Name']}")
    plt.show()